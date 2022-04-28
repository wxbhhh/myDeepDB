# 读取模型的相关配置
import csv


# 获取每个模型的相关信息
def get_model_info():
    modelConfigInfo = {}
    modelConfigPath = '../data/model_config.csv'
    with open(modelConfigPath, 'r') as modelConfigFile:
        for row in modelConfigFile:
            lineArr = row.split(',')
            modelName = lineArr[1]
            modelIndex = lineArr[0]
            modelTables = lineArr[2].split('#')
            modelProperties = lineArr[3].strip().split('#')

            model = {'index': modelIndex, 'table': modelTables, 'properties': modelProperties}
            modelConfigInfo[modelName] = model
    return modelConfigInfo


# 获取数据库每张表的属性的相关信息
def get_db_column_min_max_dnv_vals():
    file_name_column_min_max_vals = "../data/column_min_max_vals.csv"
    column_min_max_dnv_vals = {}
    with open(file_name_column_min_max_vals, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=','))
        for i, row in enumerate(data_raw):
            if i == 0:
                continue
            # column_min_max_vals[row[0]] = [float(row[1]), float(row[2])]
            column_min_max_dnv_vals[row[0]] = {'min': float(row[1]), 'max': float(row[2]), 'dnv': int(row[4])}
    return column_min_max_dnv_vals


db_column_min_max_dnv_vals = get_db_column_min_max_dnv_vals()


# 通过属性名找出该属性的最大最小值
def get_properties_max_min_val(properties_name):
    properties_info = db_column_min_max_dnv_vals[properties_name]
    return properties_info['max'], properties_info['min']


# 将分割好的sql转化成特殊的json格式，例如：
"""
    title t,movie_info_idx mi_idx,movie_keyword mk#t.id=mi_idx.movie_id,t.id=mk.movie_id#t.production_year,>,2005,mi_idx.info_type_id,=,101#850677

    =>
    't': {
            tables_alias:{ 't' },
            tables: { 'title t' }
            predicates: { 't.production_year,>,2005', 't.id,>,#(min)', 't.id,<,#(max)'}
            joins: {}
            exports: { 't.id=mi_idx.movie_id', 't.id=mk.movie_id'}
            }
    'mi': {
            tables_alias:{ 'mi' },
            tables: { 'movie_info_idx mi_idx' }
            predicates: { 'mi_idx.info_type_id,=,101', 'mi_idx.movie_id,>,#(min)', 'mi_idx.movie_id,<,#(max)' }
            joins: {}
            exports: { 't.id=mi_idx.movie_id' }
            }
    'mk': {
            tables_alias:{ mk },
            tables: { 'movie_keyword mk' }
            predicates: { 'mk.movie_id,>,#(min)', 'mk.movie_id,<,#(max)' }
            joins: {}
            exports: { 't.id=mk.movie_id' }
            }
    =>
    't,mi': {
            tables_alias:{ 't', 'mi' },
            tables: { 'title t', 'movie_info_idx mi_idx' }
            predicates: { 't.production_year,>,2005', 't.id,>,#(min)', 't.id,<,#(max)',
                            'mi_idx.info_type_id,=,101', 'mi_idx.movie_id,>,#(min)', 'mi_idx.movie_id,<,#(max)'}            
            joins: { 't.id=mi_idx.movie_id' }
            exports: { 't.id=mk.movie_id' }
    'mk': {
            tables_alias:{ mk },
            tables: { 'movie_keyword mk' }
            predicates: { 'mk.movie_id,>,#(min)', 'mk.movie_id,<,#(max)' }
            joins: {}
            exports: { 't.id=mk.movie_id' }
            }
    """


