## 项目配置项使用说明

项目所有配置项由 `chatchat.settings.Settings` 统一管理，代替原来通过 `chatchat/configs/*.py` 配置的方式。

绝大部分配置项沿用了原来的名字和分组，少数进行了整合。

### 改进后的优点：
- 配置项与 py 代码分离，减少代码升级带来的麻烦，更改配置更方便
- 切换不同的 yaml 文件即可加载不同的配置，方便多环境管理和测试
- 配置项通过 `pydantic` 模型定义，加强了数据验证，简化了环境变量的读取，可以使用 `yaml/json/toml` 不同的文件后端
- 可以自动生成 yaml 文件模板，添加配置说明
- 所有配置项进行了缓存减少文件读取，当 .yaml/.env 文件被修改时可以自动刷新缓存
  
### 使用方式：

```python3
from chatchat.settings import Settings

print(Settings.basic_settings) # 基本配置信息，包括数据目录、服务器配置等
print(Settings.kb_settings) # 知识库相关配置项
print(Settings.model_settings) # 模型相关配置项
print(Settings.tool_settings) # 工具相关配置项
print(Settings.prompt_settings) # prompt 模板

```

** 注意 **：如果使用 `Settings.xx_settings.XX` 这种方式，配置项会自动跟踪配置文件的修改而刷新；如果使用 `s = Settings.xx_settings; s.XX` 这种方式，配置项不会自动刷新。

### 添加或更改配置项：

第一步：直接在 `chatchat/settings.py` 对应的 XXSettings 类中添加字段，建议：
- 每个字段都设定默认值
- 给字段添加必要的说明

第二步：执行 `CHATCHAT_ROOT=/path/to/data chatchat init --gen-config` 更新配置模板
