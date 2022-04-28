## 镜像
### 查看镜像
```
docker image ls
```
### 搜索镜像
```
docker search [image]
```
### 拉取镜像
```
docker image pull [image]
```
### 展示镜像的细节，包括镜像层数据和元数据
```
docker image inspect [image]
```
### 删除镜像
当镜像存在关联的容器，并且容器处于运行（Up）或者停止（Exited）状态时，不允许删除该镜像
```
docker image rm
```

## 容器
###  启动新容器
```
docker container run
```
该命令的最简形式，以镜像和命令作为参数。镜像用于创建容器，而命令则是希望容器运行的应用
```
docker container run -it ubuntu /bin/bash 
```
命令会在前台启动一个 Ubuntu 容器，并运行 Bash Shell, -i: 交互式操作, -t: 终端, 要退出终端，直接输入 exit
### 后台运行
-d
```
docker container run -itd --name ubuntu-test ubuntu /bin/bash
```
### 端口映射
我们也可以通过 -p 参数来设置不一样的端口：
```
docker run -d -p 5000:5000 ubuntu python app.py
```
### 文件映射
```
docker run -it -v /true_path:container_path ubuntu python app.py
```

### 查看容器内运行的进程
```
docker container top <container-name or container-id>
```
### 进入容器
在使用 -d 参数时，容器启动后会进入后台，通过以下指令进入：
```
docker container attach  <container-name or container-id>
```
进入后再使用exit， 容器停止
### 容器查看
```
docker container ls
```
使用 -a 标记，还可以看到处于停止（Exited）状态的容器
### 查看正在运行的容器
```
docker ps
```
### 在运行状态的容器中，启动一个新进程
```
docker container exec
```
```
docker container exec -it <container-name or container-id> bash 
```
命令会在容器内部启动一个 Bash Shell 进程，并连接到该 Shell，从这个容器退出，容器不会停止
### 停止运行中的容器
```
docker container stop <容器ID or 容器名>
```
### 重启处于停止（Exited）状态的容器
```
docker container start <容器ID or 容器名>
```
### 显示容器的配置细节和运行时信息
```
docker container inspect <容器ID or 容器名>
```
### 删除停止运行的容器
```
docker container rm <容器ID or 容器名>
```

## 容器连接

### 网络端口映射
``` 
docker run -d -P training/webapp python app.py
```
使用 -P 绑定端口号 \
-P : 容器内部端口随机映射到主机的端口 \
-p : 容器内部端口绑定到指定的主机端口
### 查看端口的绑定情况
```
docker container port  <容器ID or 容器名> [指定端口]
```

## Docker 容器互联

### 新建docker网络
```
docker network create -d bridge test-net
```
d：参数指定 Docker 网络类型，有 bridge、host、overlay、maclan、none
### 查看docker网络
```
docker network ls
```
### 运行一个容器并连接到新建的 test-net 网络
```
docker container run -itd --name test1 --network test-net ubuntu /bin/bash
```
```
docker container run -itd --name test2 --network test-net ubuntu /bin/bash
```
使用ping命令查看是否连通:``ping test2``
###  删除网络
docker network rm test_net

## docker文件操作

### 复制宿主机上的文件到容器中
```
docker cp truePath container:containerPath
```
