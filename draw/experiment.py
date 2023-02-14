import matplotlib.pyplot as plt
import numpy as np

# 这两行代码解决 plt 中文显示的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 模型训练曲线1
def test0_1():
    import numpy as np
    import matplotlib.pyplot as plt

    model_files = ['data/model_0.csv']

    y = []
    for model_file_name in model_files:
        model_loss = []
        with open(model_file_name, 'r') as file:
            for row in file:
                lineArr = row.strip().split(',')
                loss = float(lineArr[1])
                model_loss.append(loss)
        y.append(model_loss)


    y = np.array(y).transpose()
    # plt.figure(figsize=(7, 5))
    x = range(100)
    plt.plot(x, y[:, 0], lw=2,  mec="r", mfc="w", ms=8, )

    plt.grid(True)
    # plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('number of epochs')
    plt.ylabel('loss')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


#模型训练曲线2
def test0_2():
    import numpy as np
    import matplotlib.pyplot as plt

    model_files = ['data/model_10.csv']

    y = []
    for model_file_name in model_files:
        model_loss = []
        with open(model_file_name, 'r') as file:
            for row in file:
                lineArr = row.strip().split(',')
                loss = float(lineArr[1])
                model_loss.append(loss)
        y.append(model_loss)

    y = np.array(y).transpose()
    # plt.figure(figsize=(7, 5))
    x = range(100)
    plt.ylim(0, 100)

    plt.plot(x, y[:, 0], lw=2,  mec="r", mfc="w", ms=8, )
    plt.grid(True)
    plt.axis('tight')
    plt.xlabel('number of epochs')
    plt.ylabel('loss')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# 模型训练曲线3
def test0_3():
    import numpy as np
    import matplotlib.pyplot as plt

    model_files = ['data/model_20.csv']

    y = []
    for model_file_name in model_files:
        model_loss = []
        with open(model_file_name, 'r') as file:
            for row in file:
                lineArr = row.strip().split(',')
                loss = float(lineArr[1])
                model_loss.append(loss)
        y.append(model_loss)

    y = np.array(y).transpose()
    x = range(100)
    plt.plot(x, y[:, 0], lw=2, label='Local NN', mec="r", mfc="w", ms=8, )

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('number of predicates')
    plt.ylabel('q-error')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# 模型训练时间
def test1():
    time = {
        "MSCN": 3837,
        "Local NN": 986,
        "Naru": 1862,
        "MTNN": 1052,
    }
    plt.bar(np.arange(len(time)), list(time.values()), label='training time')
    plt.xticks(np.arange(len(time)), list(time.keys()))
    plt.grid()

    plt.legend()  # 显示图例
    plt.ylabel('training time/s')  # 纵坐标轴标题
    plt.xlabel('model')  # 纵坐标轴标题
    # plt.title('购买饮用水情况的调查结果')  # 图形标题
    plt.show()


# 单表查询估计精度测试
def test2():
    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1000)
    y = [
        [5.2, 8.7, 14.6, 31.4],
        [3.0, 3.8, 5.4, 9.6],
        [2.4, 3.0,  4.7, 7.1],
        [2.2, 3.0, 4.2, 7.5],
        [2.5, 3.4, 4.9, 7.5]
    ]
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    x = ['1', '2', '3', '4']
    plt.plot(x, y[:, 0], lw=2, label='Histogram', marker="d", mec="r", mfc="w", ms=8,)
    plt.plot(x, y[:, 1], lw=2, label='MSCN', marker="o", mec="r", mfc="w", ms=8,)
    plt.plot(x, y[:, 2], lw=2, label='Local NN', marker="^", mec="r", mfc="w", ms=8, )
    plt.plot(x, y[:, 3], lw=2, label='Naru', marker="x", mec="r", mfc="w", ms=8, )
    plt.plot(x, y[:, 4], lw=2, label='MTNN', marker="*", mec="r", mfc="w", ms=8, )

    # plt.xticks(range(0, 2))

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('number of predicates')
    plt.ylabel('q-error')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# scale关于连接数的误差
def test3_1():
    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1000)
    y = [
        [5.5, 17.3, 31.8, 52.6, 88.7],
        [3.5, 6.3, 10.7, 26.9, 50.5],
        [3.8, 10.4, 20.9, 44.7, 85.2],
        [4.2, 6.6, 11.8, 20.4, 35.5]
    ]
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    plt.plot(y[:, 0], lw=2, label='MSCN', marker="d", mec="r", mfc="w", ms=8,)
    plt.plot(y[:, 1], lw=2, label='Local NN', marker="o", mec="r", mfc="w", ms=8,)
    plt.plot(y[:, 2], lw=2, label='Naru', marker="*", mec="r", mfc="w", ms=8, )
    plt.plot(y[:, 3], lw=2, label='MTNN', marker="^", mec="r", mfc="w", ms=8, )

    plt.xticks(range(0, 5))

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('join number')
    plt.ylabel('q-error')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# job关于连接数的误差
