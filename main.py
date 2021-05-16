from marshmallow_schemas import InternalHistorySchema, PublicHistorySchema, PublicUpdatesSchema, ApiAlarmSchema
from flask import Flask, jsonify, request, abort
import requests
import json
from model import ApiAlarm
from typing import List
from datetime import datetime

app = Flask(__name__)

@app.route("/internal/alarms/last_day")
def get_internal_alarms():
    res = requests.get('https://www.oref.org.il/WarningMessages/History/AlertsHistory.json')
        
    res_text = str(res.content, 'utf-8')

    schema = InternalHistorySchema(many=True)
    result = schema.loads(res_text)
    
    api_alarms: List[ApiAlarm] = []

    if result:
        for item in result:
            api_alarms.append(ApiAlarm(item['data'], item['alertDate']))

    return ApiAlarmSchema().dumps(api_alarms, many=True)

@app.route("/public/alarms")
def get_public_alarms():
    oref_mode: int = 0
    oref_url = 'https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=' + str(oref_mode)
    mode = request.args.get('mode')
    if mode:
        if mode == "day":
            oref_mode = 1
        elif mode == "week":
            oref_mode = 2
        elif mode == "month":
            oref_mode = 3
        elif mode == "custom":
            start_day_filter = request.args.get('from')
            end_day_filter = request.args.get('to')
            if start_day_filter and end_day_filter:
                oref_url = oref_url + '&fromDate=' + start_day_filter + '&toDate=' + end_day_filter
            else:
                return abort(400, "Missing query parameters")
        else:
            return abort(400, ("Received mode is not supported"))

    res = requests.get(oref_url)
    res_text = str(res.content, 'utf-8')

    schema = PublicHistorySchema(many=True)
    result = schema.loads(res_text)

    api_alarms: List[ApiAlarm] = []

    if result:
        for item in result:
            api_alarms.append(ApiAlarm(item['data'], item['datetime']))

    return ApiAlarmSchema().dumps(api_alarms, many=True)


@app.route("/public/alarms/updates")
def get_public_alarm_updates():
    headers = {
        "Host": 'www.oref.org.il',
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0',
        "Accept": 'text/plain, */*; q=0.01',
        "Accept-Language": 'en-US,en;q=0.5',
        "Accept-Encoding": 'gzip, deflate, br',
        "Content-Type": 'application/x-www-form-urlencoded; charset=UTF-8',
        "X-Requested-With": 'XMLHttpRequest',
        "Connection": 'keep-alive',
        "Referer": 'https://www.oref.org.il/12481-he/Pakar.aspx',
        "Cookie": 'Lastalerts=; pakar_sound_unmute=0; __atuvc=2%7C19; __atssc=google%3B2; zdSessionId_07713213=9fbc33e5-d218-49c1-9309-197476af21bc; _ga=GA1.3.2058383389.1620770162; _gid=GA1.3.2076676584.1620770162; _hjTLDTest=1; _hjid=cf2784f9-328d-458d-ae6e-a618b8aa59d2; _fbp=fb.2.1620770162505.301675791; TS013a1194=010f83961d2fc8c1a7728bbe076790ac6a6b033921bd82bbc9006c903c6762041ea8bf14b2615365eabcbc60ebf6b00d24a507944f35bbd38741b6faa5043653a54e5de153; ASP.NET_SessionId=40cfcvezmixc3sgbxef4huoe',
    }

    res = requests.get('https://www.oref.org.il/WarningMessages/alert/alerts.json', headers=headers)

    res_text = str(res.content, 'utf-8')

    if res_text != '':
        schema = PublicUpdatesSchema(many=True)
        result = schema.loads(res_text)
    
        api_alarms: List[ApiAlarm] = []

        if result:
            for item in result:
                for data in item['data']:
                    api_alarms.append(ApiAlarm(data, datetime.now()))

        return ApiAlarmSchema().dumps(api_alarms, many=True)

    return jsonify(res_text if res_text else None)
    
app.run(port=5005)