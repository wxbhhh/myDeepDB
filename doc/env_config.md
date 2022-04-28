## docker配置
### 拉取anaconda3镜像
```
docker pull continuumio/anaconda3
```
### 拉取mysql镜像
```
docker pull mysql
```
### 创建docker网络
创建名为wxb_net的docker网络
```
docker network create -d bridge wxb_net
```
### 创建名为wxb_anaconda的容器并接入网络
将真实路径下的/data10/wxb/query目录映射到容器中的/home/query路径下
```
docker run -it -v /data10/wxb/query:/home/query --name wxb_anaconda --network wxb_net  continuumio/anaconda3 /bin/bash
```
### 根据yml文件创建环境
```
conda env create -n wxb_env -f environment.yml
```
### 创建名为wxb_mysql容器
```
docker run -d -p 3308:3306 --privileged=true  -v /data10/wxb/docker_mysql:/home/mysqldata -e MYSQL_ROOT_PASSWORD=WEN19961015 --name wxb_mysql  --network wxb_net mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci
```
-d　       表示后台运行 \
-p　　     表示服务器端口和容器内部端口映射关联 \
--privileged=true　                      设值MySQL 的root用户权限, 否则外部不能使用root用户登陆  \
-v /data10/wxb/docker_mysql:/home/mysqldata 将服务器中/data10/wxb/docker_mysql目录映射到docker中的/home/mysqldata目录   \
-v /data10/wxb/data:/var/lib/mysql　　 同上,映射数据库的数据目录, 避免以后docker删除重新运行MySQL容器时数据丢失  \
-e MYSQL_ROOT_PASSWORD=WEN19961015　　　      设置MySQL数据库root用户的密码   \
--name mysql　　　　                     设值容器名称为mysql   \
mysql:5.7.30　　                         表示从docker镜像mysql:5.7中启动一个容器  \
--character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci  设值数据库默认编码
### 进入创建的mysql容器
```
docker exec -it wxb_mysql bash
```
### 执行MySQL命令, 输入root密码, 连接MySQL
```
mysql -uroot -pWEN19961015
```
####输入密码后, 执行下面命令创建新用户 (用户名: test , 密码: test123)
```
GRANT ALL PRIVILEGES ON *.* TO 'test'@'%' IDENTIFIED BY 'test123' WITH GRANT OPTION;
```
### 在容器外登录
```
mysql -utest -ptest123 -P3308 -h127.0.0.1
```
