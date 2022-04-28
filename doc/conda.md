## 基本环境使用

###创建环境
创建一个名为 my_env_name 的环境，用python 3.7 版本
```
conda create -n my_env_name python3.7
```
### 激活环境
激活 my_env_name 环境
```
conda activate my_env_name
```

## 环境分享
### 导出为 my_env_name.yml 文件
```
conda env export > my_env_name.yml
```
### 使用 yml 导入创建的环境
```
conda env create -n new_env -f my_env_name.yml
```
### 克隆新的环境
```
conda create -n new_env_2 --clone env_name
```

## 包管理
### 列出所有包
```
conda list
```
### 安装包
```
conda install pkg_name
```
### 从指定 channel 下载
```
conda install --channel https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/ pytorch
```
