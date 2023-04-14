##  在 Anaconda 中使用 pip 安装包无效问题

##  问题

最近在跑开源代码的时候遇到的问题：使用 conda 创建虚拟环境并切换到新的虚拟环境后，再使用 pip 来安装包会“无效”。这里的“无效”指的是使用 pip 安装的包不在这个新的环境中。

------

## 分析

1、首先创建一个测试环境 test，`conda create -n test`

2、激活该测试环境，`conda activate test`

3、使用 pip 安装 numpy，`pip install numpy`，会发现 numpy 已经存在默认的环境中

```powershell
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Requirement already satisfied: numpy in c:\programdata\anaconda3\lib\site-packages (1.20.3)
```

4、这时候看一下 pip 的信息，`pip show pip`

```powershell
Name: pip
Version: 21.2.4
Summary: The PyPA recommended tool for installing Python packages.
Home-page: https://pip.pypa.io/
Author: The pip developers
Author-email: distutils-sig@python.org
License: MIT
Location: c:\programdata\anaconda3\lib\site-packages
Requires:
Required-by:
```

5、可以发现当前 pip 是在默认的 conda 环境中。这也就解释了当我们直接使用 pip 安装包时为什么包不在这个新的虚拟环境中，因为使用的 pip 属于默认环境，安装的包要么已经存在，要么直接装到默认环境中去了。

------

## 解决

1、我们可以直接使用 conda 命令安装新的包，但有些时候 conda 可能没有某些包/库，所以还是得用 pip 安装

2、我们可以先使用 conda 命令为当前虚拟环境安装 pip 包，再使用 pip 安装新的包

```powershell
# 使用 conda 安装 pip 包
(test) PS C:\Users\Administrator> conda install pip
Collecting package metadata (current_repodata.json): done
Solving environment: done
....
done

# 显示当前 pip 的信息，发现 pip 在测试环境 test 中
(test) PS C:\Users\Administrator> pip show pip
Name: pip
Version: 21.2.4
Summary: The PyPA recommended tool for installing Python packages.
Home-page: https://pip.pypa.io/
Author: The pip developers
Author-email: distutils-sig@python.org
License: MIT
Location: c:\programdata\anaconda3\envs\test\lib\site-packages
Requires:
Required-by:

# 再使用 pip 安装 numpy 包，成功安装
(test) PS C:\Users\Administrator> pip install numpy
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting numpy
  Using cached https://pypi.tuna.tsinghua.edu.cn/packages/4b/23/140ec5a509d992fe39db17200e96c00fd29603c1531ce633ef93dbad5e9e/numpy-1.22.2-cp39-cp39-win_amd64.whl (14.7 MB)
Installing collected packages: numpy
Successfully installed numpy-1.22.2

# 使用 pip list 查看当前安装的包，没有问题
(test) PS C:\Users\Administrator> pip list
Package      Version
------------ ---------
certifi      2021.10.8
numpy        1.22.2
pip          21.2.4
setuptools   58.0.4
wheel        0.37.1
wincertstore 0.2
```

------

## 补充

1、之前没有发现这个问题可能时因为在虚拟环境中安装的包是指定版本的，覆盖了默认环境中的包。其实主要还是观察不仔细：），不然可以发现 `Successfully uninstalled numpy-xxx`【默认版本】 以及 `Successfully installed numpy-1.20.3`【指定版本】

2、测试时发现如果在新建包的时候指定了 python 版本的话应该是没有这个问题的，猜测时因为会在虚拟环境中安装好 pip ，而我们这里包括 pip 在内啥包也没有装，所以使用的是默认环境的 pip

3、有个问题，之前我在创建新的虚拟环境时应该指定了 python 版本，但还是使用的默认环境的 pip 包，但是刚在在两台机器上都没有复现成功，于是有了上面的第 2 点

4、出现了第 3 点的问题后，我当时是使用 `python -m pip install package-name` 解决的，在 pip 前面加上了 python -m。至于为什么，可以参考 [StackOverflow](https://stackoverflow.com/questions/41060382/using-pip-to-install-packages-to-anaconda-environment) 上的回答：

> 1、如果你有一个非 conda 的 pip 作为你的默认 pip，但是 conda 的 python 是你的默认 python（如下）：
>
> ```shell
> >which -a pip
> /home/<user>/.local/bin/pip   
> /home/<user>/.conda/envs/newenv/bin/pip
> /usr/bin/pip
> 
> >which -a python
> /home/<user>/.conda/envs/newenv/bin/python
> /usr/bin/python
> ```
>
> 2、然后，而不是直接调用 `pip install <package>`，你可以在 python 中使用模块标志 -m，以便它使用 anaconda python 进行安装
>
> ```shell
>python -m pip install <package>
> ```
>
> 3、这将把包安装到 anaconda 库目录，而不是与（非anaconda） pip 关联的库目录
> 
> 4、这样做的原因如下：命令 pip 引用了一个特定的 pip 文件 / 快捷方式（which -a pip 会告诉你是哪一个）。类似地，命令 python 引用一个特定的 python 文件（which -a python 会告诉你是哪个）。由于这样或那样的原因，这两个命令可能变得不同步，因此你的“默认” pip 与你的默认 python 位于不同的文件夹中，因此与不同版本的 python 相关联。
>
> 5、与此相反，python -m pip 构造不使用 pip 命令指向的快捷方式。相反，它要求 python 找到它的pip 版本，并使用该版本安装一个包。

-   
