from crontab import CronTab
 
my_cron = CronTab(user='sergiolluva')
job = my_cron.new(command='python3 /home/sergiolluva/flaskapp/app/run.py')
job.minute.every(2)
my_cron.write()
