import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time
import threading
import numpy as np
import cv2
import base64
root = dict()
root["name"] = "lyz"
MQTT_URL = '127.0.0.1'

def warning():
    root = dict()
    root['str'] = 'this is a warning!'
    while True:
        root['type'] = int(np.random.rand(1)[0]*100)
        s = json.dumps(root)
        publish.single('warning', payload=s, hostname=MQTT_URL)
        time.sleep(4)


def numQueue():
    root = dict()
    while True:
        root['numOfQueue'] = int(np.random.rand(1)[0]*100)
        s = json.dumps(root)
        publish.single('numQueue', payload=s, hostname=MQTT_URL)
        time.sleep(4)

def mostStandingTime():
    root = dict()
    while True:
        root['mostStaningTime'] = int(np.random.rand(1)[0]*100)
        s = json.dumps(root)
        publish.single('mostStaningTime', payload=s, hostname=MQTT_URL)
        time.sleep(4)


def crossRegion():
    root = dict()
    root['numArea'] = 3
    while True:
        tmp = list(np.random.rand(root['numArea']*root['numArea'])*100)
        tmp = [int(i) for i in tmp]
        root['flow'] = tmp
        s = json.dumps(root)
        publish.single('crossRegion', payload=s, hostname=MQTT_URL)
        time.sleep(4)

def genderRate():
    root = dict()
    root['male'] = 0
    root['female'] = 0

    while True:
        time.sleep(5)
        x = np.random.rand(2)*100
        root['男性'] = int(x[0])
        root['女性'] = int(x[1])
        s = json.dumps(root)
        publish.single('genderRate', payload=s, hostname=MQTT_URL)

def latestDay():
    root = dict()
    root['population'] = []
    population = []
    while True:
        time.sleep(7)
        x = int(np.random.rand(1)[0] * 100)
        population.append(x)
        population = population[-9:]
        root['population'] = population
        s = json.dumps(root)
        publish.single('latestday', payload=s, hostname=MQTT_URL)


def faceAttr():
    pass

def abnormal():
    root = dict()
    p = '/media/img/'
    imgs = ['knife.png', 'razor.png', 'sword.png']
    while True:
        idx = int(np.random.rand(1)[0] * 100)%3
        root['name'] = imgs[idx].split('.')[0]
        mat = cv2.imread(p+imgs[idx])
        mat = cv2.resize(mat, (50, 50))
        string = base64.b64encode(cv2.imencode('.jpg', mat)[1]).decode()
        publish.single('abnormal', payload=string, hostname=MQTT_URL)
        time.sleep(5)


def leftover():
    root = dict()
    p = '/media/img/'
    imgs = ['knife.png', 'razor.png', 'sword.png']
    while True:
        idx = int(np.random.rand(1)[0] * 100)%3
        root['name'] = imgs[idx].split('.')[0]
        mat = cv2.imread(p+imgs[idx])
        mat = cv2.resize(mat, (50, 50))
        string = base64.b64encode(cv2.imencode('.jpg', mat)[1]).decode()
        publish.single('abnormal', payload=string, hostname=MQTT_URL)
        time.sleep(5)

def managerStatus():
    sta = ['在岗','暂离','离岗']
    while True:
        idx = int(np.random.rand(1)[0] * 100) % 3
        root['status'] = sta[idx]
        s = json.dumps(root)
        publish.single('leftover', payload=s, hostname=MQTT_URL)
        time.sleep(5)

def numRegion():
    root = dict()
    while True:
        root['infos'] = []
        for i in range(3):
            tmp = list(np.random.rand(3)*100)
            tmp = [int(i) for i in tmp]
            sub = dict()
            sub['name'] = 'region' + str(tmp[0]%3)
            sub['numPerson'] = tmp[1]
            sub['avgStayTime'] = tmp[2]
            root['infos'].append(sub)

        s = json.dumps(root)
        publish.single('numRegion', payload=s, hostname=MQTT_URL)
        time.sleep(4)

'''
{
    "name" : "",
    "age": 20
}
'''
# def infos():
#     root = dict()
#     names = ["Amy", 'Bob', 'mike', 'Jake', 'Jack', 'Honey', 'Apple', 'Orange']
#     while True:
#         time.sleep(2)
#         x = int(np.random.rand(1)[0] * 100)
#         root['name'] = names[x%len(names)]
#         root['age'] = x%100
#         s = json.dumps(root)
#         publish.single('faceAttr', payload=s, hostname=MQTT_URL)





def image(video_path='/media/video/test.avi'):
    root = dict()
    idx = 1
    print(video_path)
    while True:
        cap = cv2.VideoCapture(video_path)
        while True:
            time.sleep(1)
            print('frame', idx)
            ret, img = cap.read()
            if ret == False:
                cap = cv2.VideoCapture(video_path)
                ret, img = cap.read()
            cv2.imwrite('/media/img/test.jpg', img)
            publish.single('offlineImage', payload='c', hostname=MQTT_URL)
            idx += 1




funcs = [warning, genderRate, latestDay, image]

threads = []
for func in funcs:
    threads.append(threading.Thread(target=func))
for t in threads:
    t.start()
for t in threads:
    t.join()