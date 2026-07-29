import os
import subprocess


APP_MAP = {

    "chrome":
        "chrome",

    "google chrome":
        "chrome",

    "notepad":
        "notepad",

    "calculator":
        "calc",

    "calc":
        "calc",

    "vscode":
        "code",

    "visual studio code":
        "code",

    "spotify":
        "spotify",

}



def open_application(command: str):


    text = command.lower()



    for name, exe in APP_MAP.items():


        if name in text:


            try:

                subprocess.Popen(
                    exe,
                    shell=True
                )


                return {

                    "success":True,

                    "message":
                    f"Opening {name}, sir."

                }


            except Exception as e:


                return {

                    "success":False,

                    "message":
                    str(e)

                }




    return {

        "success":False,

        "message":
        "I could not find that application, sir."

    }