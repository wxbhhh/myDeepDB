# 读取模型的相关配置
import copy
import os

from myCE3.mymscn.myDB import get_model_info, get_db_column_min_max_dnv_vals

db_column_min_max_dnv_vals = get_db_column_min_max_dnv_vals()


# 通过属性名找出该属性的最大最小值
def get_properties_max_min_val(properties_name):
    properties_info = db_column_min_max_dnv_vals[properties_name]
    return properties_info['max'], properties_info['min']


def get_tableset_tablestr_list():
    tableset_list = []
    tablestr_list = []

    current_path = os.path.dirname(__file__)
    modelConfigPath = '{}/../config/model_config.csv'.format(current_path)
    with open(modelConfigPath, 'r') as modelConfigFile:
        for row in modelConfigFile:
            lineArr = row.split(',')
            modelTableset = set(lineArr[2].split('#'))
            modelTablestr = lineArr[2].replace('#', ',')

            tableset_list.append(modelTableset)
            tablestr_list.append(modelTablestr)
    return tableset_list, tablestr_list


global_tableset_list, global_tablestr_list = get_tableset_tablestr_list()


def get_tablestr_of_tableset(tableset):
    index = global_tableset_list.index(tableset)
    return global_tablestr_list[index]


# 将分割好的sql转化成特殊的json格式，例如：
"""
    title t,movie_info_idx mi_idx,movie_keyword mk#t.id=mi_idx.movie_id,t.id=mk.movie_id#t.production_year,>,2005,mi_idx.info_type_id,=,101#850677

    =>
    其中exports表示需要与其他sqlJson合并的join谓词
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


# 将分割好的sql转化成特殊的json格式，规则如上
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
            'exports': set(),
            'exports_properties': set()
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
        sqlJsons[join_left_table_alias]['exports_properties'].add(join_left_properties)
        sqlJsons[join_right_table_alias]['exports_properties'].add(join_right_properties)

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


# 将分割好的sql根据分割策略转化成特殊的json格式，例如：
"""
分割好的的sql sqlArr: title t,movie_info_idx mi_idx,movie_keyword mk#t.id=mi_idx.movie_id,t.id=mk.movie_id#t.production_year,>,2005,mi_idx.info_type_id,=,101#850677
分割策略 table_subsets_turple: ({'title t', 'movie_info_idx mi_idx'},{'movie_keyword mk'})
=>
其中exports表示需要与其他sqlJson合并的join谓词
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


# 将分割好的sql根据分割策略转化成特殊的json格式，规则如上
def split_sqlArr_to_sqlJsons_by_policy(sqlArr, table_subsets_turple):
    sqlJsons = {}

    alias_index = {}
    for index, table_subsets in enumerate(table_subsets_turple):
        table_alias_set = set()
        for table_str in table_subsets:
            table_str_arr = table_str.split(' ')
            table_full_name = table_str_arr[0]
            table_alias = table_str_arr[1]
            alias_index[table_alias] = index
            table_alias_set.add(table_alias)

        sqlJsons[index] = {
            'tables_alias': table_alias_set,
            'tables': table_subsets,
            'predicates': set(),
            'joins': set(),
            'exports': set(),
            'exports_properties': set()
        }
    print(alias_index)

    sql_strs = sqlArr.split('#')

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

        join_left_table_index = alias_index[join_left_table_alias]
        join_right_table_index = alias_index[join_right_table_alias]

        if join_right_table_index == join_left_table_index:
            sqlJsons[join_left_table_index]['joins'].add(join_str)
            continue

        sqlJsons[join_left_table_index]['predicates'].add('%s,>=,%s' % (join_left_properties, left_properties_min))
        sqlJsons[join_left_table_index]['predicates'].add('%s,<=,%s' % (join_left_properties, left_properties_max))
        sqlJsons[join_left_table_index]['predicates'].add('%s,>=,%s' % (join_left_properties, right_properties_min))
        sqlJsons[join_left_table_index]['predicates'].add('%s,<=,%s' % (join_left_properties, right_properties_max))
        sqlJsons[join_right_table_index]['predicates'].add('%s,>=,%s' % (join_right_properties, left_properties_min))
        sqlJsons[join_right_table_index]['predicates'].add('%s,<=,%s' % (join_right_properties, left_properties_max))
        sqlJsons[join_right_table_index]['predicates'].add('%s,>=,%s' % (join_right_properties, right_properties_min))
        sqlJsons[join_right_table_index]['predicates'].add('%s,<=,%s' % (join_right_properties, right_properties_max))

        sqlJsons[join_left_table_index]['exports'].add(join_str)
        sqlJsons[join_right_table_index]['exports'].add(join_str)

        sqlJsons[join_left_table_index]['exports_properties'].add(join_left_properties)
        sqlJsons[join_right_table_index]['exports_properties'].add(join_right_properties)

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

        sqlJson_index = alias_index[predicates_table_alias]
        sqlJsons[sqlJson_index]['predicates'].add(predicate)

        if predicate_properties in join_properties_map.keys():
            for add_properties in join_properties_map[predicate_properties]:
                add_predicates_table_alias = add_properties.split('.')[0]
                sqlJson_add_index = alias_index[add_predicates_table_alias]
                add_predicate = add_properties + ',' + predicate_operator + ',' + predicate_val
                sqlJsons[sqlJson_add_index]['predicates'].add(add_predicate)

    return sqlJsons


