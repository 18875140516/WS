import threading
from django.conf.urls import *
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from dwebsocket.decorators import accept_websocket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import cv2
import os
import json
import numpy as np
import base64
import time
import logging
import pymysql
from configRetrive import ConfigRetrive
from udn_socket import UDNServer
from register_event_handler import RegisterEventHandler

USE_UDN = False
und_server = UDNServer()
logging.basicConfig(filename='/log/logger.log', level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',)
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
logging.info('-------------------------BEGIN-------------------------')
MQTT_URL = '211.67.21.65'
CONFIG_TOPIC = 'config'
PORT = 1883
MYSQL_IP = '211.67.21.65'
MYSQL_PORT = 3306
MYSQL_USER = 'lyz'
MYSQL_PASSWORD = 'lyz'
MYSQL_DB = 'mysql'
logging.info('initiate configRetrive')
config = ConfigRetrive()

logging.info('url init config')
MYSQL_IP = config.get('MYSQL_IP', MYSQL_IP)
MYSQL_PORT = config.get('MYSQL_PORT', MYSQL_PORT)
MYSQL_USER =  config.get('MYSQL_USER', MYSQL_USER)
MYSQL_PASSWORD = config.get('MYSQL_PASSWORD', MYSQL_PASSWORD)
MYSQL_DB = config.get('MYSQL_DB', MYSQL_DB)

logging.info('initiate mysql connect')
global_db = pymysql.connect(host=MYSQL_IP, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)

warning_hash = dict()
TEST_MODE = False
def base_view(request):
    print('ssss')

    return render(request, 'test.html')

def ICBC(request):
    return render(request, '/home/liuyongzhi/Downloads/dist/index.html')

clients = []

@accept_websocket
def warning(request):

    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            logging.info('receive a new websocket about warning!')

            wsclients = request.websocket
            if TEST_MODE:
                print('DEBUG MODE')
                root = dict()
                root['message'] = 'this is a warning!'
                while True:
                    root['type'] = int(np.random.rand(1)[0] * 100)
                    s = json.dumps(root)
                    wsclients.send(s)
                    time.sleep(10)

            # print(len(wsclients))
            #subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='warning')
                print('subscribe warning successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                
                if msg.payload not in warning_hash.keys():
                    #todo :control warning circle
                    warning_hash[msg.payload] = time.time()
                elif msg.payload in warning_hash.keys():
#                    print(time.time() - warning_hash[msg.payload])
                    if time.time() - warning_hash[msg.payload] < 10:
                        warning_hash[msg.payload] = time.time()
                        return
                wsclients.send(msg.payload)
                # for client in clients:
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            lock.release()

# 	{ 'population': [12, 34] }
@accept_websocket
def latestday(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about latestday!')
            wsclients = request.websocket
            if TEST_MODE:
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

            #subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='latestday')
                print('subscribe latestday successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                wsclients.send(msg.payload)
                # for client in clients:
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            clients.remove(request.websocket)
            lock.release()


@accept_websocket
def genderRate(request):
    print('genderRate')
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket
            if TEST_MODE:
                logging.info('gender rate test')
                root = dict()
                root["男"] = 0
                root["女"] = 0

                while True:
                    time.sleep(5)
                    x = np.random.rand(2) * 100
                    root["男"] = int(x[0])
                    root["女"] = int(x[1])
                    s = json.dumps(root)
                    wsclients.send(s)

            #subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='genderRate')
                print('subscribe genderRate successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                wsclients.send(msg.payload)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)
 
            client = mqtt.Client()
            client.on_connect = on_connect 
            client.on_message = on_message 
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever() 
        finally: 
            clients.remove(request.websocket) 
            lock.release()

def selectPerson(request):

    if request.method == "POST":
        #todo ֱ��ת����
        #logging.info()
        msg = request.body
        msg = json.loads(msg)
        logging.info(msg)
        x = msg['x']
        y = msg['y']
        root = dict()
        root['x'] = x
        root['y'] = y
        s = json.dumps(root)
        publish.single('selectPerson', s, hostname=MQTT_URL)
        return HttpResponse('post')
    else:
        return HttpResponse('get')
# @accept_websocket
# def faceAttr(request):
#     if request.is_websocket:
#         lock = threading.RLock()
#         try:
#             lock.acquire()
#             print('receive a new websocket about faceAttr!')
#             wsclients = request.websocket
#
#             # print(len(wsclients))
#             # subscribe topic by mqtt
#             def on_connect(client, userdata, flags, rc):
#                 print("Connected with result code " + str(rc))
#
#                 # Subscribing in on_connect() means that if we lose the connection and
#                 # reconnect then subscriptions will be renewed.
#                 client.subscribe(topic='faceAttr')
#                 print('subscribe faceAttr successfully')
#
#             # The callback for when a PUBLISH message is received from the server.
#             def on_message(client, userdata, msg):
#                 print(msg.topic + " " + str(msg.payload))
#                 wsclients.send(msg.payload)
#                 # for client in clients:
#                 #     print(len(clients))
#                 #     client.send(msg.payload)
#
#             client = mqtt.Client()
#             client.on_connect = on_connect
#             client.on_message = on_message
#             client.connect(MQTT_URL, 1883, 60)
#             client.loop_forever()
#         finally:
#             clients.remove(request.websocket)
#             lock.release()
# @accept_websocket
# def offlineImage(request):
#     img_path = '/media/offline.jpg'
#     if request.is_websocket:
#         lock = threading.RLock()
#         try:
#             lock.acquire()
#             print('receive a new websocket about offlineImage!')
#             wsclients = request.websocket
#
#             # subscribe topic by mqtt
#             def on_connect(client, userdata, flags, rc):
#                 print("Connected with result code " + str(rc))
#
#                 # Subscribing in on_connect() means that if we lose the connection and
#                 # reconnect then subscriptions will be renewed.
#                 client.subscribe(topic='offlineImage')
#                 print('subscribe offlineImage successfully')
#
#             # The callback for when a PUBLISH message is received from the server.
#             def on_message(client, userdata, msg):
#                 mat = cv2.imread(img_path)
#                 string = base64.b64encode(cv2.imencode('.jpg', mat)[1]).decode()
#                 wsclients.send(string)
#
#             client = mqtt.Client()
#             client.on_connect = on_connect
#             client.on_message = on_message
#             client.connect(MQTT_URL, 1883, 60)
#             client.loop_forever()
#         finally:
#             clients.remove(request.websocket)
#             lock.release()
#     pass

IMAGE_PATH = '/media/image/head.jpg'

@accept_websocket
def image(request):
    if request.is_websocket:   
        lock = threading.RLock()   
        try:   
            lock.acquire()   
            print('receive a new websocket about image!')
            wsclients = request.websocket 
            # print(len(wsclients))  
            #subscribe topic by mqtt 
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))
  
                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='image')
                print('subscribe image successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                mat = cv2.imread(IMAGE_PATH)
                string = base64.b64encode(cv2.imencode('.jpg', mat)[1]).decode()
                wsclients.send(string)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)
  
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            clients.remove(request.websocket)
            lock.release()


@accept_websocket
def face(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about face!')
            wsclients = request.websocket

            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='face')
                print('subscribe face successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                mat = cv2.imread('/media/image/face.jpg')
                # print('before',mat.shape)
                mat = cv2.resize(mat, (mat.shape[1]//2,mat.shape[0]//2))
                # print('after',mat.shape)
                # import matplotlib.pyplot as plt
                # plt.imshow(mat)
                # plt.show()
                string = base64.b64encode(cv2.imencode('.jpg', mat)[1]).decode()
                wsclients.send(string)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect("211.67.20.74", 1883, 60)
            client.loop_forever()
        finally:
            clients.remove(request.websocket)
            lock.release()

@accept_websocket
def faceAttr(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket

            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='faceAttr')
                print('subscribe face_attr successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                # print('msg=', msg)
                wsclients.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect("211.67.20.74", 1883, 60)
            client.loop_forever()
        finally:
            clients.remove(request.websocket)
            lock.release()


@accept_websocket
def offlineImage(request):
    img_path = '/media/img/offline.jpg'
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            logging.info('receive a new websocket about offlineImage!')
            wsclients = request.websocket
            RegisterEventHandler('/tmp/test.jpg', wsclients)
            return
            if TEST_MODE:
                if os.path.exists('/media/video/test.avi'):
                    cap = cv2.VideoCapture('/media/video/test.avi')
                else:
                    cap = cv2.VideoCapture(0)
                while True:
                    ret, img = cap.read()
                    s = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                    wsclients.send(s)
            if USE_UDN:
                UDNServer.transfer_img(wsclients)
            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='offlineImage')
                logging.info('subscribe offlineImage successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                wsclients.send(msg.payload)


            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            clients.remove(request.websocket)
            lock.release()

@accept_websocket
def flowStanding(request):
    img_path = '/tmp/standing.jpg'
    if request.is_websocket:
        print('flow standing')
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclient = request.websocket
            RegisterEventHandler(img_path, wsclient)
        finally:
            lock.release()

#{ 'age': [12, 13, 20, 23] }
@accept_websocket
def ageRate(request):
    logging.info('age rate')
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket
            if TEST_MODE:
                logging.info('age rate test')
                while True:
                    root = dict()
                    root['age'] = []
                    age = np.random.randint(low=0, high=100,size=4)
                    age = [int(i) for i in age]
                    root['age'] = age
                    s = json.dumps(root)
                    logging.info('ws:ageRate' + s)
                    wsclients.send(s)
                    time.sleep(3)

            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='age')
                print('subscribe age successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):

                wsclients.send(msg.payload)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            # clients.remove(request.websocket)
            lock.release()

# 	{ 'status': '在岗/暂离/离岗' }
@accept_websocket
def managerStatus(request):
    logging.info('managerStatus websocket')
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket


            if False and TEST_MODE:
                logging.info('test managerStatus')
                status = ['online', 'offline', 'leave']
                while True:
                    root = dict()
                    root['status'] = status[np.random.randint(low=0, high=2,size=1)[0]]
                    s = json.dumps(root)
                    wsclients.send(s)
                    time.sleep(3)

            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='managerStatus')
                print('subscribe managerStatus successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):

                wsclients.send(msg.payload)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            # clients.remove(request.websocket)
            lock.release()

#mostStandingTime
@accept_websocket
def mostStandingTime(request):
    logging.info('most standing time')
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket
#            if TEST_MODE:
#                logging.info('test mostStandingTime')
#                while True:
#                    root = dict()
#                    root['mostStandingTime'] = int(np.random.randint(low=0, high=2000, size=1)[0])
#                    s = json.dumps(root)
#                    wsclients.send(s)
#                    time.sleep(3)

            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='mostStandingTime')
                print('subscribe mostStandingTime successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):

                wsclients.send(msg.payload)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)
            logging.info('mostStandingTime')
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            # clients.remove(request.websocket)
            lock.release()

@accept_websocket
def numQueue(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket
#            if TEST_MODE:
#                logging.info('test numQueue')
#                while True:
#                    root = dict()
#                    root['numberOfQueue'] = int(np.random.randint(low=0, high=50, size=1)[0])
#                    s = json.dumps(root)
#                    # logging.info('numberOfQueue = ' + s)
#                    wsclients.send(s)
#                    time.sleep(3)
#
            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                logging.info('connected numQueue')
                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='numQueue')
                logging.info('subscribe numQueue')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):

                wsclients.send(msg.payload)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            # clients.remove(request.websocket)
            lock.release()

#{ mostContactTime: 12 }
@accept_websocket
def mostContactTime(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            wsclients = request.websocket
#            if TEST_MODE:
#                logging.info('test mostContactTime')
#                while True:
#                    root = dict()
#                    root['mostContactTime'] = int(np.random.randint(low=0, high=2000, size=1)[0])
#                    s = json.dumps(root)
#                    # logging.info('mostContactTime msg = '+ s)
#                    wsclients.send(s)
#                    time.sleep(3)
#
            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='age')
                print('subscribe mostContactTime successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):

                wsclients.send(msg.payload)
                # for client in clients:
                #     print(len(clients))
                #     client.send(msg.payload)

            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            # clients.remove(request.websocket)
            lock.release()

def areaHandle(request):
    logging.info('areaHandle request')
    msg = None
    logging.info(request.method)
    if request.method == 'POST':
        msg = request.body
        msg = json.loads(msg)
    elif request.method == 'GET':
        msg = request.GET
    root = dict()
    logging.info(msg['flag'])
    if msg['flag'] == 'get_image':
        rtsp_url = None  # todo: get the url of topic
        img = cv2.imread('/media/img/test.jpg')  # todo: get the image of url
        root['flag'] = 'return_img'
        root['topic'] = msg['topic']
        img_str = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        root['img'] = img_str
        s = json.dumps(root)
        #logging.info('encoded = ' +s )
        return HttpResponse(s)
    elif msg['flag'] == 'send_area':
        root['flag'] = 'response'
        try:
            area = msg['area']
            size = msg['size']
            logging.info('type = ' + str(type(area)) + 'area = ' + str(area))
            logging.info('type = ' + str(type(size)) + 'size = ' + str(size))
            if list == type(area) and list == type(size):
                logging.info('pack json')
                root = dict()
                tmp = msg['area']
                tmp = [[x[0]/msg['size'][0], x[1]/msg['size'][1]] for x in tmp]
                logging.info(str(tmp))
                logging.info(msg['topic'])
                root[msg['topic']] = tmp
                s = json.dumps(root)
                logging.info('get a new area '+ s)
                logging.info(s)
                publish.single(topic=CONFIG_TOPIC, hostname=MQTT_URL, payload=s)
            root['status'] = '1'
        except:
            root['status'] = '2'
        s = json.dumps(root)
        return HttpResponse(s)
        #todo: return the result to frontend
def selectPattern(request):
    logging.info('selectPattern request')
    msg = None
    logging.info(request.method)
    if request.method == 'POST':
        msg = request.body
        msg = json.loads(msg)
    elif request.method == 'GET':
        msg = request.GET
    root = dict()
    logging.info('get msg ' + str(msg))
    if msg['flag'] == 'upload_pattern':
        #todo: insert imgs to the database(ok) and update backend operate, send received image to topic config(key=manager_pattern)
        #check if img_id in database
        try:
            img_b64 = base64.b64decode(msg['img'])
            img_array = np.fromstring(img_b64, np.uint8)
            img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (128, 384))

            img_s = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
            root[msg['topic']] = img_s
            cursor = global_db.cursor()
            s = json.dumps(root)      
            # logging.info(str(s))
            publish.single(topic='config', hostname=MQTT_URL, payload=s)
            if msg['img_id'] == -1:
                #upload img
                ret = cursor.execute(r"insert into pattern_infos(img, topic, timestamp) values ('{}', '{}', '{}')"
                        .format(img_s, msg['topic'],msg['timestamp']))
                global_db.commit()
                if ret == 1:
                    logging.info('insert mysql pattern_infos OK')
                    

            return HttpResponse('ok')
        except:
            return HttpResponse('error')
    elif msg['flag'] == 'get_candidates':
        root['flag'] = 'return_pattern'
        #read the database and return pattern
        try:
            root['imgs'] = []
            root['topics'] = []
            root['img_ids'] = []
            root['timestamps'] = []
            cursor = global_db.cursor()
            cursor.execute(r'select * from pattern_infos order by timestamp desc limit 5')
            ret = cursor.fetchall()
            for item in ret:
                root['imgs'].append(item[0])
                root['img_ids'].append(item[1])
                root['topics'].append(item[2])
                root['timestamps'].append(item[3])
            s = json.dumps(root)
            return HttpResponse(s)
        except:
            return HttpResponse('error')
    return HttpResponse("paramter error")

def setEntrySize(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()
        k = str(list(msg.keys())[0])
        v = msg[k]
        root[k] = v
        s = json.dumps(root)
        publish.single('config', payload=s, hostname=MQTT_URL)
        return HttpResponse('ok')
    except:
        return HttpResponse('error')

def setBankCapacity(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()
        k = str(list(msg.keys())[0])
        v = msg[k]
        root[k] = v
        s = json.dumps(root)
        publish.single('config', payload=s, hostname=MQTT_URL)
        return HttpResponse('ok')
    except:
        return HttpResponse('error')


def setWaitTime(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()
        k = str(list(msg.keys())[0])
        v = msg[k]
        root[k] = v
        s = json.dumps(root)
        publish.single('config', payload=s, hostname=MQTT_URL)
        return HttpResponse('ok')
    except:
        return HttpResponse('error')


def setWaitNumber(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()
        k = str(list(msg.keys())[0])
        v = msg[k]
        root[k] = v
        s = json.dumps(root)
        publish.single('config', payload=s, hostname=MQTT_URL)
        return HttpResponse('ok')
    except:
        return HttpResponse('error')


def setLeaveTime(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()
        k = str(list(msg.keys())[0])
        v = msg[k]
        root[k] = v
        s = json.dumps(root)
        publish.single('config', payload=s, hostname=MQTT_URL)
        return HttpResponse('ok')
    except:
        return HttpResponse('error')


def setContactTime(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()
        k = str(list(msg.keys())[0])
        v = msg[k]
        root[k] = v
        s = json.dumps(root)
        publish.single('config', payload=s, hostname=MQTT_URL)
        return HttpResponse('ok')
    except:
        return HttpResponse('error')

def getWaitNumber(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()

        k = 'waitNumber'
        v = config.get(k, '999')
        print('waitNumber = ', v)
        root[k] = v
        s = json.dumps(root)
        return HttpResponse(s)
    except:
        return HttpResponse('error')

def getLeaveTime(request):
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()

        k = 'leaveTime'

        v = config.get(k, '999')

        root[k] = v
        s = json.dumps(root)
        return HttpResponse(s)
    except:
        return HttpResponse('error')

def getContactTime(request):
    logging.info('getContactTime')
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()

        k = 'contactTime'

        v = config.get(k, '999')

        root[k] = v
        s = json.dumps(root)
        return HttpResponse(s)
    except:
        return HttpResponse('error')
def getWaitTime(request):
    logging.info('getWaitTime')
    try:
        if request.method == 'POST':
            msg = request.body
            msg = json.loads(msg)
        elif request.method == 'GET':
            msg = request.GET
        root = dict()

        k = 'waitTime'

        v = config.get(k, '999')
        root[k] = v
        s = json.dumps(root)
        return HttpResponse(s)
    except:
        return HttpResponse('error')
def getEntrySize(request):
    logging.info('getEntrySize')
    try:
        if request.method == 'POST': 
            msg = request.body       
            msg = json.loads(msg)  
        elif request.method == 'GET': 
            msg = request.GET  
        root = dict()   
    
        k = 'entrySize'    
    
        v = config.get(k, '999')
   
        root[k] = v   
        s = json.dumps(root)  
        return HttpResponse(s) 
    except: 
        return HttpResponse('error') 
def getPattern(request):
    print("getPattern")
    logging.info('getPattern')
    try:
        if request.method == 'POST': 
            msg = request.body       
            msg = json.loads(msg)  
        elif request.method == 'GET': 
            msg = request.GET  
        root = dict()   
        if msg['flag'] == 'get_pattern':
            topic = msg['topic']
            root['topic'] = topic
            root['img'] = config.get(topic, None)
            s = json.dumps(root)

            return HttpResponse(s) 
        return HttpResponse('flag error')
    except: 
        return HttpResponse('error') 
@accept_websocket 
def leftover(request): 
    """ 
    展示遗留物品类别及图片信息 
    :param request: 
    :return: {'img':base64img,'classes':bag}
    """ 
    #main() 
    if request.is_websocket: 
        lock = threading.RLock() 
        try: 
            lock.acquire() 
            print("receive a new ws about abnormal")
            wsclients = request.websocket
  
            def on_connect(clent, userdata, flags, rc):
                print("Connected with result code " + str(rc))
                client.subscribe(topic="leftover")
                print('subscribe abnormal successfully')
    
            def on_message(client, userdata, msg):
                wsclients.send(msg.payload)
     
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(host=MQTT_URL, port=MQTT_PORT)
            client.loop_forever()
            # client.loop_start()
        finally:
            lock.release()
@accept_websocket
def abnormal(request):
    """ 
    展示危险物品类别及图片信息
    :param request:
    :return: {'img':base64img,'name':knife}
    """ 
    if request.is_websocket:
        lock = threading.RLock()
        try: 
            lock.acquire()
            print("receive a new ws about abnormal")
            wsclients = request.websocket
 
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))
                client.subscribe(topic="abnormal")
                print('subscribe abnormal successfully')
 
            def on_message(client, userdata, msg):
                wsclients.send(msg.payload)
 
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            A
            client.connect(host=MQTT_URL, port=MQTT_PORT)
            client.loop_forever()
            # client.loop_start()
        finally:
            lock.release()
urlpatterns = [
    # Example:
    url(r'^$', base_view),
    url(r'ICBC', ICBC),
    url(r'^warning', warning),
    url(r'selectPerson', selectPerson),
    url(r'flowStanding', flowStanding),
    #url(r'flowFace', flowStanding),
    #url(r'flowDangerous', flowStanding),
    #url(r'flowLeftover', flowStanding),
    #url(r'flowOffline', flowStanding),
    url(r'managerStatus', managerStatus), #test ok
    url(r'mostStandingTime', mostStandingTime), #test ok
    url(r'mostContactTime', mostContactTime), #test ok
    url(r'^numQueue', numQueue), #test ok
    url(r'^areaHandle', areaHandle), #test ok
    url(r'^selectPattern', selectPattern),
     

    #some config information
    url(r'setEntrySize', setEntrySize),
    url(r'setBankCapacity', setBankCapacity),
    url('setWaitTime', setWaitTime),
    url(r'setWaitNumber', setWaitNumber),
    url(r'setLeaveTime', setLeaveTime),
    url(r'setContactTime', setContactTime),
    
    url(r'getWaitNumber', getWaitNumber),
    url(r'getLeaveTime', getLeaveTime),
    url(r'getContactTime', getContactTime),
    url(r'getWaitTime', getWaitTime),
    url(r'getEntrySize', getEntrySize),
	url(r'leftover', leftover),
	url(r'abnormal', abnormal),
    url(r'getPattern', getPattern),
    # url(r'^genderRate', genderRate),#test ok
    # url(r'^latestday', latestday),
    # url(r'^image', face),
    # url(r'^faceAttr', faceAttr),
    # url(r'^face', face),
    # url(r'^ageRate', ageRate), # test ok

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
]



