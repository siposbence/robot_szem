import paho.mqtt.client as mqtt
import os

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("$SYS/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "start":
      os.system("bash /home/pi/robot_szem/start_left.sh")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.73", 1883, 60)

client.loop_forever()
