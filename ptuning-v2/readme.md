如果使用了[p-tuning-v2](https://github.com/THUDM/ChatGLM-6B/tree/main/ptuning)方式微调了模型，可以将得到的PrefixEndoer放入此文件夹。

只需要放入模型的*config.json*和*pytorch_model.bin*

并在加载模型时勾选 *"使用p-tuning-v2微调过的模型"*