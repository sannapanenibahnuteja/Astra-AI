import os
import shutil
import subprocess
from send2trash import send2trash


USER = os.path.expanduser("~")

FOLDERS = {
    "desktop": os.path.join(USER, "Desktop"),
    "documents": os.path.join(USER, "Documents"),
    "downloads": os.path.join(USER, "Downloads"),
    "pictures": os.path.join(USER, "Pictures"),
    "music": os.path.join(USER, "Music"),
    "videos": os.path.join(USER, "Videos"),
}


def open_folder(name):

    path = FOLDERS.get(name.lower())

    if not path or not os.path.exists(path):
        return {
            "success": False,
            "message": "Unknown folder."
        }

    subprocess.Popen(["explorer", path])

    return {
        "success": True,
        "message": f"Opening {name}."
    }


def list_folder(name):

    path = FOLDERS.get(name.lower())

    if not path:
        return {
            "success": False,
            "message": "Unknown folder."
        }

    try:

        return {
            "success": True,
            "files": sorted(os.listdir(path)),
            "message": f"{len(os.listdir(path))} items found."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


def search_file(filename):

    filename = filename.lower()

    matches = []

    for root, _, files in os.walk(USER):

        for file in files:

            if filename in file.lower():

                matches.append(os.path.join(root, file))

    if not matches:

        return {
            "success": False,
            "message": "File not found."
        }

    return {
        "success": True,
        "path": matches[0],
        "matches": matches,
        "count": len(matches),
        "message": f"Found {len(matches)} matching file(s)."
    }


def open_file(filename):

    result = search_file(filename)

    if not result["success"]:
        return result

    os.startfile(result["path"])

    return {
        "success": True,
        "message": "Opening file."
    }


def reveal_file(filename):

    result = search_file(filename)

    if not result["success"]:
        return result

    subprocess.Popen([
        "explorer",
        "/select,",
        result["path"]
    ])

    return {
        "success": True,
        "message": "Showing file."
    }


def delete_file(filename):

    result = search_file(filename)

    if not result["success"]:
        return result

    try:

        send2trash(result["path"])

        return {
            "success": True,
            "message": "File moved to Recycle Bin."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


def create_folder(name, location="desktop"):

    base = FOLDERS.get(location.lower())

    if not base:
        return {
            "success": False,
            "message": "Unknown location."
        }

    path = os.path.join(base, name)

    try:

        os.makedirs(path, exist_ok=True)

        return {
            "success": True,
            "path": path,
            "message": "Folder created."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


def rename_file(old_name, new_name):

    result = search_file(old_name)

    if not result["success"]:
        return result

    old_path = result["path"]

    directory = os.path.dirname(old_path)

    extension = os.path.splitext(old_path)[1]

    new_path = os.path.join(directory, new_name + extension)

    try:

        os.rename(old_path, new_path)

        return {
            "success": True,
            "message": "File renamed."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


def move_file(filename, destination):

    result = search_file(filename)

    if not result["success"]:
        return result

    dest = FOLDERS.get(destination.lower())

    if not dest:
        return {
            "success": False,
            "message": "Unknown destination."
        }

    try:

        shutil.move(result["path"], dest)

        return {
            "success": True,
            "message": "File moved."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


def copy_file(filename, destination):

    result = search_file(filename)

    if not result["success"]:
        return result

    dest = FOLDERS.get(destination.lower())

    if not dest:
        return {
            "success": False,
            "message": "Unknown destination."
        }

    try:

        shutil.copy2(result["path"], dest)

        return {
            "success": True,
            "message": "File copied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }