#!/bin/bash
PIDFILE="/tmp/$NAME.pid"
if [ -f $PIDFILE ]; then
    PID=`cat $PIDFILE`
    echo "Stopping PID $PID"
    kill $PID && \
    while [ -e /proc/$PID ]; do sleep 0.1; done && \
    echo "stopped."
    rm -f $PIDFILE
else
    echo "no $PID_FILE file found, stop ignored."
fi
