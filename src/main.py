import threading

from   fastapi  import FastAPI, HTTPException
import uvicorn

from api_models import models
import parseConfig
import timer


app = FastAPI()

@app.get("/on", status_code=200)
async def turn_on():
    light_ON()
    return {"ok": True}

@app.get("/off", status_code=200)
async def turn_off():
    light_OFF()
    return {"ok": True}

# TODO: Update config file when stting new time.
@app.post("/set", status_code=200)
async def set_time(req: models.LightSetter):
    if req.mode == models.Mode.On:
        TIMER_ONE.stop_timer()
        if req.time != "":
            TIMER_ONE.t = req.time
            return {"ok": True}
        raise HTTPException(status_code=400)
    elif req.mode == models.Mode.Off:
        TIMER_TWO.stop_timer()
        if req.time != "":
            TIMER_TWO.t = req.time
            return {"ok": True}
        raise HTTPException(status_code=400)
    
    raise HTTPException(status_code=400)


TIMER_ONE, TIMER_TWO = None, None

def light_ON():
    #TODO: ...
    print("LIGHT ON")

def light_OFF():
    #TODO: ...
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
    cfg = parseConfig.load_config("./config")

    print("DEBUG", cfg.start_time, cfg.stop_time)

    light_on_timer(cfg.start_time)
    light_off_timer(cfg.stop_time)


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="0.0.0.0", port=8080)
