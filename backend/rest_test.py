import requests

API_KEY = "YOUR_NEW_API_KEY"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Say hello"
                }
            ]
        }
    ]
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print(response.text)