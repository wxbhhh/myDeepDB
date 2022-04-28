import pymysql


# 获取数据库的相关信息
def getDBInfo():

    conn = pymysql.connect( host='localhost',
                            port=3306,
                            user='root',
                            passwd='WEN19961015',
                            charset='utf8')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    cursor.execute("use imdb;")

    # 列出所有的表
    cursor.execute("show tables")
    tables = [row[0] for row in cursor.fetchall()]

    # 查询每张表包含的属性
    tableProperties = {}
    for table_name in tables:
        cursor.execute('SELECT * FROM ' + table_name + ' limit 1')
        properties = [head[0] for head in cursor.description]
        tableProperties[table_name] = properties

    # 关闭数据库连接
    cursor.close()

    return tableProperties

