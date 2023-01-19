import matplotlib.pyplot as plt
import numpy as np

# 这两行代码解决 plt 中文显示的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 实验1：谓词数估计精度比较
def test1():
    # 输入统计数据
    est_method = ('直方图', 'MSCN', 'Local NN', 'Naru', 'MTNN')
    predicate1_data = [2.4, 3.2, 2.2, 2.5, 2.2]
    predicate2_data = [8.7, 4.5, 3.8, 3.6, 4.0]
    predicate3_data = [18.6, 7.4, 5.7, 6.9, 6.1]
    predicate4_data = [25.4, 8.6, 7.5, 7.7, 7.5]

    bar_width = 0.2  # 条形宽度
    predicate1_index = np.arange(len(est_method))  # 男生条形图的横坐标
    predicate2_index = predicate1_index + bar_width
    predicate3_index = predicate2_index + bar_width
    predicate4_index = predicate3_index + bar_width

    # 使用两次 bar 函数画出两组条形图
    # alpha:透明度 edgecolor:边框颜色  linestyle:边框样式 linewidth：边框线宽
    # 透明度：alpha=0.8  边框颜色：edgecolor='blue'  边框样式(边框样式为虚线):linestyle='--' 边框线宽: linewidth=1
    plt.bar(predicate1_index, height=predicate1_data, width=bar_width, edgecolor='r', color='#58A399', label='1个谓词', hatch='...')
    plt.bar(predicate2_index, height=predicate2_data, width=bar_width, alpha=0.5, color='#72327B', label='2个谓词', hatch='+++')
    plt.bar(predicate3_index, height=predicate3_data, width=bar_width, color='#C66964', label='3个谓词', hatch='///')
    plt.bar(predicate4_index, height=predicate4_data, width=bar_width, color='#C6921A', label='4个谓词', hatch='xxx')

    plt.legend()  # 显示图例
    plt.xticks(predicate1_index + bar_width*1.5, est_method)  # 让横坐标轴刻度显示 waters 里的饮用水， index_male + bar_width/2 为横坐标轴刻度的位置
    plt.ylabel('q-error')  # 纵坐标轴标题
    plt.title('几种估计方法的q-error比较')  # 图形标题

    plt.show()
    return


# 实验1：谓词数估计精度比较
def test2():
    return


# 实验1：谓词数估计精度比较
def test3():
    return


if __name__ == "__main__":
    test1()
    # test2()
    # test3()

