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

# Usuários cadastrados (autenticação simulada)
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
    # 🔐 Verifica token
    token = request.headers.get("Authorization")
    if not token or token not in TOKENS:
        return jsonify({"error": "Não autorizado"}), 403

    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    # ✔️ Formato correto exigido pelo SDK da OpenAI
    openai_file = (file.filename, file.stream, file.mimetype)

    # 🎤 1. Transcrição do áudio
    try:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=openai_file
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao transcrever: {str(e)}"}), 500

    text = transcription.text

    # 🤖 2. IA gera resposta em texto
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um consultor agrícola especialista em produtividade rural."},
                {"role": "user", "content": text}
            ]
        )
        ai_text = completion.choices[0].message.content

    except Exception as e:
        return jsonify({"error": f"Erro na IA: {str(e)}"}), 500

    # 🔊 3. Converter texto da IA para áudio (TTS)
    try:
        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=ai_text
        )

        audio_base64 = base64.b64encode(speech.read()).decode("utf-8")

    except Exception as e:
        return jsonify({"error": f"Erro ao gerar áudio: {str(e)}"}), 500

    # 📦 4. Retornar tudo
    return jsonify({
        "transcription": text,
        "ai_text": ai_text,
        "ai_audio": audio_base64
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
