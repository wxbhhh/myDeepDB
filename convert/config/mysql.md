# 创建用户组
groupadd tmpmysql
# 创建用户
useradd -g tmpmysql tmpmysql

# 初始化数据库
# 进入新mysql的bin目录下，执行
./mysqld --defaults-file=/data10/wxb/mysql8.0/my.cnf --user=tmpmysql --initialize

# 查看初始密码
cat /data10/wxb/mysqldata/mysql-error.log

# 把mysql.server放置到主目录mysql8.0中
cp /data10/wxb/mysql8.0/support-files/mysql.server /data10/wxb/mysql8.0/mysql

# 软连接/var/lib/mysql/mysql.sock 到   /data10/wxb/mysqltmpfile/mysql.sock
ln -s /data10/wxb/mysqltmpfile/mysql.sock /var/lib/mysql/mysql.sock

# 在主目录mysql8.0中启动mysql
mysql start