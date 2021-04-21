import threading

from   fastapi  import FastAPI, HTTPException
from   gpiozero import LED
import uvicorn


from api_models import models
import parseConfig
import timer


app = FastAPI()

led = LED(17)

@app.get("/on", status_code=200)
async def turn_on():
    light_ON()
    return {"ok": True}

@app.get("/off", status_code=200)
async def turn_off():
    light_OFF()
    return {"ok": True}

@app.post("/set", status_code=200)
async def set_time(req: models.LightSetter):
    global CONFIG
    if req.mode == models.Mode.On:
        TIMER_ONE.stop_timer()
        if req.time != "":
            TIMER_ONE.t = req.time
            CONFIG = CONFIG._replace(start_time=req.time)
            print("DEBUG", CONFIG)
            CONFIG.write_config_file("./config")
            return {"ok": True}
        raise HTTPException(status_code=400)
    elif req.mode == models.Mode.Off:
        TIMER_TWO.stop_timer()
        if req.time != "":
            TIMER_TWO.t = req.time
            CONFIG._replace(start_time=req.time)
            CONFIG.write_config_file("./config")
            return {"ok": True}
        raise HTTPException(status_code=400)
    
    raise HTTPException(status_code=400)


TIMER_ONE, TIMER_TWO = None, None

CONFIG = None

def light_ON():
    led.on()
    print("LIGHT ON")

def light_OFF():
    led.off()
    print("LIGHT OFF")


def light_on_timer(start_time:str):
    global TIMER_ONE
    TIMER_ONE = timer.Timer(start_time)
    th = threading.Thread(target=TIMER_ONE.start_timer, args=(light_ON,))
    th.daemon = True
    th.start()

def light_off_timer(stop_time:str):
    global TIMER_TWO
    TIMER_TWO = timer.Timer(stop_time)
    th = threading.Thread(target=TIMER_TWO.start_timer, args=(light_OFF,))
    th.daemon = True
    th.start()

def main():
    global CONFIG
    CONFIG = parseConfig.load_config("./config")

    print("DEBUG", CONFIG.start_time, CONFIG.stop_time)

    light_on_timer(CONFIG.start_time)
    light_off_timer(CONFIG.stop_time)



if __name__ == "__main__":
    main()
    uvicorn.run(app, host="0.0.0.0", port=8080)
