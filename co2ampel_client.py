
# co2ampel_client.py

"""

Taken from docs at https://pypi.org/project/paho-mqtt 

Todo: logging (journalctl)
      error handling (influxdb.exceptions.InfluxDBClientError: 400: {"error":"partial write: field type conflict...)
       
Last update: 2021-04-08, hhoegl

Output: 

Connected with result code 0
fr_co2ampel_hft/devices/co2ampelbndlg_dev01/up
b'{"app_id":"fr_co2ampel_hft","dev_id":"co2ampelbndlg_dev01","hardware_serial":"1111111111111111","port":1,"counter":256,"payload_raw":"M5BK","payload_fields":{"co2":1020,"hum":37,"tmp":18.8},"metadata":{"time":"2021-03-20T16:20:00.461870801Z","frequency":868.1,"modulation":"LORA","data_rate":"SF7BW125","airtime":51456000,"coding_rate":"4/5","gateways":[{"gtw_id":"eui-58a0cbfffe80130d","timestamp":3840645035,"time":"2021-03-20T16:20:00.207355022Z","channel":0,"rssi":-79,"snr":10,"rf_chain":0}]}}'

...

Sample InfluxDB query:

influx -execute 'select * from "franz-co2"' --database="loradb" -precision=rfc3339

Output looks like

2021-04-22T20:29:58.091392Z    940  38   20.8
2021-04-22T20:35:07.200516864Z 920  38   20.8
2021-04-22T20:40:16.419217152Z 920  38   20.8
2021-04-22T20:45:25.828901888Z 900  38   20.8
2021-04-22T20:50:35.21579904Z  900  38   20.8
2021-04-22T20:55:44.515228928Z 880  38   20.8
2021-04-22T21:00:53.82912Z     880  38   20.6
2021-04-22T21:06:03.18772608Z  880  38   20.6
2021-04-22T21:11:12.480773888Z 860  38   20.6
2021-04-22T21:16:21.386727936Z 860  37.5 20.6
2021-04-22T21:21:30.431068928Z 840  38   20.6
...


"""

import os
import json
from influxdb import InfluxDBClient

# Eclipse Paho MQTT Python client library (install with "pip install paho-mqtt")
import paho.mqtt.client as mqtt

client_name = "client1"

# APPID
user = "fr_co2ampel_hft"

# APPKEY/ACCESS_KEY (set environment variable: export TTNPASSWD=...)
password = os.environ["TTNPASSWD"] 

topic = "+/devices/+/up"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic, qos=0)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    # topic: fr_co2ampel_hft/devices/co2ampelbndlg_dev01/up
    # print("topic:", msg.topic)

    # <class 'paho.mqtt.client.MQTTMessage'> <paho.mqtt.client.MQTTMessage object at 0xb63ad2b0>
    #print(type(msg), msg)

    # <class 'bytes'>
    #print(type(msg.payload), msg.payload)
    ps = msg.payload.decode('ascii')
    j = json.loads(ps)
    # print(j['metadata']['time'], j['payload_fields'])
    pf = j['payload_fields']
    # [{'measurement': 'franz-co2', 'time': '2021-04-08T16:01:48.206104336Z', 'fields': {'co2': 900, 'hum': 33.5, 'tmp': 19.6}}]

    co2 = pf['co2']  # int (float?)
    hum = pf['hum']  # can change int or float, influxdb need a fixed type (= type of first data write)
    tmp = pf['tmp']  # can change between int or float 
    D = { "measurement": "franz-co2",
          "time": j['metadata']['time'],
          "fields": { 'co2': float(co2), 'hum': float(hum), 'tmp': float(tmp) }}  # force all field to float
    print([D])
    inflx.write_points([D])


if __name__ == "__main__":
    inflx = InfluxDBClient(host='localhost', port=8086, username='root', 
                                 password='root', database='loradb')
    inflx.create_database('loradb')

    client = mqtt.Client(client_name)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(user, password)
    client.connect("eu.thethings.network")
    client.loop_forever()
