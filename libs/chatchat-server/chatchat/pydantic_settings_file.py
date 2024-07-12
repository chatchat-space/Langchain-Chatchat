from __future__ import annotations

from functools import cached_property
from io import StringIO
import os
from pathlib import Path
import typing as t

from memoization import cached, CachingAlgorithmFlag
from pydantic import BaseModel, Field, ConfigDict, computed_field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, YamlConfigSettingsSource, SettingsConfigDict
import ruamel.yaml
from ruamel.yaml.comments import CommentedBase, TaggedScalar


__all__ = ["YamlTemplate", "MyBaseModel", "BaseFileSettings", "Field",
           "SubModelComment", "SettingsConfigDict",
           "computed_field", "cached_property", "settings_property"]


def import_yaml() -> ruamel.yaml.YAML:
    def text_block_representer(dumper, data):
        style = None
        if len(data.splitlines()) > 1: # check for multilines
            style = "|"
        return dumper.represent_scalar("tag.yaml.org,2002:str", data, style=style)

    yaml = ruamel.yaml.YAML()
    yaml.block_seq_indent = 2
    yaml.map_indent = 2
    yaml.sequence_dash_offset = 2
    yaml.sequence_indent = 4

    # this representer makes all OrderedDict to TaggedScalar
    # yaml.representer.add_representer(str, text_block_representer)
    return yaml


class SubModelComment(t.TypedDict):
    """parameter defines howto create template for sub model"""
    model_obj: BaseModel
    dump_kwds: t.Dict
    is_entire_comment: bool = False # share comment for complex field such as list
    sub_comments: t.Dict[str, "SubModelComment"]


class YamlTemplate:
    """create yaml configuration template for pydantic model object"""
    def __init__(
        self,
        model_obj: BaseModel,
        dump_kwds: t.Dict={},
        sub_comments: t.Dict[str, SubModelComment]={},
    ):
        self.model_obj = model_obj
        self.dump_kwds = dump_kwds
        self.sub_comments = sub_comments

    @cached_property
    def model_cls(self):
        return self.model_obj.__class__

    def _create_yaml_object(
        self,
    ) -> CommentedBase:
        """helper method to convert settings instance to ruamel.YAML object"""
        # # exclude computed fields
        # exclude = set(self.dump_kwds.get("exclude", []))
        # exclude |= set(self.model_cls.model_computed_fields)
        # self.dump_kwds["exclude"] = list(exclude)

        data = self.model_obj.model_dump(**self.dump_kwds)
        yaml = import_yaml()
        buffer = StringIO()
        yaml.dump(data, buffer)
        buffer.seek(0)
        obj = yaml.load(buffer)
        return obj

    def get_class_comment(self, model_cls: t.Type[BaseModel] | BaseModel=None) -> str | None:
        """
        you can override this to customize class comments
        """
        if model_cls is None:
            model_cls = self.model_cls
        return model_cls.model_json_schema().get("description")

    def get_field_comment(self, field_name: str, model_obj: BaseModel=None) -> str | None:
        """
        you can override this to customize field comments
        model_obj is the instance that field_name belongs to
        """
        if model_obj is None:
            schema = self.model_cls.model_json_schema().get("properties", {})
        else:
            fields_schema = model_obj.model_json_schema().get("properties", {})
        if field := fields_schema.get(field_name):
            lines = [field.get("description", "")]
            if enum := field.get("enum"):
                lines.append(f"可选值：{enum}")
            return "\n".join(lines)

    def create_yaml_template(
        self,
        write_to: str | Path | bool = False,
        indent: int = 0,
    ) -> str:
        """
        generate yaml template with default object
        sub_comments indicate how to populate comments for sub models, it could be nested.
        """
        cls = self.model_cls
        obj = self._create_yaml_object()

        # add start comment for class
        cls_comment = self.get_class_comment()
        if cls_comment:
            obj.yaml_set_start_comment(cls_comment + "\n\n", indent)
        
        sub_comments = self.sub_comments
        # add comments for fields
        def _set_subfield_comment(
            o: CommentedBase,
            m: BaseModel,
            n: str,
            sub_comment: SubModelComment,
            indent: int,
        ):
            if sub_comment:
                if sub_comment.get("is_entire_comment"):
                    comment = (YamlTemplate(sub_comment["model_obj"],
                                            dump_kwds=sub_comment.get("dump_kwds", {}),
                                            sub_comments=sub_comment.get("sub_comments", {}),)
                                .create_yaml_template()
                            )
                    if comment:
                        o.yaml_set_comment_before_after_key(n, "\n"+comment, indent=indent)
                elif sub_model_obj := sub_comment.get("model_obj"):
                    comment = self.get_field_comment(n, m) or self.get_class_comment(sub_model_obj)
                    if comment:
                        o.yaml_set_comment_before_after_key(n, "\n"+comment, indent=indent)
                    for f in sub_model_obj.model_fields:
                        s = sub_comment.get("sub_comments", {}).get(f, {})
                        _set_subfield_comment(o[n], sub_model_obj, f, s, indent+2)
            else:
                comment = self.get_field_comment(n, m)
                if comment:
                    o.yaml_set_comment_before_after_key(n, "\n"+comment, indent=indent)

        for n in cls.model_fields:
            _set_subfield_comment(obj, self.model_obj, n, sub_comments.get(n, {}), indent)

        yaml = import_yaml()
        buffer = StringIO()
        yaml.dump(obj, buffer)
        template = buffer.getvalue()

        if write_to is True:
            write_to = self.model_cls.model_config.get("yaml_file")
        if write_to:
            with open(write_to, "w", encoding="utf-8") as fp:
                fp.write(template)

        return template


