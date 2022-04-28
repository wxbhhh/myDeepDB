import threading
import time
from queue import Queue


def do_something(num=1):
    print("-> 线程启动")
    time.sleep(num)
    print("-> 线程结束")


def test1():
    start = time.perf_counter()
    do_something()
    finish = time.perf_counter()
    print(f"全部任务执行完成，耗时 {round(finish - start, 2)} 秒")


def test2():
    start = time.perf_counter()
    thread1 = threading.Thread(target=do_something, args=[3])
    thread2 = threading.Thread(target=do_something, args=[2])

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    finish = time.perf_counter()

    print(f"全部任务执行完成，耗时 {round(finish - start, 2)} 秒")


# 循环创建线程
def test3():
    thread_list = []
    start = time.perf_counter()
    for i in range(1, 11):
        thread = threading.Thread(target=do_something, args=[i])
        thread.start()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    finish = time.perf_counter()

    print(f"全部任务执行完成，耗时 {round(finish - start, 2)} 秒")


lock = threading.Lock()

test4Result = []


def test4Mission(insertNum):
    #lock.acquire()
    print("-> 线程启动")
    time.sleep(0.05)
    test4Result.append(insertNum)
    print("-> 线程结束")
    #lock.release()


# 共享变量锁
def test4():
    thread_list = []
    start = time.perf_counter()
    for i in range(1, 11):
        thread = threading.Thread(target=test4Mission, args=[i])
        thread.start()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    finish = time.perf_counter()

    print(f"全部任务执行完成，耗时 {round(finish - start, 2)} 秒")
    print(test4Result)


test5Result = []


def test5Mission(insertNum):
    lock.acquire()
    print("-> 线程启动")
    time.sleep(0.05)
    test4Result.append(insertNum)
    print("-> 线程结束")
    lock.release()

# 限制线程数量(存在问题)
def test5():
    thread_list = []
    max_thread = 13
    threadPool = threading.BoundedSemaphore(max_thread)
    start = time.perf_counter()
    for i in range(1, 11):
        threadPool.acquire()
        thread = threading.Thread(target=test4Mission, args=[i])
        thread.start()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    finish = time.perf_counter()

    print(f"全部任务执行完成，耗时 {round(finish - start, 2)} 秒")
    print(test4Result)

queue = Queue()

# 定义需要线程池执行的任务
def do_job():
    while True:
        i = queue.get()
        time.sleep(1)
        print('index %s, curent: %s' % (i, threading.current_thread()) )
        queue.task_done()
def test7():
    queue.put(10)
    queue.put(12)
    queue.put(13)
    # 创建包括3个线程的线程池
    for i in range(3):
        t = threading.Thread(target=do_job)
        # 设置线程daemon 主线程退出，daemon线程也会推出，即时正在运行
        t.daemon = True
        t.start()
    # 模拟创建线程池3秒后塞进10个任务到队列
    time.sleep(3)
    for i in range(10):
        queue.put(i)
    queue.join()


g_num = 1
def work1():
    global g_num
    print('before add in work1 g_num is : %d' % g_num)
    for i in range(3):
        g_num += 1
        print('after add in work1 g_num is : %d' % g_num)
def work2():
    global g_num
    print('in work2 g_num is : %d' % g_num)
def test6():
    t1 = threading.Thread(target=work1)
    t1.start()
    time.sleep(1)
    t2 = threading.Thread(target=work2)
    t2.start()


if __name__ == "__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    test7()
