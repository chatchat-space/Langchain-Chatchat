import queue
import time
import threading


class DelayQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.lock = threading.Lock()

    def add_task(self, task, delay):
        execute_time = time.time() + delay
        self.queue.put((execute_time, task))

    def worker(self):
        while True:
            with self.lock:
                if self.queue.empty():
                    time.sleep(1)
                    continue
                execute_time, task = self.queue.get()
                now = time.time()
                if execute_time > now:
                    time.sleep(execute_time - now)
                task()
                self.queue.task_done()

    def start(self):
        thread = threading.Thread(target=self.worker)
        thread.start()


# 使用示例
def my_task1():
    print("1")


def my_task2():
    print("2")


def my_task3():
    print("3")


if __name__ == '__main__':
    dq = DelayQueue()
    dq.add_task(my_task3, 3)  # 任务将在5秒后执行
    dq.add_task(my_task2, 2)  # 任务将在5秒后执行
    dq.add_task(my_task1, 1)  # 任务将在5秒后执行
    dq.start()
