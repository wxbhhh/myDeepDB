import csv
import os
import time

from tool.dbTool import *
from tool.fileTool import mkdir

tableNameAlias = {
    'cast_info': 'ci',
    'movie_companies': 'mc',
    'movie_info': 'mi',
    'movie_info_idx': 'mi_idx',
    'movie_keyword': 'mk',
    'title': 't'
}


# csv中的一行转为SQL
def rowToSQL(row, addCountInfo=None):
    rowInfo = row.split('#')

    query = rowInfo[0]
    joinPredicates = rowInfo[1]
    basePredicates = rowInfo[2]

    outStr = 'count(*)'
    if addCountInfo is not None:
        for tableStr in query.split(','):
            tableName = tableStr.split(' ')[0]
            outStr += ', ' + ', '.join(addCountInfo[tableName])

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


# 获取文件中所有的查询类型
def getQueryTypes(tables):
    table_names = set()
    for query in tables:
        # list.sort(query)
        table_names.add(','.join(query))
    return table_names


# 将原始train.csv文件分割并转sql文件
def train_csv_convert(outDir):
    filePath = 'data_origin/train.csv'

    tables = []
    with open(filePath, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter='#'))
        for row in data_raw:
            tables.append(row[0].split(','))

    # 获取文件内不同的查询类型
    queryType = getQueryTypes(tables)
    queryType = list(queryType.intersection(queryType))
    list.sort(queryType)
    for queryTables in queryType:
        print(queryTables)
    print(len(queryType))

    # 列表转字典：使用内置函数zip
    queryTypeSize = range(len(queryType))
    modelIndex = dict(zip(queryType, queryTypeSize))
    print(modelIndex)

    dbInfo = getDBMoreInfo()
    addInfo = {}
    for tableName in dbInfo.keys():
        properties = dbInfo[tableName]['properties']
        countProperties = []
        for propertiesName in properties:
            countProperties.append('count(distinct(%s.%s))' % (tableNameAlias[tableName], propertiesName))
        addInfo[tableName] = countProperties

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    csvOutPath = (outDir + "train_csv_%s/" % timeStamp)
    mkdir(csvOutPath)
    sqlOutPath = (outDir + "train_sql_%s/" % timeStamp)
    mkdir(sqlOutPath)

    csvFiles = {}
    sqlFiles = {}
    configInfo = []
    for query in modelIndex.keys():
        csvFileName = csvOutPath + 'model_%s.csv' % modelIndex[query]
        csvFile = open(csvFileName, mode='a')
        csvFiles[query] = csvFile
        sqlFileName = sqlOutPath + 'model_%s.sql' % modelIndex[query]
        sqlFile = open(sqlFileName, mode='a')
        sqlFiles[query] = sqlFile

        modelConfig = '%s,model_%s,%s,' % (modelIndex[query], modelIndex[query], query.replace(',', '#').strip())
        modelProperties = []
        model_card = 1
        for tableStr in query.split(','):
            tableName = tableStr.split(' ')[0]
            tableProperties = dbInfo[tableName]['properties']
            model_card = model_card*dbInfo[tableName]['card']
            for properties in tableProperties:
                modelProperties.append((tableNameAlias[tableName] + '.' + properties))
        modelConfig += '#'.join(modelProperties) + (',%s\n' % model_card)
        configInfo.append(modelConfig)

    # 模型相关信息的配置文件
    modelConfigFilePath = (outDir + "train_model_config_%s.csv" % timeStamp)
    with open(modelConfigFilePath, 'a') as configFile:
        configFile.writelines(configInfo)


    # 分割文件
    with open(filePath, 'r') as f:
        for row in f:
            # print(row)

            query = row.split('#')[0]
            index = modelIndex[query]

            csvFile = csvFiles[query]
            csvFile.write(row)

            sqlFile = sqlFiles[query]
            sql = rowToSQL(row, addInfo)
            # print(sql)
            sqlFile.write(sql)
            sqlFile.write('\n')

    for query in modelIndex.keys():
        csvFiles[query].close()
        sqlFiles[query].close()


# 将原始测试用csv转sql文件，fileName: scale, job-light, synthetic
def test_csv_convert(fileName='scale', outDir='./data_prepared/'):
    dbInfo = getDBInfo()
    addInfo = {}
    for tableName in dbInfo.keys():
        properties = dbInfo[tableName]
        countProperties = []
        for propertiesName in properties:
            countProperties.append('count(distinct(%s.%s))' % (tableNameAlias[tableName], propertiesName))
        addInfo[tableName] = countProperties

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    sqlFileName = (outDir + fileName + "_%s.sql" % timeStamp)

    filePath = './data_origin/' + fileName + '.csv'
    # 分割文件
    with open(filePath, 'r') as f:
        with open(sqlFileName, 'a') as sqlFile:
            for row in f:
                # print(row)
                sql = rowToSQL(row)
                # print(sql)
                sqlFile.write(sql)
                sqlFile.write('\n')


# 将多个csv文件合并到一起
def csv_connect_data():

    modelDataPath = './file'

    modelDataFiles = os.listdir(modelDataPath)  # 采用listdir来读取所有文件
    modelDataFiles.sort()  # 排序

    train_data_file_path = './out/train.csv'
    with open(train_data_file_path, 'w') as train_data_file:
        for modelFileName in modelDataFiles:
            modelFilePath = modelDataPath + '/' + modelFileName
            with open(modelFilePath, 'r') as model_file:
                for row in model_file:
                    train_data_file.write(row)


