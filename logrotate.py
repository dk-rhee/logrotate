#!/usr/bin/env python

import configparser
from datetime import datetime, timedelta
import gzip
import os
import schedule
import shutil
import subprocess
import time

# CONFIG_PATH = '/etc/oops'
# CONFIG_FILE = 'logrotate.conf'
LOG_PATH = '/var/log/remote/192.168.0.1'
# LOG_FILE = 'logrotate.log'
SERVICE = 'rsyslog'

# 대상 로그 파일 확보
def get_logfiles(path):
    res = []
    for root, dirs, files in os.walk(path):
        rootpath = os.path.join(os.path.abspath(path), root)

        for f in files:
            filepath = os.path.join(rootpath, f)
            if filepath.endswith('.log'):
                res.append(filepath)
    return res


def restart_syslogd():
    try:
        cmd = '/bin/systemctl restart {}.service'.format(SERVICE)
        completed = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)


def do_job():
    res = get_logfiles(LOG_PATH)
    date = (datetime.now() + timedelta(days=-1)).strftime('%Y%m%d')
    for log in res:
        log_to = log+'-'+date
        os.rename(log, log_to)
        with open(log_to, 'rb') as f_in:
            with gzip.open(log_to+'.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(log_to)
    
    restart_syslogd()


def main():
    schedule.every().day.at("00:00").do(do_job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
