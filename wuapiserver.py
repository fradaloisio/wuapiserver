
'''
/weatherstation/updateweatherstation.php?ID=Stazione&PASSWORD=1234&action=updateraww&realtime=1&rtfreq=5&dateutc=now&baromin=29.82&tempf=66.3&humidity=65&windspeedmph=0&windgustmph=0&winddir=140&dewptf=54.1&rainin=0&dailyrainin=0.03&UV=1.8

'date': DD/MM/YYYY: [0]
'ora': HH:MM:SS: [1]
'tempf': [2]
'humidity': [3]
'dewptf': [4]
'windspeedmph': [5]
'winddir': [7]
'rainin': [8] 
'dailyrainin': [9]
'baromin': [10]
'tempmax': [26]
'tempmin': [28]
'windgustmph': [40]
'UV': [43]

https://martinezwebmaster.altervista.org/WP/archives/215
http://www.laconimeteo.it/santasofia/MBrealtime.txt

'''
import json
import sqlite3
import datetime
import logging
import os
from flask import Flask, request, send_from_directory

logging.basicConfig(filename="wuapiserver.log",format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

mbfolder = "./mb/"
if not os.path.exists(mbfolder):
    os.makedirs(mbfolder)
app = Flask(__name__, static_folder='')
out = ""
db = "wuapiserver.db"


def check_db():
    logging.info("checking db")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(''' create table if not exists temperatures(datetime date, tempf real, stationid text) ''')
    conn.commit()
    c.execute(''' create table if not exists rainmonth(datetime date, rain real, stationid text) ''')
    conn.commit()
    c.execute(''' create table if not exists rainyear(datetime date, rain real, stationid text) ''')
    conn.commit()
    conn.close()

def clean_db():
    logging.info("cleaning db")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    today = str(datetime.datetime.now().strftime('%Y-%m-%d'))
    q = 'delete from temperatures where datetime < "'+ today+'"'
    c.execute(q)
    conn.commit()
    conn.close()

@app.route('/weatherstation/mb/<path:path>')
def send_mb(path):
    return send_from_directory(mbfolder, path)

@app.route('/weatherstation/updateweatherstation.php')
def init():
    logging.info("request received" )

    p = request.args.to_dict()
    if p['date'] == 'now':
        p['date'] = str(datetime.datetime.now().replace(microsecond=0).strftime('%m/%d/%YT%H:%M:%S'))

    p['tempf'] = str(round(((float(p['tempf'])-32)/1.8),1))
    p['dewptf'] = str(round(((float(p['dewptf'])-32)/1.8),1))
    p['windspeedmph'] = str(round((float(p['windspeedmph'])*1.609),1))
    p['windgustmph'] = str(round((float(p['windgustmph'])*1.609),1))
    p['rainin'] = str(round((float(p['rainin'])*25.4),1))
    p['dailyrainin'] = str(round((float(p['dailyrainin'])*25.4),1))
    p['baromin'] = str(round((float(p['baromin'])*33.864),1))

    MB = ["--"] * 66
    MB[0] = str(p['date']).split("T")[0]
    MB[1] = str(p['date']).split("T")[1]
    MB[2] = p['tempf']
    MB[3] = p['humidity']
    MB[4] = p['dewptf']
    MB[5] = p['windspeedmph']
    MB[7] = p['winddir']
    MB[8] = p['rainin']
    MB[9] = p['dailyrainin']
    MB[10] = p['baromin']
    MB[40] = p['windgustmph']
    MB[43] = p['UV']


    conn = sqlite3.connect(db)
    conn.set_trace_callback(print) # debug query
    c = conn.cursor()
    
    d = datetime.datetime.strptime(p['date'],'%m/%d/%YT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
    c.execute(''' INSERT INTO temperatures VALUES (?,?,?) ''', (str(d),float(p['tempf']),str(p['ID'])))
    conn.commit()

    c.execute(''' INSERT INTO rainmonth VALUES (?,?,?) ''', (str(d),float(p['dailyrainin']),str(p['ID'])))
    c.execute(''' DELETE FROM rainmonth where datetime != ? and stationid == ?''', (str(d),str(p['ID'])))
    conn.commit()

    c.execute(''' select sum(rain) from rainmonth where stationid == ? AND datetime >= ? ''', (p['ID'],d.split("T")[0]))
    r = c.fetchone()
    print("------------ " + str(r[0]))
    MB[19] = str(r[0])
    #MB[20] = p['rainyr']


    c.execute(''' select min(tempf), max(tempf) from temperatures where stationid == ? AND datetime BETWEEN ? AND ? ''', (p['ID'],d.split("T")[0]+"T00:00:00",d.split("T")[0]+"T23:59:59"))
    r = c.fetchone()
    conn.close()

    MB[26] = "--"if str(r[1]) == "None" else str(r[1]) 
    MB[28] = "--"if str(r[0]) == "None" else str(r[0]) 

    outputfile = out if out != "" else str(p['ID'])+".txt"
    outputfile = mbfolder+outputfile
    f = open(outputfile,'w')
    f.write(' '.join(MB))
    f.close()

    logging.info(' '.join(MB))

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


if __name__ == "__main__":
    check_db()
    clean_db()
    app.run(host='127.0.0.1', port=5000)