#!/bin/bash
source ../pinax/bin/activate
kill `cat /home/www/var/run/myewb/myewb.pid`
export MALLOC_CHECK_=0
python manage.py runfcgi socket=/home/www/var/run/myewb/myewb errlog=/home/myewb2/myewb/errors.log outlog=/home/myewb2/myewb/out.log pidfile=/home/www/var/run/myewb/myewb.pid maxrequests=100
chmod 777 /home/www/var/run/myewb/myewb