# 合并两个sqlJson
def merge_sqlJsons(json1, json2):
    """
    集合交集：A and B， intersection
    集合并集：A or B，union
    集合差集： A-B，difference
    集合对称差：AoB，symmetric_difference
    """
    tables_alias = json1['tables_alias'].union(json2['tables_alias'])
    tables = json1['tables'].union(json2['tables'])
    joins = json1['joins'].union(json2['joins']).union(json1['exports'].intersection(json2['exports']))
    predicates = json1['predicates'].union(json2['predicates'])
    exports = json1['exports'].symmetric_difference(json2['exports'])
    exports_properties = json1['exports_properties'].union(json2['exports_properties'])
    new_sqlJson = {
        'tables_alias': tables_alias,
        'tables': tables,
        'predicates': predicates,
        'joins': joins,
        'exports': exports,
        'exports_properties': exports_properties
    }
    return new_sqlJson


# 将sqlJson转化为分割好的sql
def sqlJson_to_sqlArr(json):
    tables = json['tables']
    joins = json['joins']
    predicates = json['predicates']

    # tables_str = ','.join(tables)
    tables_str = get_tablestr_of_tableset(set(tables))
    joins_str = ','.join(joins)
    predicates_str = ','.join(predicates)
    sql = tables_str + "#" + joins_str + "#" + predicates_str

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


# 从基本的子集合列表中扩展生成所有的子集合的列表以及相应的生成方式
def get_all_policy(base_subset_list, base_subsets_index):
    """
    :param base_subset_list: 基本的子集合的列表
    :param base_subsets_index: 基本的子集合中的位置和策略间的映射（处理后的结果目前还用不到）
    :return:new_sets_list：基本的子集合列表通过并运算扩展生成的子集合列表，policy：各个子集合对应的从基本子集合中生成的策略
    """

    temp_sets_list = copy.deepcopy(base_subset_list)
    temp_sets_size = len(temp_sets_list)

    new_sets_size = 0
    new_sets_list = []

    policy = {}
    subsets_index = copy.deepcopy(base_subsets_index)

    curent_index_size = len(base_subsets_index)

    while new_sets_size != temp_sets_size:

        temp_sets_size = new_sets_size
        new_sets_list = copy.deepcopy(temp_sets_list)
        for i, subset1 in enumerate(temp_sets_list):
            for k, subset2 in enumerate(temp_sets_list):
                if k <= i:
                    continue

                if subset1.isdisjoint(subset2):
                    local_temp_subset = subset1.union(subset2)
                    if local_temp_subset not in new_sets_list:
                        new_sets_list.append(local_temp_subset)
                        subsets_index[curent_index_size] = [(i, k)]
                        curent_index_size += 1
                    else:
                        union_subsets_index = new_sets_list.index(local_temp_subset)
                        union_subsets = subsets_index[union_subsets_index]
                        if len(union_subsets) == 1 and len(union_subsets[0]) == 1:
                            continue
                        else:
                            if(i, k) not in union_subsets:
                                subsets_index[union_subsets_index].append((i, k))

        # print(new_sets_list)
        new_sets_size = len(new_sets_list)
        temp_sets_list = copy.deepcopy(new_sets_list)

    for i in subsets_index:
        for k, model_policy_tuple in enumerate(subsets_index[i]):
            if len(model_policy_tuple) == 1:
                policy[i] = model_policy_tuple
                break
            if k > 0:
                continue
            left_model_index = model_policy_tuple[0]
            right_model_index = model_policy_tuple[1]
            policy[i] = policy[left_model_index] + policy[right_model_index]
    # print(policy)
    # print(subsets_index)
    return new_sets_list, subsets_index, policy


def get_all_sets_and_policy():
    model_info = get_model_info()
    base_subsets_list = []
    base_subsets_index = {}
    index = 0
    for model_name in model_info.keys():
        model = model_info[model_name]
        subset = set(model['table'])
        base_subsets_list.append(subset)
        base_subsets_index[index] = [(index,)]
        index += 1
    all_sets_list, _, policy = get_all_policy(base_subsets_list, base_subsets_index)
    return all_sets_list, policy, base_subsets_list


global_all_sets_list, global_policy, global_base_subsets_list = get_all_sets_and_policy()


