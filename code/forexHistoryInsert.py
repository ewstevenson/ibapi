#!/usr/bin/python3
import numpy as np
import sys
import mysql.connector

config = {
    'user': 'ibapi',
    'password': 'password',
    'host': '127.0.0.1',
}

mysqlDB = 'historicData'
mysqlTable = 'USDJPY'

conn = mysql.connector.connect(**config)
cur = conn.cursor(buffered=True)
cur.execute("SHOW DATABASES;")
print(cur.fetchone())
cur.close()
conn.close()

sql = 'INSERT INTO `USDJPY` ( `date`, `open`, `high`, `low`, `close`, `volume` `count` `wap`, `hasGaps` ) VALUES ( date, open, high, low, close, volume, barCount, WAP, hasGaps )' 




#r = np.core.records.fromrecords([(456,'dbe',1.2),(2,'de',1.3)],names='col1,col2,col3')
#print(r[0])
