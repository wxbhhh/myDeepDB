
# 折线图
def load1():
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


# 柱状图
def load2():
    import matplotlib.pyplot as plt
    import numpy as np

    # 这两行代码解决 plt 中文显示的问题
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 输入统计数据
    waters = ('碳酸饮料', '绿茶', '矿泉水', '果汁', '其他')
    buy_number_male = [6, 7, 6, 1, 2]
    buy_number_female = [9, 4, 4, 5, 6]
    buy_number_avg = [12, 11, 7, 9, 5]
    buy_number_avg2 = [6, 1, 4, 3, 7]


    bar_width = 0.2  # 条形宽度
    index_male = np.arange(len(waters))  # 男生条形图的横坐标
    index_female = index_male + bar_width  # 女生条形图的横坐标
    index_avg = index_female + bar_width  # 女生条形图的横坐标
    index_avg2 = index_avg + bar_width  # 女生条形图的横坐标

    # 使用两次 bar 函数画出两组条形图
    # alpha:透明度 edgecolor:边框颜色  linestyle:边框样式 linewidth：边框线宽
    # 透明度：alpha=0.8  边框颜色：edgecolor='blue'  边框样式(边框样式为虚线):linestyle='--' 边框线宽: linewidth=1
    plt.bar(index_male, height=buy_number_male, width=bar_width, edgecolor='r', color='b', label='男性', hatch='....')
    plt.bar(index_female, height=buy_number_female, width=bar_width, alpha=0.5, color='g', label='女性', hatch='+++')
    plt.bar(index_avg, height=buy_number_avg, width=bar_width, color='r', label='平均', hatch='////')
    plt.bar(index_avg2, height=buy_number_avg2, width=bar_width, color='y', label='平均2', hatch='xxx')


    plt.legend()  # 显示图例
    plt.xticks(index_male + bar_width / 2, waters)  # 让横坐标轴刻度显示 waters 里的饮用水， index_male + bar_width/2 为横坐标轴刻度的位置
    plt.ylabel('购买量')  # 纵坐标轴标题
    plt.title('购买饮用水情况的调查结果')  # 图形标题

    plt.show()


# 箱线图
def load3():
    import matplotlib.pyplot as plt
    import numpy as np

    # x = np.random.randint(10, 100, size=(5, 4))  # 随机生成5行9列 [10, 100]之间的数

    x = list("ABCD")

    y = [
        [63, 12, 10, 71, 91],
        [49, 60, 45, 23, 70],
        [70, 23, 10, 92, 65],
        [79, 65, 51, 82, 81],
    ]

    y = np.array(y).transpose()

    '''
    关键参数含义说明如下： 
    y：指定要绘制箱线图的数据，可以是一组数据也可以是多组数据；
    notch：是否以凹口的形式展现箱线图，默认非凹口；
    sym：指定异常点的形状，默认为蓝色的+号显示；
    vert：是否需要将箱线图垂直摆放，默认垂直摆放；
    whis：指定上下须与上下四分位的距离，默认为1.5倍的四分位差；
    positions：指定箱线图的位置，默认为range(1, N+1)，N为箱线图的数量；
    widths：指定箱线图的宽度，默认为0.5；
    patch_artist：是否填充箱体的颜色，默认为False；
    meanline：是否用线的形式表示均值，默认用点来表示；
    showmeans：是否显示均值，默认不显示；
    showcaps：是否显示箱线图顶端和末端的两条线，默认显示；
    showbox：是否显示箱线图的箱体，默认显示；
    showfliers：是否显示异常值，默认显示；
    boxprops：设置箱体的属性，如边框色，填充色等；
    labels：为箱线图添加标签，类似于图例的作用；
    filerprops：设置异常值的属性，如异常点的形状、大小、填充色等；
    medianprops：设置中位数的属性，如线的类型、粗细等；
    meanprops：设置均值的属性，如点的大小、颜色等；
    capprops：设置箱线图顶端和末端线条的属性，如颜色、粗细等；
    whiskerprops：设置须的属性，如颜色、粗细、线的类型等；
    manage_ticks：是否自适应标签位置，默认为True；
    autorange：是否自动调整范围，默认为False；
    '''

    plt.grid(True)
    plt.xlabel('join number')
    plt.ylabel('q-error')
    plt.title('q-error in scale')

    #plt.title('几种模型误差分析')  # 图形标题
    plt.boxplot(y, labels=x, sym="r+", patch_artist='b',
                showmeans=False, medianprops={'linewidth':3},
                )  # 绘制箱线图
    plt.show()  # 显示图片


# 双y轴
def load4():
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.arange(0., np.e, 0.01)
    y1 = np.exp(-x)
    y2 = np.log(x)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, y1, 'r', label="right");
    ax1.legend(loc=1)
    ax1.set_ylabel('Y values for exp(-x)');
    ax2 = ax1.twinx()  # this is the important function
    ax2.plot(x, y2, 'g', label="left")
    ax2.legend(loc=2)
    ax2.set_xlim([0, np.e]);
    ax2.set_ylabel('Y values for ln(x)');
    ax2.set_xlabel('Same X for both exp(-x) and ln(x)')
    plt.show()


# 横向柱状图
def load5():
    import matplotlib
    import random
    import matplotlib.pyplot as plt

    # 城市数据。
    city_name = ['北京', '上海', '广州', '深圳', '成都']

    # 数组反转。
    city_name.reverse()

    # 装载随机数据。
    data = []
    for i in range(len(city_name)):
        data.append(random.randint(100, 150))

    # 绘图。
    fig, ax = plt.subplots()
    b = ax.barh(range(len(city_name)), data, color='#6699CC')

    # 为横向水平的柱图右侧添加数据标签。
    for rect in b:
        w = rect.get_width()
        ax.text(w, rect.get_y() + rect.get_height() / 2, '%d' %
                int(w), ha='left', va='center')

    # 设置Y轴纵坐标上的刻度线标签。
    ax.set_yticks(range(len(city_name)))
    ax.set_yticklabels(city_name)

    # 不要X横坐标上的label标签。
    plt.xticks(())

    plt.title('水平横向的柱状图', loc='center', fontsize='25',
              fontweight='bold', color='red')
    plt.show()


# 纵向堆叠的柱状图
def load6():
    import numpy as np
    import matplotlib.pyplot as plt
    a1 = [23, 14, 26, 15]
    a2 = [28, 22, 38, 20]
    a3 = [29, 27, 42, 21]

    x = np.arange(len(a1))
    a = [x + y + z for x, y, z in zip(a1, a2, a3)]
    plt.bar(x, a1, color='tab:blue', label="species 1")
    plt.bar(x, a2, color='tab:orange', label="species 2", bottom=a1)   #bottom = a1 表示a2对应的柱子以a1的柱子的顶端为起始点
    plt.bar(x, a3, color='tab:green', label="species 3", bottom=[x + y for x, y in zip(a1, a2)])  # bottom = a1 表示a2对应的柱子以a1的柱子的顶端为起始点

    ax = plt.gca()
    tt = ['gene 1', 'gene 2', 'gene 3', 'gene 4']
    ax.set_xticks(x)
    ax.set_xticklabels(tt, rotation = 45)
    # ax.set_yticks([0, 100, 200, 300])
    ax.set_xlabel("Related genes")
    ax.set_ylabel("The amount of diseases")
    ax.set_title("The relationship between genes and diseases")
    plt.legend(loc = 0) #显示图例
    plt.show()

if __name__ == "__main__":
    load6()
