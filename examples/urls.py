import threading
from django.conf.urls import *
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from dwebsocket.decorators import accept_websocket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import cv2
import json
import numpy as np
import base64
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
MQTT_URL = '127.0.0.1'
def base_view(request):
    print('ssss')

    return render(request, 'test.html')

clients = []

@accept_websocket
def warning(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about warning!')
            wsclients = request.websocket
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
                # print(msg.topic + " " + str(msg.payload))
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

@accept_websocket
def latestday(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about latestday!')
            wsclients = request.websocket
            # print(len(wsclients))
            #subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='latestday')
                print('subscribe latestday successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                # print(msg.topic + " " + str(msg.payload))
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

@accept_websocket
def genderRate(request):
    print('genderRate')
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about genderRate!')
            wsclients = request.websocket
            # print(len(wsclients))
            #subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='genderRate')
                print('subscribe genderRate successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                # print(msg.topic + " " + str(msg.payload))
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
        #todo 直接转发？
        x = request.POST.get("x", None)
        y = request.POST.get("y", None)
        root = dict()
        root['x'] = x
        root['y'] = y
        print(root)
        s = json.dumps(root)
        print('get the infos from frontend ', s)
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
            print('receive a new websocket about face_attr!')
            wsclients = request.websocket

            # print(len(wsclients))
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

#读取指定位置的图片并通过websocket发送到前端页面
@accept_websocket
def offlineImage(request):
    img_path = '/media/img/offline.jpg'
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about offlineImage!')
            wsclients = request.websocket

            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(topic='offlineImage')
                print('subscribe offlineImage successfully')

            # The callback for when a PUBLISH message is received from the server.
            def on_message(client, userdata, msg):
                print(msg.payload)
                wsclients.send(msg.payload)

                mat = cv2.imread(img_path)

                mat = cv2.resize(mat, (mat.shape[1]//2,mat.shape[0]//2))
                print('after',mat.shape)
                # import matplotlib.pyplot as plt
                # plt.imshow(mat)
                # plt.show()
                string = base64.b64encode(cv2.imencode('.jpg', mat)[1]).decode()
                wsclients.send(string)


            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_URL, 1883, 60)
            client.loop_forever()
        finally:
            clients.remove(request.websocket)
            lock.release()

@accept_websocket
def age(request):
    print('get a ws from age')
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            print('receive a new websocket about age!')
            wsclients = request.websocket

            # print(len(wsclients))
            # subscribe topic by mqtt
            def on_connect(client, userdata, flags, rc):
                print("Connected with result code " + str(rc))

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
            clients.remove(request.websocket)
            lock.release()
urlpatterns = [
    # Example:
    url(r'^$', base_view),
    # url(r'^warning', warning),
    # url(r'^genderRate', genderRate),
    # url(r'^latestday', latestday),
    # url(r'^image', face),
    # url(r'^faceAttr', faceAttr),
    # url(r'^face', face),
    # url(r'^age', age),
    url(r'selectPerson', selectPerson),
    url(r'offlineImage', offlineImage),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
]



