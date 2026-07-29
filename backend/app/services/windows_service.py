import subprocess



pending_updates = []





def run_powershell(command):

    result = subprocess.run(

        [
            "powershell",

            "-ExecutionPolicy",

            "Bypass",

            "-Command",

            command
        ],

        capture_output=True,

        text=True

    )


    return (
        result.stdout.strip(),
        result.stderr.strip()
    )







def check_windows_updates():

    global pending_updates


    command = r"""

    $session = New-Object -ComObject Microsoft.Update.Session

    $searcher = $session.CreateUpdateSearcher()

    $result = $searcher.Search("IsInstalled=0 and Type='Software'")


    foreach($update in $result.Updates)
    {

        Write-Output $update.Title

    }

    """



    output, error = run_powershell(command)



    updates = [

        x.strip()

        for x in output.splitlines()

        if x.strip()

    ]



    pending_updates = updates



    if updates:


        return {

            "success": True,

            "message":
            (
                f"I found {len(updates)} updates available, sir. "
                "Would you like to know what they are?"
            )

        }




    return {

        "success": True,

        "message":
        "Your Windows is up to date, sir."

    }








def get_update_details():


    if not pending_updates:


        return {

            "success": True,

            "message":
            "I do not have any pending update information, sir."

        }




    message = "The available updates are: "



    for index, update in enumerate(

        pending_updates,

        start=1

    ):

        message += f"{index}. {update}. "



    message += (
        "Would you like me to install them?"
    )



    return {

        "success": True,

        "message": message

    }








def install_windows_updates():

    command = r"""
    Start-Process powershell `
    -Verb RunAs `
    -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"Import-Module PSWindowsUpdate; Install-WindowsUpdate -AcceptAll -IgnoreReboot`" 
    """


    subprocess.Popen(

        [
            "powershell",
            "-Command",
            command
        ]

    )


    return {

        "success": True,

        "message":
        (
            "Administrator permission requested. "
            "Please approve the Windows permission prompt, sir."
        )

    }