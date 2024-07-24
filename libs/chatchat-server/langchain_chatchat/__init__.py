import importlib
import sys
import types

# 动态导入 a_chatchat 模块
chatchat = importlib.import_module("chatchat")

# 创建新的模块对象
module = types.ModuleType("langchain_chatchat")
sys.modules["langchain_chatchat"] = module

# 把 a_chatchat 的所有属性复制到 langchain_chatchat
for attr in dir(chatchat):
    if not attr.startswith("_"):
        setattr(module, attr, getattr(chatchat, attr))


# 动态导入子模块
def import_submodule(name):
    full_name = f"chatchat.{name}"
    submodule = importlib.import_module(full_name)
    sys.modules[f"langchain_chatchat.{name}"] = submodule
    for attr in dir(submodule):
        if not attr.startswith("_"):
            setattr(module, attr, getattr(submodule, attr))


# 需要的子模块列表，自己添加
submodules = ["settings", "server", "startup", "webui_pages"]

# 导入所有子模块
for submodule in submodules:
    import_submodule(submodule)
