import os
import webbrowser


from app.services.system_service import get_system_status


from app.services.windows_service import (
    check_windows_updates,
    get_update_details,
    install_windows_updates
)


from app.services.conversation_state import (
    set_action,
    get_action,
    clear_action
)





COMMANDS = {

    "youtube":
        "https://youtube.com",

    "google":
        "https://google.com",

    "github":
        "https://github.com",

}








def is_confirmation(text):

    return text in [

        "yes",
        "yeah",
        "yep",
        "sure",
        "okay",
        "ok",
        "do it",
        "go ahead"

    ]









def execute_command(message: str):


    text = message.lower().strip()





    # HANDLE CONFIRMATIONS

    if is_confirmation(text):


        action = get_action()



        if action == "show_updates":


            clear_action()


            set_action(
                "install_updates"
            )


            return get_update_details()



        if action == "install_updates":


            clear_action()


            return install_windows_updates()





    # ASK UPDATE DETAILS

    if (

        "what updates" in text

        or "which updates" in text

        or "tell me updates" in text

        or "update details" in text

    ):


        return get_update_details()







    # WINDOWS UPDATE CHECK

    if (

        "check update" in text

        or "check updates" in text

        or "windows update" in text

    ):


        set_action(
            "show_updates"
        )


        return check_windows_updates()







    # INSTALL UPDATES DIRECTLY

    if (

        "install update" in text

        or "install updates" in text

        or "update my pc" in text

    ):


        clear_action()


        return install_windows_updates()







    # SYSTEM STATUS

    if (

        "cpu" in text

        or "ram" in text

        or "battery" in text

        or "system status" in text

    ):



        status = get_system_status()



        return {


            "success": True,


            "message":

            (
                f"Your CPU usage is {status['cpu']}. "
                f"RAM usage is {status['ram']}. "
                f"Battery is {status['battery']}, sir."
            )

        }








    # OPEN WEBSITES

    for name, url in COMMANDS.items():


        if (

            name in text

            and

            (
                "open" in text

                or "launch" in text

            )

        ):


            webbrowser.open(url)



            return {


                "success": True,


                "message":
                f"Opening {name}, sir."

            }








    # CALCULATOR

    if "calculator" in text:


        os.system(
            "start calc"
        )


        return {


            "success": True,


            "message":
            "Opening calculator, sir."

        }








    # NOTEPAD

    if "notepad" in text:


        os.system(
            "start notepad"
        )


        return {


            "success": True,


            "message":
            "Opening notepad, sir."

        }








    return {


        "success": False,


        "message":
        "I don't know how to do that yet, sir."

    }