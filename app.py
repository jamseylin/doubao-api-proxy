from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# 从环境变量读取密钥（Render 里设置）
ARK_API_KEY = os.environ.get("ARK_API_KEY")
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_MODEL = os.environ.get("ARK_MODEL")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])

    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": ARK_MODEL,
        "messages": messages,
        "stream": True
    }

    def generate():
        try:
            response = requests.post(
                f"{ARK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    if line.strip() == "data: [DONE]":
                        break
                    yield line + "\n"
        except Exception as e:
            yield f"data: {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
