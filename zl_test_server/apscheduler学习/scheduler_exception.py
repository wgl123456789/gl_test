from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR
from datetime import datetime,timedelta
from apscheduler.events import JobExecutionEvent
import logging

# 配置日志显示
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='scheduler_log.txt',
                    filemode='a')

def normal_task():
    print("我是正在运行的正常任务！")

def error_task():
    print("我是一个会抛出异常的任务！")
    print(1/0)

def error_listener(event):
    if event.exception:
        print("抛出异常了！")
        print(event.traceback)
    else:
        print("正常执行！")

scheduler = BlockingScheduler()
scheduler.add_job(error_task,next_run_time=datetime.now()+timedelta(seconds=2))
scheduler.add_job(normal_task,trigger="interval",seconds=3)

# | 或操作：10 | 01 = 11
scheduler.add_listener(error_listener,EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

scheduler._logger = logging

scheduler.start()