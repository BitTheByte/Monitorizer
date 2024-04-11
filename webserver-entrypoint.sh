#!/usr/bin/env bash
set -e

CORE_COUNT=$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')
WORKERS=${GUNICORN_WORKERS:-$(($CORE_COUNT))}
THREADS=${GUNICORN_THREADS:-$((2 * $WORKERS))}
TIMEOUT=${GUNICORN_TIMEOUT:-500}
KEEPALIVE=${GUNICORN_KEEPALIVE:-300}
SOCKET=unix:/etc/openresty/monitorizer.gunicorn.sock

python3 -m monitorizer.manage migrate
python3 -m monitorizer.configure
python3 -m monitorizer.manage collectstatic --no-input

mkdir -p /var/log/openresty/ /etc/openresty/conf.d/
python3 -m monitorizer.manage openresty_template --gateway $SOCKET > /etc/openresty/conf.d/server.conf

openresty -t
service openresty start
openresty -s reload

gunicorn monitorizer.server.wsgi:application\
  -b $SOCKET\
  --capture-output\
  --enable-stdio-inheritance\
  --workers $WORKERS\
  --threads $THREADS\
  --keep-alive $KEEPALIVE\
  --worker-class gthread\
  --error-logfile '-'\
  --max-requests 20000\
  --timeout $TIMEOUT $@