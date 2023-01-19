import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib as mpl


def load():

    plt.rcParams['font.sans-serif'] = ['FangSong']
    plt.rcParams['axes.unicode_minus'] = False

    bar1 = [4, 5, 6, 8, 7]
    bar2 = [7, 6, 2, 5, 4]
    labels = ['小明', '小张', '小洪', '小红', '小铭']
    bar_width = 0.35

    plt.bar(np.arange(5)-0.5*bar_width, bar1, label='第一次',
            width=bar_width, color='#58C9B9')
    plt.bar(np.arange(5)+0.5*bar_width, bar2, label='第二次',
            width=bar_width, color='#519D9E')
    plt.xlabel('人名', fontsize=15)
    plt.ylabel('数量', fontsize=15)
    plt.title('数量统计', fontsize=18)
    plt.ylim([0, 10])
    plt.legend()
    plt.xticks(np.arange(5), labels, fontsize=13)
    plt.box(False)
    plt.grid(color='0.4', axis='y', linestyle='solid', alpha=0.1)

    for i, j in enumerate(bar1):
        plt.text(i-0.5*bar_width-0.05, j+0.1, str(j))

    for i, j in enumerate(bar2):
        plt.text(i+0.5*bar_width-0.05, j+0.1, str(j))

    # plt.savefig('fig.pdf', bbox_inches='tight')
    plt.show()


def load2():
    np.random.seed(1000)
    y = [
        [5.5, 10.3, 26.8, 50.6, 88.7],
        [4.1, 8.1, 16.7, 28.9, 50.5],
        [3.2, 6.3, 10.8, 18.4, 32.5],
    ]
    y = np.array(y).transpose()
    plt.figure(figsize=(7, 5))
    plt.plot(y[:, 0], lw=2, label='MSCN')
    plt.plot(y[:, 1], lw=2, label='Local NN')
    plt.plot(y[:, 2], lw=2, label='MTNN')

    plt.xticks(range(0, 5))

    plt.plot(y, 'ro')
    plt.grid(True)
    plt.legend(loc=0)  # 图例位置自动
    plt.axis('tight')
    plt.xlabel('join number')
    plt.ylabel('q-error')
    plt.title('q-error in scale')
    plt.show()


if __name__ == "__main__":
    load2()