# 拆分
def split_into_two():
    filePath = './data_train/train.csv'

    tables = []
    with open(filePath, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter='#'))
        for row in data_raw:
            tables.append(row[0].split(','))

    # 获取文件内不同的查询类型
    queryType = getQueryTypes(tables)
    queryType = list(queryType.intersection(queryType))
    list.sort(queryType)
    for queryTables in queryType:
        print(queryTables)
    print(len(queryType))

    # 列表转字典：使用内置函数zip
    queryTypeSize = range(len(queryType))
    modelIndex = dict(zip(queryType, queryTypeSize))
    print(modelIndex)

    dbInfo = getDBMoreInfo()
    addInfo = {}
    for tableName in dbInfo.keys():
        properties = dbInfo[tableName]['properties']
        countProperties = []
        for propertiesName in properties:
            countProperties.append('count(distinct(%s.%s))' % (tableNameAlias[tableName], propertiesName))
        addInfo[tableName] = countProperties


    csv_file_dir = './data_origin'
    false_csv_dir_path = './output/false_csv'
    false_sql_dir_path = './output/false_sql'
    true_csv_dir_path = './output/true_csv'

    mkdir(false_csv_dir_path)
    mkdir(true_csv_dir_path)
    mkdir(false_sql_dir_path)

    csvFiles = os.listdir(csv_file_dir)  # 采用listdir来读取所有文件
    csvFiles.sort()  # 排序

    false_all = 0
    true_all = 0
    for csvFileName in csvFiles:
        true_csv_file = open(true_csv_dir_path + '/' + csvFileName, 'w')
        sqlFileName = csvFileName.split(',')[0] + '.sql'
        false_sql_file = open(false_sql_dir_path + '/' + sqlFileName, 'w')
        false_csv_file = open(false_csv_dir_path + '/' + csvFileName, 'w')

        cur_false_num = 0
        cur_true_num = 0
        with open(csv_file_dir + '/' + csvFileName, 'r') as csvFile:
            for row in csvFile:
                if 'title t' in row:
                    if ('t.production_year,<=' in row) or ('t.production_year,<' in row) or \
                        ('t.production_year,=>' in row) or ('t.production_year,>' in row) or \
                            ('t.production_year,=' in row):
                        true_all += 1
                        cur_true_num += 1
                        true_csv_file.write(row)
                    else:
                        sql = rowToSQL(row, addInfo)
                        false_csv_file.write(row)
                        false_sql_file.write(sql + '\n')
                        false_all += 1
                        cur_false_num += 1
                else:
                    cur_true_num += 1
                    true_all += 1
                    true_csv_file.write(row)

        print('%s 出错：%s' % (csvFileName, cur_false_num))
        print('%s 正确：%s' % (csvFileName, cur_true_num))

        true_csv_file.close()
        false_csv_file.close()
        false_sql_file.close()

    print('------------------------------------------')
    print('共出错：%s' % false_all)
    print('共正确：%s' % true_all)


# 将sqlArr 和查询结果连接
def dataConvertMain(dataSqlPath, dataResultPath, outPath):
    timeStamp = time.strftime("%Y%m%d%H%M%S")
    convertDataPath = outPath + '/concat_data_%s' % timeStamp
    mkdir(convertDataPath)

    sqlFiles = os.listdir(dataSqlPath)  # 采用listdir来读取所有文件
    sqlFiles.sort()  # 排序

    for fileName in sqlFiles:  # 循环读取每个文件名
        baseName = fileName.split('.')[0]
        sqlFilePath = dataSqlPath + '/' + baseName + '.csv'
        resultFilePath = dataResultPath + '/' + baseName + '_result.csv'
        with open(sqlFilePath, 'r') as sqlFile:
            with open(resultFilePath, 'r') as resultFile:
                sqlLists = sqlFile.readlines()
                resultLists = resultFile.readlines()

                concatResultLists = []
                for i in range(len(resultLists)):
                    sql = sqlLists[i].strip().split('#')
                    result = resultLists[i].strip()
                    card_dnv = result.split(',')
                    card = card_dnv[0]
                    if int(card) != 0:
                        concatResult = sql[0] + '#' + sql[1] + '#' + sql[2] + '#' + result + '\n'
                        concatResultLists.append(concatResult)
                concatResultFilePath = convertDataPath + '/' + baseName + '.csv'
                with open(concatResultFilePath, 'a') as concatResultFile:
                    concatResultFile.writelines(concatResultLists)


# 过滤基数为0的sql
def dataFilter():
    dataSqlArrPath = './file'
    dataResultPath = './out'

    sqlFiles = os.listdir(dataSqlArrPath)  # 采用listdir来读取所有文件
    sqlFiles.sort()  # 排序

    for fileName in sqlFiles:  # 循环读取每个文件名
        baseName = fileName.split('.')[0]
        sqlFilePath = dataSqlArrPath + '/' + baseName + '.csv'

        with open(sqlFilePath, 'r') as sqlFile:
            sqlLists = sqlFile.readlines()
            resultLists = []
            for line in sqlLists:
                sqlArr = line.split('#')
                card_and_dnv = sqlArr[3]
                card = int(card_and_dnv.split(',')[0])
                if card > 0:
                    resultLists.append(line)

        resultFilePath = dataResultPath + '/' + baseName + '.csv'
        with open(resultFilePath, 'w') as resultFile:
            resultFile.writelines(resultLists)


if __name__ == "__main__":
    # csv_connect_data()
    # train_csv_convert('./data_prepared/')
    # test_csv_convert('scale', './data_prepared/')
    # test_csv_convert('synthetic', './data_prepared/')
    # test_csv_convert('job-light', './data_prepared/')
    # dataFilter()

    dataConvertMain('./file/csv', './file/result', './out')
