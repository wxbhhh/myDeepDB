import json
import os
import random
import time

import pymysql

# 为了兼容mysqldb，只需要加入
# pymysql.install_as_MySQLdb()

tableNameAlias = {
        'cast_info': 'ci',
        'movie_companies': 'mc',
        'movie_info': 'mi',
        'movie_info_idx': 'mi_idx',
        'movie_keyword': 'mk',
        'title': 't'
    }

aliasTableName = {
        'ci': 'cast_info',
        'mc': 'movie_companies',
        'mi': 'movie_info',
        'mi_idx': 'movie_info_idx',
        'mk': 'movie_keyword',
        't': 'title'
    }


# 创建直方图信息文件
def create_histogram_config():

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

    with open('./output/histogram_config.csv', 'a') as histogram_file:
        for table_name in tables:
            for properties in tableProperties[table_name]:
                create_histogram_sql = 'analyze table imdb.%s update histogram on %s;' % (table_name, properties)
                print(create_histogram_sql)
                cursor.execute(create_histogram_sql)

                show_histogram_sql = 'select histogram from information_schema.column_statistics ' \
                                     'where table_name = \'%s\' and column_name = \'%s\' and schema_name = \'imdb\';' \
                                     % (table_name, properties)
                print(show_histogram_sql)
                cursor.execute(show_histogram_sql)

                result = cursor.fetchone()
                histogram_vals = []
                histogram_num = 20
                if result is None:
                    max_min_sql = 'select max(%s), min(%s) from %s' % (properties, properties, table_name)
                    cursor.execute(max_min_sql)
                    max_min_result = cursor.fetchone()
                    max_val = max_min_result[0]
                    min_val = max_min_result[1]
                    step = (max_val - min_val) // histogram_num

                    for i in range(histogram_num):
                        histogram_vals.append(str(min_val+step*(i+1)))
                else:
                    histogram_json = result[0]
                    histogram_dict = json.loads(histogram_json)
                    buckets = histogram_dict['buckets']
                    step = max(len(buckets)//histogram_num, 1)
                    for i in range(histogram_num):
                        bucket = buckets[(i * step) % len(buckets)]
                        if len(bucket) > 2:
                            bucket_max = bucket[1]
                        else:
                            bucket_max = bucket[0]
                        histogram_vals.append(str(bucket_max))

                print(histogram_vals)
                line = '%s.%s,%s\n' % (tableNameAlias[table_name], properties, '#'.join(histogram_vals))
                print(line)

                histogram_file.write(line)

    # 关闭数据库连接
    cursor.close()


# 加载直方图配置
def load_histogram_config():
    temp_column_histogram_info = dict()
    with open('./config/histogram_config.csv', 'r') as histogram_file:
        for column_histogram in histogram_file:
            column_histogram_arr = column_histogram.strip().split(',')
            column_name = column_histogram_arr[0]
            histogram_info = column_histogram_arr[1].split('#')
            temp_column_histogram_info[column_name] = histogram_info
    return temp_column_histogram_info


column_histogram_info = load_histogram_config()


# 加载每张表的属性
def load_table_properties():
    temp_table_properties = dict()
    for columnFullName in column_histogram_info.keys():
        columnFullNameArr = columnFullName.split('.')
        table_alias = columnFullNameArr[0]
        tabel_name = aliasTableName[table_alias]
        if tabel_name not in temp_table_properties:
            temp_table_properties[tabel_name] = []
        temp_table_properties[tabel_name].append(columnFullName)
    return temp_table_properties


table_properties = load_table_properties()


# 将分割好的sql转化成可执行的sql
def sqlArr_to_sql(sqlArr):
    rowInfo = sqlArr.strip().split('#')
    query = rowInfo[0]
    joinPredicates = rowInfo[1]
    basePredicates = rowInfo[2]

    outStr = 'count(*)'
    tables_arr = query.split(',')
    for table_str in tables_arr:
        table_name = table_str.split(' ')[0]
        properties = table_properties[table_name]
        for propertiesName in properties:
            outStr += ', count(distinct(%s))' % propertiesName

    queryStr = query

    joinPredicatesStr = 'true'
    if len(joinPredicates) > 0:
        joinPredicatesStr = joinPredicates.replace(',', ' AND ')

    basePredicatesPart = basePredicates.split(',')
    predicates = []
    for i in range(len(basePredicatesPart) // 3):
        predicate = basePredicatesPart[i * 3] + basePredicatesPart[i * 3 + 1] + basePredicatesPart[i * 3 + 2]
        predicates.append(predicate)
    basePredicatesStr = 'true'
    list.sort(predicates)
    if len(predicates) > 0:
        basePredicatesStr = ' AND '.join(predicates)

    sql = 'SELECT %s FROM %s WHERE %s AND %s ;' % (outStr, queryStr, joinPredicatesStr, basePredicatesStr)
    return sql


# 根据直方图信息创建sql(单表查询)
def generate_sql():
    operator_list = ['>', '<', '=', '<=', '>=']

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    resultOutPath = './output/result_%s' % timeStamp
    os.makedirs(resultOutPath)

    for tableName in tableNameAlias.keys():
        csv_file_name = resultOutPath + '/%s.csv' % tableName
        with open(csv_file_name, 'w') as csv_file:
            sql_arr_set = set()
            for i in range(10000):
                curr_table_properties = table_properties[tableName]
                curr_predicate_num = random.randint(1, len(curr_table_properties))
                predicate_properties = random.sample(curr_table_properties, curr_predicate_num)
                predicates = []
                for predicate_property in predicate_properties:
                    op = random.choice(operator_list)
                    val = random.choice(column_histogram_info[predicate_property])
                    predicate = '%s,%s,%s' % (predicate_property, op, val)
                    predicates.append(predicate)
                sql_arr = tableName + ' ' + tableNameAlias[tableName] + '##' + ','.join(predicates)
                print(sql_arr)
                sql_arr_set.add(sql_arr + '\n')
            sql_arr_list = list(sql_arr_set)
            list.sort(sql_arr_list)
            csv_file.writelines(sql_arr_list)

        sql_file_name = resultOutPath + '/%s.sql' % tableName
        with open(sql_file_name, 'w') as sql_file:
            for sql_arr in sql_arr_list:
                sql = sqlArr_to_sql(sql_arr)
                print(sql)
                sql_file.write(sql + '\n')


table_join_key = {
    'cast_info': 'movie_id',
    'movie_companies': 'movie_id',
    'movie_info': 'movie_id',
    'movie_info_idx': 'movie_id',
    'movie_keyword': 'movie_id',
    'title': 'id'
}


# 根据直方图信息创建sql(连接查询)
def generate_join_sql():
    operator_list = ['>', '<', '=', '<=', '>=']

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    resultOutPath = './output/result_%s' % timeStamp
    os.makedirs(resultOutPath)

    list1 = sorted(list(table_join_key.keys()))
    list2 = sorted(list(table_join_key.keys()))
    for j, tableName1 in enumerate(list1):
        for k, tableName2 in enumerate(list2):
            if j >= k or j == 5 or k == 5:
                continue
            csv_file_name = resultOutPath + '/%s-%s.csv' % (tableName1, tableName2)
            with open(csv_file_name, 'w') as csv_file:
                sql_arr_set = set()
                for i in range(10000):
                    predicates = []

                    table1_properties = table_properties[tableName1]
                    table1_predicate_num = random.randint(1, len(table1_properties))
                    predicate1_properties = random.sample(table1_properties, table1_predicate_num)
                    for predicate_property in predicate1_properties:
                        op = random.choice(operator_list)
                        val = random.choice(column_histogram_info[predicate_property])
                        predicate = '%s,%s,%s' % (predicate_property, op, val)
                        predicates.append(predicate)

                    table2_properties = table_properties[tableName2]
                    table2_predicate_num = random.randint(1, len(table2_properties))
                    predicate2_properties = random.sample(table2_properties, table2_predicate_num)
                    for predicate_property in predicate2_properties:
                        op = random.choice(operator_list)
                        val = random.choice(column_histogram_info[predicate_property])
                        predicate = '%s,%s,%s' % (predicate_property, op, val)
                        predicates.append(predicate)

                    table_str = tableName1 + ' ' + tableNameAlias[tableName1] + ',' + tableName2 + ' ' + tableNameAlias[tableName2]
                    join_str = tableNameAlias[tableName1] + '.' + table_join_key[tableName1] + '=' + tableNameAlias[tableName2] + '.' + table_join_key[tableName2]
                    predicate_str = ','.join(predicates)
                    sql_arr = table_str + '#' + join_str + '#' + predicate_str
                    print(sql_arr)
                    sql_arr_set.add(sql_arr + '\n')

                sql_arr_list = list(sql_arr_set)
                list.sort(sql_arr_list)
                csv_file.writelines(sql_arr_list)

                sql_file_name = resultOutPath + '/%s-%s.sql' % (tableName1, tableName2)
                with open(sql_file_name, 'w') as sql_file:
                    for sql_arr in sql_arr_list:
                        sql = sqlArr_to_sql(sql_arr)
                        print(sql)
                        sql_file.write(sql + '\n')


if __name__ == "__main__":
    # create_histogram_config()
    # generate_sql()
    generate_join_sql()