# 将分割好的sqlArr划分成几个可执行的sqlJson
def split_sqlArr_to_access_sqlJsons(sqlArr):
    tar_model_table_sets = set(sqlArr.split('#')[0].split(','))
    tar_model_index = global_all_sets_list.index(tar_model_table_sets)
    tar_model_policy = global_policy[tar_model_index]
    table_subsets_turple = ()
    for subset_index in tar_model_policy:
        table_subsets_turple = table_subsets_turple + (global_base_subsets_list[subset_index],)
    sqlJsons = split_sqlArr_to_sqlJsons_by_policy(sqlArr, table_subsets_turple)

    return sqlJsons

    # access_sqlArrs = []
    # for sqlJson_key in sqlJsons:
    #     sqlJson = sqlJsons[sqlJson_key]
    #     access_sqlArr = sqlJson_to_sqlArr(sqlJson)
    #     access_sqlArrs.append(access_sqlArr)
    # return access_sqlArrs


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
        'exports': set(),
        'exports_properties': set()
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


# 测试sqlArr的拆分和组合
def test1():
    test_sql1 = 'title t,movie_info_idx mi_idx,movie_keyword mk#t.id=mi_idx.movie_id,t.id=mk.movie_id#t.production_year,>,2005,mi_idx.info_type_id,=,101#850677'
    test_sql2 = 'title t,movie_companies mc,cast_info ci#t.id=mc.movie_id,t.id=ci.movie_id#mc.company_id,=,27,mc.company_type_id,=,1,ci.person_id,<,1265390#96573'
    #test_sql_and_json(test_sql1)
    #test_sql_and_json(test_sql2)

    test_sql3 = 'title t,movie_companies mc,cast_info ci#t.id=mc.movie_id,t.id=ci.movie_id#mc.company_id,=,27,t.id,>,1000000,mc.company_type_id,=,1,ci.person_id,<,1265390#96573'
    test_sql_and_json(test_sql3)

    test_sql4 = 'cast_info ci,movie_companies mc#ci.movie_id=mc.movie_id#ci.person_id,>,50,ci.role_id,>,3,mc.company_id,>,11328,mc.company_type_id,=,2#20'
    test_sql_and_json(test_sql4)

# 测试通过基本子集合列表生成所有子集合列表的合并策略
def test2():
    model_info = get_model_info()
    # print(model_info)

    base_subsets_list = []
    base_subsets_index = {}
    index = 0
    for model_name in model_info.keys():
        model = model_info[model_name]
        subset = set(model['table'])
        base_subsets_list.append(subset)
        base_subsets_index[index] = [(index,)]
        index += 1
    print(base_subsets_list)
    new_sets_list, subsets_index, policy = get_all_policy(base_subsets_list, base_subsets_index)
    print(new_sets_list)
    print(subsets_index)
    print(policy)


def test3():

    model_info = get_model_info()
    # print(model_info)
    base_subsets_list = []
    base_subsets_index = {}
    index = 0
    for model_name in model_info.keys():
        model = model_info[model_name]
        subset = set(model['table'])
        base_subsets_list.append(subset)
        base_subsets_index[index] = [(index,)]
        index += 1
    # print(base_subsets_list)
    all_sets_list, _, policy = get_all_policy(base_subsets_list, base_subsets_index)

    sqlArr = 'movie_info mi,movie_companies mc,cast_info ci#mi.movie_id=mc.movie_id,mi.movie_id=ci.movie_id#mc.company_id,=,27,mi.movie_id,>,1000000,mc.company_type_id,=,1,ci.person_id,<,1265390#96573'
    # test_sql_and_json(sqlArr)


    tar_model_table_sets = set(sqlArr.split('#')[0].split(','))
    print(tar_model_table_sets)
    tar_model_index = all_sets_list.index(tar_model_table_sets)
    print(tar_model_index)
    tar_model_policy = policy[tar_model_index]
    print(tar_model_policy)
    table_subsets_turple = ()
    for subset_index in tar_model_policy:
        table_subsets_turple = table_subsets_turple + (base_subsets_list[subset_index],)
    print(table_subsets_turple)
    table_subsets_turple = ({'movie_companies mc'}, {'movie_info mi', 'cast_info ci'})
    # sqlJsons = split_sqlArr_to_sqlJsons(sqlArr)
    sqlJsons = split_sqlArr_to_sqlJsons_by_policy(sqlArr, table_subsets_turple)
    print(sqlJsons)

    print(sqlArr_to_sql(sqlArr))

    result_json = {
        'tables_alias': set(),
        'tables': set(),
        'predicates': set(),
        'joins': set(),
        'exports': set(),
        'exports_properties': set()
    }
    for sqlJson_key in sqlJsons:
        sqlJson = sqlJsons[sqlJson_key]
        sqlArr = sqlJson_to_sqlArr(sqlJson)
        sql = sqlArr_to_sql(sqlArr)
        print(sql)
        result_json = merge_sqlJsons(result_json, sqlJson)
        result_sqlArr = sqlJson_to_sqlArr(result_json)
        result_sql = sqlArr_to_sql(result_sqlArr)
        print(result_sql)


if __name__ == "__main__":
    # test1()
    test2()
    # test3()
