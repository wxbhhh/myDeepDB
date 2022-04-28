### 备份数据库到文件
```
mysqldump -uroot -pWEN19961015 --databases dbname> bak.sql
```
### 还原数据库
```
mysql -uroot -pWEN19961015 dbname < bak.sq1
```