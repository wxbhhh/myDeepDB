import os
import time


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


def statistic_notmatch():
    csv_file_name = './match/train.csv'
    has_t_file_path = './match/hsa_t.csv'
    hs_gt_file_path = './match/hsa_t_gt.csv'
    hs_lt_file_path = './match/hsa_t_lt.csv'
    hs_eq_file_path = './match/hsa_t_eq.csv'
    has_t_no_op_file_path = './match/hsa_t_no_op.csv'

    has_t_file = open(has_t_file_path, 'w')
    hs_gt_file = open(hs_gt_file_path, 'w')
    hs_lt_file = open(hs_lt_file_path, 'w')
    hs_eq_file = open(hs_eq_file_path, 'w')
    has_t_no_op_file = open(has_t_no_op_file_path, 'w')
    with open(csv_file_name, 'r') as train_file:
        for row in train_file:
            if 'title t' in row:
                has_t_file.write(row)
                if ('t.production_year,<=' in row) or ('t.production_year,<' in row):
                    hs_lt_file.write(row)
                else:
                    if ('t.production_year,=>' in row) or ('t.production_year,>' in row):
                        hs_gt_file.write(row)
                    else:
                        if 't.production_year,=' in row:
                            hs_eq_file.write(row)
                        else:
                            has_t_no_op_file.write(row)

    has_t_file.close()
    hs_gt_file.close()
    hs_lt_file.close()
    hs_eq_file.close()
    has_t_no_op_file.close()


if __name__ == "__main__":
    # dataFilter()
    statistic_notmatch()
