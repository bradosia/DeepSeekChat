# python_interface.py
import requests
import json
import sys

def send_query(user_input):
    url = "https://api.gmi-serving.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY_HERE"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()["choices"][0]["message"]["content"]
        print(result)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    user_input = sys.argv[1]
    send_query(user_input)
