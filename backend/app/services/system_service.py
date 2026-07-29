import psutil



def get_system_status():


    cpu = psutil.cpu_percent(
        interval=1
    )


    memory = psutil.virtual_memory()


    ram_used = round(
        memory.percent,
        1
    )


    battery = psutil.sensors_battery()


    battery_percent = None


    if battery:

        battery_percent = battery.percent



    return {


        "cpu":
        f"{cpu}%",


        "ram":
        f"{ram_used}%",


        "battery":
        (
            f"{battery_percent}%"
            if battery_percent is not None
            else "Not available"
        )

    }