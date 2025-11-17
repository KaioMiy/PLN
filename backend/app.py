import base64
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# "Banco" de usuários simulados
USERS = {
    "kaio": "123456",
    "admin": "admin123",
    "demo": "demo"
}

# Tokens ativos
TOKENS = {}


@app.post("/login")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) == password:
        token = str(uuid.uuid4())
        TOKENS[token] = username

        return jsonify({
            "status": "ok",
            "user": username,
            "token": token
        })

    return jsonify({"error": "Credenciais inválidas"}), 401


@app.post("/api/audio")
def process_audio():
    token = request.headers.get("Authorization")

    # Verificar se o token é válido
    if not token or token not in TOKENS:
        return jsonify({"error": "Não autorizado"}), 403

    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    # 1. Transcrever áudio
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=file
    )

    text = transcription.text

    # 2. Inteligência Artificial responde
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um consultor agrícola especialista em produtividade rural."},
            {"role": "user", "content": text}
        ]
    )

    ai_text = completion.choices[0].message.content

    # 3. Converter resposta da IA em áudio
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=ai_text
    )

    audio_base64 = base64.b64encode(speech.read()).decode("utf-8")

    return jsonify({
        "transcription": text,
        "ai_text": ai_text,
        "ai_audio": audio_base64
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
