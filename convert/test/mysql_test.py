import pymysql

# 为了兼容mysqldb，只需要加入
# pymysql.install_as_MySQLdb()


# 查询
def load():

    # 打开数据库连接
    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           passwd='WEN19961015',
                           charset='utf8'
                           )

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    cursor.execute("use imdb;")

    # 列出所有的表
    cursor.execute("show tables")
    tables = [row[0] for row in cursor.fetchall()]
    print(tables)

    # 查询每张表包含的属性
    tableProperties = {}
    for table_name in tables:
        cursor.execute('SELECT * FROM ' + table_name + ' limit 1')
        properties = [head[0] for head in cursor.description]
        tableProperties[table_name] = properties
        print(table_name + ":")
        print(properties)
    print(tableProperties)

    # 查询每张表内每个属性的最小值、最大值、基数、distinct value
    tablePropertiesInfo = {}
    for table_name in tableProperties.keys():
        for properties in tableProperties[table_name]:
            sql = 'SELECT min(%s), max(%s), count(%s), count(distinct(%s)) from %s' % \
                  (properties, properties, properties, properties, table_name)
            cursor.execute(sql)
            tp = table_name + '.' + properties
            info = ['%s' % row for row in cursor.fetchone()]
            print(tp)
            print(info)
            tablePropertiesInfo[tp] = info

    # 结果写入文件
    with open('../output/max_min.csv', 'a') as maxMin:
        for tp in tablePropertiesInfo.keys():
            info = tablePropertiesInfo[tp]
            line = tp + ',' + ','.join(info)
            maxMin.write(line+'\n')

    # 关闭数据库连接
    cursor.close()


if __name__ == "__main__":
    load()
