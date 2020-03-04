# #!/usr/bin/env python
# # coding: utf-8

import threading
import time
import click 

@click.command () 
@click.option ('--count', default=1, help = 'Number of greetings.') 
@click.option('--name', prompt = ' Your name ', help= 'The person to greet.') 
def hello(count, name) :
    '''Simple program that greets NAME for a total of COUNT times .''' 
    for x in range(count): 
        click.echo(' Hello %s ！' %name) 
         
class Job(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True
        self.data = "init-value"

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            print ("%f = %s " % (time.time(), self.data))
            time.sleep(1)
            self.pause()
            
    def setdata(self, data):
      self.data = data

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False

if __name__ == '__main__':
# if name == 'main': 
    hello ()


# # hello.py
# # import click
# @click.command()
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
# def hello(count, name):
#     """Simple program that greets NAME for a total of COUNT times."""
#     for x in range(count):
#         click.echo('Hello %s!' % name)
# if __name__ == '__main__':
#     hello()
    