import os
import time

from tool.fileTool import mkdir

# 将sqlArr 和查询结果连接
def dataConvertMain():
    timeStamp = time.strftime("%Y%m%d%H%M%S")
    dataSqlPath = './model_sql'
    dataResultPath = './model_result'
    convertDataPath = './concat_data_%s' % timeStamp
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
                    sql = sqlLists[i].split('#')
                    result = resultLists[i]
                    concatResult = sql[0] + '#' + sql[1] + '#' + sql[2] + '#' + result
                    concatResultLists.append(concatResult)
                concatResultFilePath = convertDataPath + '/' + baseName + '.csv'
                with open(concatResultFilePath, 'a') as concatResultFile:
                    concatResultFile.writelines(concatResultLists)


if __name__ == "__main__":
    dataConvertMain()
