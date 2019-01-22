#!/bin/sh
if [ -f "/data/ejbcadb.h2.db" ]; then
    echo "DB ok"
    rm /data/ejbcadb.h2.lock
else
    cp /root/ejbcadb.h2.db /data/
fi

/opt/jboss-as-7.1.1.Final/bin/standalone.sh -b 127.0.0.1 &
python3 /var/www/RESTmain.py
