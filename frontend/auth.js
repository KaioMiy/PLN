// Backend URL depois do deploy no Render
const API_BASE = "https://pln.onrender.com";
;
// depois você troca para:
// const API_BASE = "https://seu-backend.onrender.com";

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", data.user);
        window.location.href = "dashboard.html";
    } else {
        alert("Usuário ou senha inválidos");
    }
}

function getToken() {
    return localStorage.getItem("token");
}