class MyBaseModel(BaseModel):
    model_config = ConfigDict(
        use_attribute_docstrings=True,
        extra="allow",
        env_file_encoding="utf-8",
    )


class BaseFileSettings(BaseSettings):
    model_config = SettingsConfigDict(
        use_attribute_docstrings=True,
        extra="ignore",
        yaml_file_encoding="utf-8",
        env_file_encoding="utf-8",
    )

    def model_post_init(self, __context: os.Any) -> None:
        self._auto_reload = True
        return super().model_post_init(__context)

    @property
    def auto_reload(self) -> bool:
        return self._auto_reload
    
    @auto_reload.setter
    def auto_reload(self, val: bool):
        self._auto_reload = val

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, env_settings, dotenv_settings, YamlConfigSettingsSource(settings_cls)

    def create_template_file(
        self,
        model_obj: BaseFileSettings=None,
        dump_kwds: t.Dict={},
        sub_comments: t.Dict[str, SubModelComment]={},
        write_file: bool | str | Path = False,
        file_format: t.Literal["yaml", "json"] = "yaml",
    ) -> str:
        if model_obj is None:
            model_obj = self
        if file_format == "yaml":
            template = YamlTemplate(model_obj=model_obj, dump_kwds=dump_kwds, sub_comments=sub_comments)
            return template.create_yaml_template(write_to=write_file)
        else:
            dump_kwds.setdefault("indent", 4)
            data = model_obj.model_dump_json(**dump_kwds)
            if write_file:
                write_file = self.model_config.get("json_file")
                with open(write_file, "w", encoding="utf-8") as fp:
                    fp.write(data)
            return data


def _lazy_load_key(settings: BaseSettings):
    keys = [settings.__class__]
    for n in ["env_file", "json_file", "yaml_file", "toml_file"]:
        key = None
        if file := settings.model_config.get(n):
            if os.path.isfile(file) and os.path.getsize(file) > 0:
                key = int(os.path.getmtime(file))
        keys.append(key)
    return tuple(keys)


_T = t.TypeVar("_T", bound=BaseFileSettings)

@cached(max_size=1, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True, custom_key_maker=_lazy_load_key)
def _cached_settings(settings: _T) -> _T:
    """
    the sesstings is cached, and refreshed when configuration files changed
    """
    if settings.auto_reload:
        settings.__init__()
    return settings


def settings_property(settings: _T):
    def wrapper(self) -> _T:
        return _cached_settings(settings)
    return property(wrapper)
