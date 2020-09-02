#!/usr/bin/env python3
from flask import Flask, request, jsonify
from gpiozero import LED
import asyncio


#TODO: add gpio raspberry pi to control light

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
####################################
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

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="6000",debug=False)
