from app.services import media_manager

print("Current:", media_manager.get_volume())

print("Setting:", media_manager.set_volume(10))

print("After:", media_manager.get_volume())