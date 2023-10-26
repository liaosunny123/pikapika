# Pikapika

Pikapika 是基于 Python 的单模块运行程序，提供可控图像生成的功能。

# Usage

Pikapika 工作模式为单实例提供单服务模式：

1. 配置运行时环境变量

```bash
git clone --recurse-submodules https://github.com/liaosunny123/pikapika.git 
cp server.yaml.example server.yaml
vim server.yaml 
```

编辑信息后保存并退出

2. 安装运行时环境

```bash
pip3 install -r requirements.txt
```

3. 运行程序

```bash
python3 main.py 
```