import psutil
import time


START_TIME = time.time()



def get_system_status():

    battery = None

    try:

        battery_info = psutil.sensors_battery()

        if battery_info:

            battery = {
                "percent": battery_info.percent,
                "charging": battery_info.power_plugged
            }


    except:

        battery = None



    uptime_seconds = (
        time.time() - START_TIME
    )


    return {

        "cpu": psutil.cpu_percent(
            interval=0.5
        ),


        "memory": psutil.virtual_memory().percent,


        "disk": psutil.disk_usage("/").percent,


        "battery": battery,


        "uptime": int(
            uptime_seconds
        )

    }