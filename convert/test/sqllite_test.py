import sqlite3


# 查询
def load():
    # 连接数据库
    con = sqlite3.connect("E:/data_temp/soccer.sqlite")
    # 获得游标
    cur = con.cursor()

    # 查询包含的表
    cur.execute('SELECT name _id FROM sqlite_master WHERE type =\'table\' and name like \'m_%\';')
    tables = [row[0] for row in cur.fetchall()]
    print(tables)

    # 查询每张表包含的属性
    tableProperties = {}
    for table_name in tables:
        cur.execute('SELECT * FROM ' + table_name + ' limit 1')
        properties = [head[0] for head in cur.description]
        tableProperties[table_name] = properties
        print(table_name+":")
        print(properties)
    print(tableProperties)

    # 查询每张表内每个属性的最小值、最大值、基数、distinct value
    tablePropertiesInfo = {}
    for table_name in tableProperties.keys():
        for properties in tableProperties[table_name]:
            sql = 'SELECT min(%s), max(%s), count(%s), count(distinct(%s)) from %s' % \
                  (properties, properties, properties, properties, table_name)
            cur.execute(sql)
            tp = table_name + '.' + properties
            info = [row for row in cur.fetchone()]
            print(tp)
            print(info)

    con.commit()
    cur.close()


if __name__ == "__main__":
    load()
