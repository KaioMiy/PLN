let mediaRecorder;
let chunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const player = document.getElementById("player");


startBtn.onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    chunks = [];

    mediaRecorder.ondataavailable = e => chunks.push(e.data);

    startBtn.disabled = true;
    stopBtn.disabled = false;
};

stopBtn.onclick = () => {
    mediaRecorder.stop();

    mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/webm" });

        const formData = new FormData();
        formData.append("file", blob, "audio.webm");

        const response = await fetch(`${API_BASE}/api/audio`, {
            method: "POST",
            headers: {
                "Authorization": getToken()
            },
            body: formData
        });

        const data = await response.json();

        if (data.ai_audio) {
            player.src = "data:audio/mp3;base64," + data.ai_audio;
        }

        startBtn.disabled = false;
        stopBtn.disabled = true;
    };
};

