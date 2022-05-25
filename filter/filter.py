import os
import time


# 将sqlArr 和查询结果连接
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
    dataFilter()