def test3_2():
    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1000)

    # [5.5, 17.3, 31.8, 52.6, 88.7],
    # [3.5, 6.3, 12.7, 26.9, 50.5],
    # [3.8, 8.4, 22.9, 44.7, 85.2],
    # [4.2, 6.6, 13.8, 19.4, 34.5]

    y = [
        [21.4, 27.7, 45.6, 81.1],
        [7.2, 15.7, 24.6, 47.5],
        [8.1, 21.9, 41.7, 77.2],
        [9.6, 16.6, 21.1, 30.5]
    ]
    x = ['1', '2', '3', '4']
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    plt.plot(x, y[:, 0], lw=2, label='MSCN', marker="d", mec="r", mfc="w", ms=8,)
    plt.plot(x, y[:, 1], lw=2, label='Local NN', marker="o", mec="r", mfc="w", ms=8,)
    plt.plot(x, y[:, 2], lw=2, label='Naru', marker="*", mec="r", mfc="w", ms=8, )
    plt.plot(x, y[:, 3], lw=2, label='MTNN', marker="^", mec="r", mfc="w", ms=8, )

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('join number')
    plt.ylabel('q-error')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# 模型训练曲线
def test4():
    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1000)
    y = [
        [5.5, 10.3, 26.8, 50.6, 88.7],
        [4.1, 8.1, 16.7, 28.9, 50.5],
        [3.2, 6.3, 10.8, 18.4, 32.5],
    ]
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    plt.plot(y[:, 0], lw=2, label='MSCN', marker="d", mec="r", mfc="w", ms=8,)
    plt.plot(y[:, 1], lw=2, label='Local NN', marker="o", mec="r", mfc="w", ms=8,)
    plt.plot(y[:, 2], lw=2, label='MTNN', marker="^", mec="r", mfc="w", ms=8, )

    plt.xticks(range(0, 5))

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('join number')
    plt.ylabel('q-error')
    plt.title('q-error in scale')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# 模型估计时间
def test5():
    import matplotlib.pyplot as plt
    import numpy as np

    # 输入统计数据
    models = ('MSCN', 'Local NN', 'Naru', 'MTNN')
    synthetic = [23, 14, 26, 15]
    scale = [28, 22, 38, 20]
    job = [29, 27, 42, 21]

    bar_width = 0.2  # 条形宽度
    index_synthetic = np.arange(len(models))
    index_scale = index_synthetic + bar_width
    index_job = index_scale + bar_width

    # 使用两次 bar 函数画出两组条形图
    # alpha:透明度 edgecolor:边框颜色  linestyle:边框样式 linewidth：边框线宽
    # 透明度：alpha=0.8  边框颜色：edgecolor='blue'  边框样式(边框样式为虚线):linestyle='--' 边框线宽: linewidth=1
    plt.bar(index_synthetic, height=synthetic, width=bar_width, color='grey', label='synthetic', hatch='..')
    plt.bar(index_scale, height=scale, width=bar_width, alpha=0.5, color='g', label='scale', hatch='++')
    plt.bar(index_job, height=job, width=bar_width, color='orange', label='JOB-light', hatch='//')

    plt.legend()  # 显示图例
    plt.grid(True)
    plt.xticks(index_synthetic + bar_width / 2, models)
    plt.ylabel('estimate time /ms')  # 纵坐标轴标题

    plt.show()


# scale关于连接数的估计时间
def test6():
    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1000)
    y = [
        [19, 20, 25, 32, 41],
        [9, 13, 20, 29, 39],
        [21, 26, 33, 42, 57],
        [10, 15, 21, 24, 30]
    ]
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    plt.plot(y[:, 0], lw=2, label='MSCN', marker="d", mec="r", mfc="w", ms=8,)
    plt.plot(y[:, 1], lw=2, label='Local NN', marker="o", mec="r", mfc="w", ms=8,)
    plt.plot(y[:, 2], lw=2, label='Naru', marker="*", mec="r", mfc="w", ms=8, )
    plt.plot(y[:, 3], lw=2, label='MTNN', marker="^", mec="r", mfc="w", ms=8, )

    plt.xticks(range(0, 5))

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('join number')
    plt.ylabel('estimate time /ms')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


# job关于连接数的估计时间
def test7():
    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1000)
    y = [
        [20, 29, 34, 43],
        [15, 24, 34, 42],
        [27, 37, 50, 61],
        [16, 26, 29, 33],
    ]
    x = ['1', '2', '3', '4']
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    plt.plot(x, y[:, 0], lw=2, label='MSCN', marker="d", mec="r", mfc="w", ms=8,)
    plt.plot(x, y[:, 1], lw=2, label='Local NN', marker="o", mec="r", mfc="w", ms=8,)
    plt.plot(x, y[:, 2], lw=2, label='Naru', marker="*", mec="r", mfc="w", ms=8, )
    plt.plot(x, y[:, 3], lw=2, label='MTNN', marker="^", mec="r", mfc="w", ms=8, )

    # plt.xticks(range(0, 5))

    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('join number')
    plt.ylabel('estimate time /ms')
    plt.show()
    # plt.savefig("test_3.png", dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    test0_1()
    # test0_2()
    # test0_3()
    # test1()
    # test2()
    # test3_1()
    # test3_2()
    # test5()
    # test6()
    # test7()

