from model_providers.core.bootstrap import Bootstrap


class BootstrapRegister:
    """
    注册管理器
    """

    mapping = {
        "bootstrap": {},
    }

    @classmethod
    def register_bootstrap(cls, name):
        r"""Register system bootstrap to registry with key 'name'

        Args:
            name: Key with which the task will be registered.

        Usage:

            from lavis.common.registry import registry
        """

        print(f"register_bootstrap {name}")

        def wrap(task_cls):
            assert issubclass(
                task_cls, Bootstrap
            ), "All tasks must inherit bootstrap class"
            if name in cls.mapping["bootstrap"]:
                raise KeyError(
                    "Name '{}' already registered for {}.".format(
                        name, cls.mapping["bootstrap"][name]
                    )
                )
            cls.mapping["bootstrap"][name] = task_cls
            return task_cls

        return wrap

    @classmethod
    def get_bootstrap_class(cls, name):
        return cls.mapping["bootstrap"].get(name, None)

    @classmethod
    def list_bootstrap(cls):
        return sorted(cls.mapping["bootstrap"].keys())


bootstrap_register = BootstrapRegister()
