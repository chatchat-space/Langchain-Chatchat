## Issue with Installing Packages Using pip in Anaconda

## Problem

Recently, when running open-source code, I encountered an issue: after creating a virtual environment with conda and switching to the new environment, using pip to install packages would be "ineffective." Here, "ineffective" means that the packages installed with pip are not in this new environment.

------

## Analysis

1. First, create a test environment called test: `conda create -n test`
2. Activate the test environment: `conda activate test`
3. Use pip to install numpy: `pip install numpy`. You'll find that numpy already exists in the default environment.

```powershell
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Requirement already satisfied: numpy in c:\programdata\anaconda3\lib\site-packages (1.20.3)
```

4. Check the information of pip: `pip show pip`

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

5. We can see that the current pip is in the default conda environment. This explains why the package is not in the new virtual environment when we directly use pip to install packages - because the pip being used belongs to the default environment, the installed package either already exists or is installed directly into the default environment.

------

## Solution

1. We can directly use the conda command to install new packages, but sometimes conda may not have certain packages/libraries, so we still need to use pip to install.
2. We can first use the conda command to install the pip package for the current virtual environment, and then use pip to install new packages.

```powershell
# Use conda to install the pip package
(test) PS C:\Users\Administrator> conda install pip
Collecting package metadata (current_repodata.json): done
Solving environment: done
....
done

# Display the information of the current pip, and find that pip is in the test environment
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

# Now use pip to install the numpy package, and it is installed successfully
(test) PS C:\Users\Administrator> pip install numpy
Looking in indexes: 
https://pypi.tuna.tsinghua.edu.cn/simple
Collecting numpy
  Using cached https://pypi.tuna.tsinghua.edu.cn/packages/4b/23/140ec5a509d992fe39db17200e96c00fd29603c1531ce633ef93dbad5e9e/numpy-1.22.2-cp39-cp39-win_amd64.whl (14.7 MB)
Installing collected packages: numpy
Successfully installed numpy-1.22.2

# Use pip list to view the currently installed packages, no problem
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

## Supplement

1. The reason I didn't notice this problem before might be because the packages installed in the virtual environment were of a specific version, which overwrote the packages in the default environment. The main issue was actually a lack of careful observation:), otherwise, I could have noticed `Successfully uninstalled numpy-xxx` **default version** and `Successfully installed numpy-1.20.3` **specified version**.
2. During testing, I found that if the Python version is specified when creating a new package, there shouldn't be this issue. I guess this is because pip will be installed in the virtual environment, while in our case, including pip, no packages were installed, so the default environment's pip was used.
3. There's a question: I should have specified the Python version when creating a new virtual environment before, but I still used the default environment's pip package. However, I just couldn't reproduce the issue successfully on two different machines, which led to the second point mentioned above.
4. After encountering the problem mentioned in point 3, I solved it by using `python -m pip install package-name`, adding `python -m` before pip. As for why, you can refer to the answer on [StackOverflow](https://stackoverflow.com/questions/41060382/using-pip-to-install-packages-to-anaconda-environment):

>1. If you have a non-conda pip as your default pip but conda python as your default python (as below):
>
>```shell
>>which -a pip
>/home/<user>/.local/bin/pip   
>/home/<user>/.conda/envs/newenv/bin/pip
>/usr/bin/pip
>
>>which -a python
>/home/<user>/.conda/envs/newenv/bin/python
>/usr/bin/python
>```
>
>2. Then, instead of calling `pip install <package>` directly, you can use the module flag -m in python so that it installs with the anaconda python
>
>```shell
>python -m pip install <package>
>```
>
>3. This will install the package to the anaconda library directory rather than the library directory associated with the (non-anaconda) pip
>4. The reason for doing this is as follows: the pip command references a specific pip file/shortcut (which -a pip will tell you which one). Similarly, the python command references a specific python file (which -a python will tell you which one). For one reason or another, these two commands can become out of sync, so your "default" pip is in a different folder than your default python and therefore is associated with different versions of python.
>5. In contrast, the python -m pip construct does not use the shortcut that the pip command points to. Instead, it asks python to find its pip version and use that version to install a package.