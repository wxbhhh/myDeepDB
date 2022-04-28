import argparse
import threading
import time
import os
from queue import Queue

import pymysql

from tool.fileTool import mkdir


def queryDB(sqlFilePath, sqlResultDirPath):
    startTime = time.time()
    startTimeStr = time.strftime("%Y-%m-%d %H:%M:%S")
    # 连接数据库
    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           passwd='WEN19961015',
                           charset='utf8')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    cursor.execute("use imdb;")

    fileNameSubpaths = sqlFilePath.split('/')
    sqlFileName = fileNameSubpaths[len(fileNameSubpaths) - 1].split('.')[0]
    timeStamp = time.strftime("%Y%m%d%H%M%S")
    sqlResultFilePath = sqlResultDirPath + '/' + sqlFileName + "_%s_result.csv" % timeStamp
    sqlLogFilePath = sqlResultDirPath + '/' + sqlFileName + "_%s_result.log" % timeStamp

    logFile = open(sqlLogFilePath, 'a')
    with open(sqlFilePath, 'r') as sqlFile:
        with open(sqlResultFilePath, 'a') as resultFile:
            for sql in sqlFile:
                print('查询：' + sql)
                logFile.write('查询：' + sql + '\n')
                cursor.execute(sql)
                queryResult = ['%s' % row for row in cursor.fetchone()]
                queryResultStr = ','.join(queryResult)
                print('结果：' + queryResultStr)
                logFile.write('结果：' + queryResultStr + '\n')
                resultFile.write(queryResultStr)
                resultFile.write('\n')
                print('-------------------------------------------------------')
                logFile.write('-------------------------------------------------------\n')
            print("结果写入：" + resultFile.name)

    endTime = time.time()
    endTimeStr = time.strftime("%Y-%m-%d %H:%M:%S")
    print("耗时：%f s" % (endTime-startTime))
    logFile.write('--------------------------------------------------------\n')
    logFile.write('开始时间：%s\n' % startTimeStr)
    logFile.write("结束时间：%s\n" % endTimeStr)
    logFile.write("耗时：%f s" % (endTime-startTime) + '\n')
    logFile.close()

    conn.close()


def queryDBByDir(sqlDirPath, sqlResultDirPath):

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    dirName = os.path.basename(sqlDirPath)
    sqlResultOutDirPath = sqlResultDirPath + '/' + dirName + "_%s" % timeStamp
    mkdir(sqlResultOutDirPath)

    sqlFiles = os.listdir(sqlDirPath)  # 采用listdir来读取所有文件
    sqlFiles.sort()  # 排序
    sqlFilePaths = []  # 创建一个空列表
    for fileName in sqlFiles:  # 循环读取每个文件名
        filePath = sqlDirPath + '/' + fileName
        if not os.path.isdir(filePath):  # 判断该文件是否是一个文件夹
            queryDB(filePath, sqlResultOutDirPath)


def syncWork(queue):
    while True:
        filePath, sqlResultOutDirPath = queue.get()
        print('+++++++++++++++++++++++++++++++++开始查询: %s' % filePath)
        queryDB(filePath, sqlResultOutDirPath)
        print('++++++++++++++++++++++++++++++++::: %s 查询结束' % filePath)
        queue.task_done()


def queryDBByDirSync(sqlDirPath, sqlResultDirPath):

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    dirName = os.path.basename(sqlDirPath)
    sqlResultOutDirPath = sqlResultDirPath + '/' + dirName + "_%s" % timeStamp
    mkdir(sqlResultOutDirPath)

    sqlFiles = os.listdir(sqlDirPath)  # 采用listdir来读取所有文件
    sqlFiles.sort()  # 排序
    sqlFilePaths = []  # 创建一个空列表
    queue = Queue()
    for fileName in sqlFiles:  # 循环读取每个文件名
        filePath = sqlDirPath + '/' + fileName
        if not os.path.isdir(filePath):  # 判断该文件是否是一个文件夹
            queue.put((filePath, sqlResultOutDirPath))
           # queryDB(filePath, sqlResultOutDirPath)

    max_thread = 5
    # 创建包括3个线程的线程池
    for i in range(max_thread):
        t = threading.Thread(target=syncWork, args=[queue])
        # 设置线程daemon 主线程退出，daemon线程也会推出，即时正在运行
        t.daemon = True
        t.start()

    queue.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="file that include sql need to be execute ", default='default.sql')
    parser.add_argument("--out", help="saved result file directory", default='./result/')
    args = parser.parse_args()

    # 文件绝对路径
    current_file_path = __file__
    # 借助dirname()从绝对路径中提取目录
    current_file_dir = os.path.dirname(current_file_path)

    sqlFilePath = current_file_dir + '/testData/' + args.file
    sqlResultDir = current_file_dir + '/result'

    if os.path.isdir(sqlFilePath):
        sqlDirPath = current_file_dir + '/tmp'
        sqlResultDir = current_file_dir + '/result'
        # queryDBByDir(sqlDirPath, sqlResultDir)
        queryDBByDirSync(sqlFilePath, sqlResultDir)
    else:
        queryDB(sqlFilePath, sqlResultDir)




