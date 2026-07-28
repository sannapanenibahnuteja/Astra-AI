from app.services.ai_service import stream_astra

print("Starting stream...\n")

for chunk in stream_astra("Write a 100 word story about Mars."):
    print(repr(chunk), end="", flush=True)

print("\n\nDone.")