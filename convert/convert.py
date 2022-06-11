import csv
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


if __name__ == "__main__":
    train_csv_convert('./data_prepared/')
    # test_csv_convert('scale', './data_prepared/')
    # test_csv_convert('synthetic', './data_prepared/')
    # test_csv_convert('job-light', './data_prepared/')
