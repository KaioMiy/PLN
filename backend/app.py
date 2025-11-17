import base64
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🚀 CORS TOTALMENTE LIBERADO (funciona no Render)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Usuários cadastrados (autenticação simulada)
USERS = {
    "kaio": "123456",
    "admin": "admin123",
    "demo": "demo"
}

# Tokens armazenados em memória
TOKENS = {}


# -------------------------------
# 🔐 LOGIN
# -------------------------------
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


# -------------------------------
# 🎤 ÁUDIO → TRANSCRIÇÃO → IA → ÁUDIO
# -------------------------------
@app.post("/api/audio")
def process_audio():
    # Validar token
    token = request.headers.get("Authorization")

    if not token or token not in TOKENS:
        return jsonify({"error": "Não autorizado"}), 403

    # Receber arquivo
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    # Formato EXIGIDO pelo novo SDK da OpenAI
    openai_file = (file.filename, file.stream, file.mimetype)

    # 1️⃣ TRANSCRIÇÃO
    try:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=openai_file
        )
        text = transcription.text
    except Exception as e:
        return jsonify({"error": f"Erro ao transcrever áudio: {str(e)}"}), 500

    # 2️⃣ RESPOSTA DA IA
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

    # 3️⃣ CONVERTER TEXTO PARA ÁUDIO (TTS)
    try:
        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=ai_text
        )
        audio_base64 = base64.b64encode(speech.read()).decode("utf-8")
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar áudio: {str(e)}"}), 500

    # 4️⃣ RETORNAR RESULTADO FINAL
    return jsonify({
        "transcription": text,
        "ai_text": ai_text,
        "ai_audio": audio_base64
    })


# -------------------------------
# SERVER LOCAL (para testes)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