def split_sqlArr_to_sqlJsons(sqlArr):
    sqlJsons = {}

    sql_strs = sqlArr.split('#')

    tables_strs = sql_strs[0].split(',')
    for table_str in tables_strs:
        table_str_arr = table_str.split(' ')
        table_full_name = table_str_arr[0]
        table_alias = table_str_arr[1]
        # table_predicates[table_alias]['fullName'] = table_full_name

        sqlJsons[table_alias] = {
            'tables_alias': {table_alias},
            'tables': {table_str},
            'predicates': set(),
            'joins': set(),
            'exports': set()
        }

    join_strs = sql_strs[1].split(',')
    join_properties_map = {}
    for join_str in join_strs:
        join_str_arr = join_str.split('=')

        join_left_properties = join_str_arr[0]
        join_left_table_alias = join_left_properties.split('.')[0]
        left_properties_max, left_properties_min = get_properties_max_min_val(join_left_properties)
        join_right_properties = join_str_arr[1]
        join_right_table_alias = join_right_properties.split('.')[0]
        right_properties_max, right_properties_min = get_properties_max_min_val(join_right_properties)

        sqlJsons[join_left_table_alias]['predicates'].add('%s,>=,%s' % (join_left_properties, left_properties_min))
        sqlJsons[join_left_table_alias]['predicates'].add('%s,<=,%s' % (join_left_properties, left_properties_max))
        sqlJsons[join_left_table_alias]['predicates'].add('%s,>=,%s' % (join_left_properties, right_properties_min))
        sqlJsons[join_left_table_alias]['predicates'].add('%s,<=,%s' % (join_left_properties, right_properties_max))
        sqlJsons[join_right_table_alias]['predicates'].add('%s,>=,%s' % (join_right_properties, left_properties_min))
        sqlJsons[join_right_table_alias]['predicates'].add('%s,<=,%s' % (join_right_properties, left_properties_max))
        sqlJsons[join_right_table_alias]['predicates'].add('%s,>=,%s' % (join_right_properties, right_properties_min))
        sqlJsons[join_right_table_alias]['predicates'].add('%s,<=,%s' % (join_right_properties, right_properties_max))

        sqlJsons[join_left_table_alias]['exports'].add(join_str)
        sqlJsons[join_right_table_alias]['exports'].add(join_str)

        if join_left_properties in join_properties_map.keys():
            join_properties_map[join_left_properties].add(join_right_properties)
        else:
            join_properties_map[join_left_properties] = {join_right_properties}
        if join_right_properties in join_properties_map.keys():
            join_properties_map[join_right_properties].add(join_left_properties)
        else:
            join_properties_map[join_right_properties] = {join_left_properties}

    predicates_strs = sql_strs[2].split(',')
    for i in range(0, len(predicates_strs) // 3):
        predicate_properties = predicates_strs[i * 3]
        predicate_operator = predicates_strs[i * 3 + 1]
        predicate_val = predicates_strs[i * 3 + 2]
        predicate = predicate_properties + ',' + predicate_operator + ',' + predicate_val
        predicates_table_alias = predicate_properties.split('.')[0]
        sqlJsons[predicates_table_alias]['predicates'].add(predicate)

        if predicate_properties in join_properties_map.keys():
            for add_properties in join_properties_map[predicate_properties]:
                add_predicates_table_alias = add_properties.split('.')[0]
                add_predicate = add_properties + ',' + predicate_operator + ',' + predicate_val
                sqlJsons[add_predicates_table_alias]['predicates'].add(add_predicate)

    return sqlJsons


# 合并两个sqlJson
def merge_sqlJsons(json1, json2):
    tables_alias = json1['tables_alias'].union(json2['tables_alias'])
    tables = json1['tables'].union(json2['tables'])
    joins = json1['joins'].union(json2['joins']).union(json1['exports'].intersection(json2['exports']))
    predicates = json1['predicates'].union(json2['predicates'])
    exports = json1['exports'].symmetric_difference(json2['exports'])
    new_sqlJson = {
        'tables_alias': tables_alias,
        'tables': tables,
        'predicates': predicates,
        'joins': joins,
        'exports': exports
    }
    return new_sqlJson


# 将sqlJson转化为分割好的sql
def sqlJson_to_sqlArr(json):
    tables = json['tables']
    joins = json['joins']
    predicates = json['predicates']
    sql = ','.join(tables) + "#" + ','.join(joins) + "#" + ','.join(predicates)

    return sql


# 将分割好的sql转化成可执行的sql
def sqlArr_to_sql(sqlArr):
    rowInfo = sqlArr.split('#')
    query = rowInfo[0]
    joinPredicates = rowInfo[1]
    basePredicates = rowInfo[2]

    outStr = 'count(*)'

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
    if len(predicates) > 0:
        basePredicatesStr = ' AND '.join(predicates)

    sql = 'SELECT %s FROM %s WHERE %s AND %s ;' % (outStr, queryStr, joinPredicatesStr, basePredicatesStr)
    return sql


def test_sql_and_json(sqlArr):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++ start')
    sql_jsons_dict = split_sqlArr_to_sqlJsons(sqlArr)
    sql_jsons = [sql_jsons_dict[key] for key in sql_jsons_dict]
    print(sql_jsons)

    result_json = {
        'tables_alias': set(),
        'tables': set(),
        'predicates': set(),
        'joins': set(),
        'exports': set()
    }

    for key in sql_jsons_dict:
        tmp_json = sql_jsons_dict[key]
        print("准备合并的json:")
        print(tmp_json)

        print("json合并后：")
        result_json = merge_sqlJsons(result_json, tmp_json)
        print(result_json)
        print("合并后的sql:")
        result_sql = sqlJson_to_sqlArr(result_json)
        print(result_sql)

    print('------------------------------------------最终结果对比')
    print('原始sql: ' + sqlArr_to_sql(sqlArr))
    print('转化后sql: ' + sqlArr_to_sql(result_sql))
    # print(get_model_info())
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++ end')


def func():
    test_sql1 = 'title t,movie_info_idx mi_idx,movie_keyword mk#t.id=mi_idx.movie_id,t.id=mk.movie_id#t.production_year,>,2005,mi_idx.info_type_id,=,101#850677'
    test_sql2 = 'title t,movie_companies mc,cast_info ci#t.id=mc.movie_id,t.id=ci.movie_id#mc.company_id,=,27,mc.company_type_id,=,1,ci.person_id,<,1265390#96573'
    #test_sql_and_json(test_sql1)
    #test_sql_and_json(test_sql2)

    test_sql3 = 'title t,movie_companies mc,cast_info ci#t.id=mc.movie_id,t.id=ci.movie_id#mc.company_id,=,27,t.id,>,1000000,mc.company_type_id,=,1,ci.person_id,<,1265390#96573'
    test_sql_and_json(test_sql3)


def test():
    d1 = {'1'}
    d2 = {'2'}
    d3 = {'3'}
    d4 = {'4'}
    d4 = {'1', '2'}
    d6 = {'2', '4'}
    d7 = {'2', '3'}

    t = {'1', '2', '3'}


if __name__ == "__main__":
    func()
