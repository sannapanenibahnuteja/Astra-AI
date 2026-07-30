from app.services import file_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }
import os

class FileHandler:
    print("FILE HANDLER:", os.path.abspath(__file__))

    FILE_ACTIONS = {
        "open",
        "find",
        "search_file",
        "open_file",
        "delete_file",
        "rename_file",
        "copy_file",
        "move_file",
        "create_folder",
        "show_folder",
        "recent_files",
    }

    FOLDER_TARGETS = {
        "desktop",
        "documents",
        "downloads",
        "pictures",
        "videos",
        "music",
        "recycle bin",
    }

    def handle(self, action, target, value, query=None):

        if action not in self.FILE_ACTIONS:
            return None

        # -------------------------
        # Open Windows folders
        # -------------------------

        if action == "open" and target in self.FOLDER_TARGETS:

            if file_manager.show_folder(target):
                return response(True, f"Opening {target}.")

            return response(False, f"Couldn't open {target}.")

        # -------------------------
        # Find File
        # -------------------------

        if action in ("find", "search_file"):

            if not target:
                return response(False, "Which file should I find?")

            result = file_manager.find_file(target)

            if result:
                return response(
                    True,
                    f"Found {target}.",
                    result,
                )

            return response(False, f"Couldn't find {target}.")

        # -------------------------
        # Open File
        # -------------------------

        if action == "open_file":

            if not target:
                return response(False, "Which file should I open?")

            if file_manager.open_file(target):
                return response(True, f"Opening {target}.")

            return response(False, f"Couldn't open {target}.")

        # -------------------------
        # Delete File
        # -------------------------

        if action == "delete_file":

            if not target:
                return response(False, "Which file should I delete?")

            if file_manager.delete_file(target):
                return response(True, f"Deleted {target}.")

            return response(False, f"Couldn't delete {target}.")

        # -------------------------
        # Rename File
        # -------------------------

        if action == "rename_file":

            if not target or not value:
                return response(False, "Need both old and new names.")

            if file_manager.rename_file(target, value):
                return response(
                    True,
                    f"Renamed {target} to {value}.",
                )

            return response(False, "Rename failed.")

        # -------------------------
        # Copy File
        # -------------------------

        if action == "copy_file":

            if not target or not value:
                return response(False, "Source or destination missing.")

            if file_manager.copy_file(target, value):
                return response(True, "File copied.")

            return response(False, "Copy failed.")

        # -------------------------
        # Move File
        # -------------------------

        if action == "move_file":

            if not target or not value:
                return response(False, "Source or destination missing.")

            if file_manager.move_file(target, value):
                return response(True, "File moved.")

            return response(False, "Move failed.")

        # -------------------------
        # Create Folder
        # -------------------------

        if action == "create_folder":

            if not target:
                return response(False, "Folder name missing.")

            if file_manager.create_folder(target):
                return response(
                    True,
                    f"Created folder '{target}'.",
                )

            return response(False, "Couldn't create folder.")

        # -------------------------
        # Show Folder
        # -------------------------

        if action == "show_folder":

            if not target:
                return response(False, "Folder name missing.")

            if file_manager.show_folder(target):
                return response(True, f"Opening {target}.")

            return response(False, "Couldn't open folder.")

        # -------------------------
        # Recent Files
        # -------------------------

        if action == "recent_files":

            files = file_manager.recent_files()

            return response(
                True,
                "Recent files.",
                files,
            )

        return None