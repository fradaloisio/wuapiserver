#!/bin/bash
NAME="wuapiserver"
INTERPRETER=python3 
PROGRAM=wuapiserver.py
OPTIONS=
OUTFILE=/dev/null

PIDFILE="/tmp/$NAME.pid"

BASENAME=`basename $0`
PRG_HOME="$(cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
cd "$PRG_HOME"
if [ -f $PIDFILE ]; then
    pid=`cat $PIDFILE`
    PIDEXIST=$([ -n $pid -a -d "/proc/$pid" ] && echo $pid || echo "")
    if [[ "$PIDEXIST" != "" ]]; then
        echo "Running with pid $PIDEXIST"
        exit
    fi
fi

source venv/bin/activate
nohup $INTERPRETER $PROGRAM $OPTIONS &> $OUTFILE &
echo $! > $PIDFILE
