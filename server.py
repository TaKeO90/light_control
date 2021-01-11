#!/usr/bin/env python3

from flask import Flask, request, jsonify
from typing import NamedTuple
from gpiozero import LED
from datetime import datetime, timedelta
from time import strftime
import math
import time
import asyncio
import threading
import json
import os


#TODO: Code Cleaning. 

app = Flask(__name__)

led = LED(17)

LIGHTSTATUS = "off"

class ResponseData:

    def __init__(self,msg:str,isok:bool):
        self.msg = msg
        self.isok = isok
   
    def ReturnMsg(self):
        if self.isok:
            ValidMsg = dict(ok=True,msg=self.msg)
            return ValidMsg
        elif not self.isok:
            ErrorMsg = dict(ok=False,msg=self.msg)
            return ErrorMsg
        elif msg == "" and not self.isok:
            WrongMethod = dict(ok="Wrong Method")
            return WrongMethod

class Light:
    statuses = dict(on=True,off=False)
    @classmethod
    def control(cls,status:str) -> bool :
        global led
        global LIGHTSTATUS
        if cls.statuses[status]:
            led.on()
            LIGHTSTATUS = "on"
            return True
        else :
            led.off()
            LIGHTSTATUS = "off"
            return True


@app.route("/api/light",methods=["POST","GET"])
def lightControl():
    if request.method == "POST":
        status = request.get_json()
        try :
            lightStatus = status["light"]
            l = Light()
            if lightStatus.lower() == "on":
                r = ResponseData("lightup",True).ReturnMsg()
                isOk = l.control(lightStatus.lower())
                if isOk:
                    return jsonify(r)
            elif lightStatus.lower() == "off":
                r = ResponseData("lightOff",True).ReturnMsg()
                isOk = l.control(lightStatus.lower())
                if isOk:
                    return jsonify(r)
                else :
                    return jsonify(ResponseData("No such commmand",False).ReturnMsg())
        except KeyError as k:
            key, = k.args
            r = ResponseData(f"There is no parametre as {key}",False).ReturnMsg()
            return jsonify(r)
    else :
        global LIGHTSTATUS
        r = ResponseData(LIGHTSTATUS,True).ReturnMsg()
        return jsonify(r)


## Accept on and off light timestamps.
TRACK_RUNNING = False
MINI_DB_JSON_FILE = "time.json"
#TODO: initialize this var when server start.
TIME_DB_OBJ = {"light":{"on":"","off":""}}
##

def writeTimeToConf():
    with open(MINI_DB_JSON_FILE, "w") as f:
        json.dump(TIME_DB_OBJ, f)


@app.route("/api/light/on", methods=["POST","GET"])
def getOnTime():
    if request.method == "POST":
        global TIME_DB_OBJ
        try:
            on_time = request.get_json()["time"]
        except KeyError as k:
            return jsonify({"Invalid Parameter":k.args[0]})

        TIME_DB_OBJ["light"]["on"] = on_time
        writeTimeToConf()
        return jsonify({"msg":"on Time Set"})

    elif request.method == "GET":
        if TIME_DB_OBJ["light"]["on"] != "":
            return jsonify(TIME_DB_OBJ["light"]["on"])
        return jsonify({"msg":"no on time specified"})


@app.route("/api/light/off", methods=["POST","GET"])
def getOffTime():
    if request.method == "POST":
        global TIME_DB_OBJ 
        try:
            off_time = request.get_json()["time"]
        except KeyError as k:
            return jsonify({"Invalid Parameter": k.args[0]})

        TIME_DB_OBJ["light"]["off"] = off_time
        writeTimeToConf()
        return jsonify({"msg":"off Time Set"})

    elif request.method == "GET":
        if TIME_DB_OBJ["light"]["off"] != "":
            return jsonify(TIME_DB_OBJ["light"]["off"])
        return jsonify({"msg":"no off time specified"})
        

class Times(NamedTuple):
    onTime:int
    offTime:int


def getTimeDiffs() -> Times:
    # if our time object has no on or off time.
    if TIME_DB_OBJ["light"]["on"] == "" or TIME_DB_OBJ["light"]["off"] == "":
        #need both on and off timestamp in order to get time diffs.
        return None

    now = datetime.now()
    fmt = "%Y-%m-%d %H:%M:%S"

    on_h, on_m, on_s  = TIME_DB_OBJ["light"]["on"].split(":")
    off_h, off_m, off_s = TIME_DB_OBJ["light"]["off"].split(":")

    on_time = datetime.strptime(
            f"{now.year}-{now.month}-{now.day} {on_h}:{on_m}:{on_s}", fmt)
    off_time = datetime.strptime(
            f"{now.year}-{now.month}-{now.day} {off_h}:{off_m}:{off_s}", fmt)

    time_now  = datetime.strptime(
            f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}", fmt)

    deltaONtime = (on_time - time_now).total_seconds()
    deltaOFFtime = (off_time - time_now).total_seconds()

    if time_now > on_time :
        on_time = on_time + timedelta(hours=24)
        deltaONtime = (on_time - time_now).total_seconds()

    if time_now > off_time:
        off_time = off_time + timedelta(hours=24)
        deltaOFFtime = (off_time - time_now).total_seconds()

    return Times(math.floor(deltaONtime), math.floor(deltaOFFtime))



### need to set for each thread a separated function
deltaOntime = 0
deltaOfftime= 0
###

def turnOn():
    global deltaOntime
    deltaOntime = 0
    diffs = getTimeDiffs()
    deltaOntime = diffs.onTime
    Light().control("on")
    runOnTimeThread()


def turnOff():
    global deltaOfftime
    deltaOfftime = 0
    diffs = getTimeDiffs()
    deltaOfftime = diffs.offTime
    Light().control("off")
    runOffTimeThread()

def runOnTimeThread(): 
    if deltaOntime != 0:
        threading.Timer(deltaOntime, turnOn).start()

def runOffTimeThread():
    if deltaOfftime != 0:
        threading.Timer(deltaOfftime, turnOff).start()


@app.route("/api/track", methods=["GET"])
def trackTime():
    diffs = getTimeDiffs()
    if diffs is not None:
        global deltaOntime
        global deltaOfftime

        deltaOntime = diffs.onTime
        deltaOfftime = diffs.offTime

        runOnTimeThread()
        runOffTimeThread()

        return "Tracking..."

    return "Failed to Track both on and off Times..."


if __name__ == "__main__":
    # When server starts we deserialize our json into TIME_DB_OBJ.
    if len([f for f in os.listdir() if f == MINI_DB_JSON_FILE]) != 0:
        with open(MINI_DB_JSON_FILE, "r") as f:
            TIME_DB_OBJ = json.load(f)
        print("[+] times initialized", TIME_DB_OBJ)
        trackTime()

    app.run(host="0.0.0.0",port="6040",debug=False)

