

# 文件读取
def fileRead():

    # 使用 open() 打开文件
    file = open('filename.txt', mode='r')
    num = 1
    for con in file:
      print('第 %d 行：' % num, con)

    # 使用 readline()，读取一行信息
    con = file.readline()
    # 使用 readlines()，读取全部信息
    con = file.readlines()
    print(con)

    file.close()


def fileWrite():

    with open('hello.txt') as hello:
        hello.write("I Love You")# 创建一个列表
        txtlist = ['Python 私教\n', 'Java 私教\n', 'C++ 私教\n']
        hello.writelines(txtlist)



if __name__ == "__main__":
    with open('../output/hello.txt', 'x') as hello :
        hello.write("I Love You")
