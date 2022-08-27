
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

def my_clock():
    print("Hello! The time is:%s"%datetime.now())

def date_trigger():
    scheduler = BlockingScheduler()
    scheduler.add_job(my_clock, "date", run_date=datetime(2020,5,26,15,25))
    scheduler.start()

def interval_trigger():
    scheduler = BlockingScheduler()
    scheduler.add_job(my_clock,"interval",seconds=2)
    scheduler.start()

def cron_trigger():
    scheduler = BlockingScheduler()
    scheduler.add_job(my_clock, "cron", second="10-20/2,40-59/2")
    scheduler.start()

if __name__ == '__main__':
    # date_trigger()
    cron_trigger()