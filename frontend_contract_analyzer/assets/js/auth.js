// auth.js
const apiBaseUrl = "http://localhost:8000"; // URL da sua API FastAPI


document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch(`${apiBaseUrl}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (res.ok) {
            const data = await res.json();
            // Salvar token no localStorage
            localStorage.setItem("accessToken", data.access_token);
            window.location.href = "contracts.html";
        } else {
            alert("Falha no login. Verifique suas credenciais.");
        }
    } catch (err) {
        console.error(err);
        alert("Erro ao conectar com o servidor.");
    }
});


document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const full_name = document.getElementById("fullName").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch(`${apiBaseUrl}/users/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                full_name: full_name,
                email: email,
                password: password
            })
        });

        if (res.ok) {
            alert("Cadastro realizado com sucesso!");
            window.location.href = "login.html";
        } else {
            const data = await res.json();
            alert(`Erro no cadastro: ${data.detail || "Tente novamente."}`);
        }
    } catch (err) {
        console.error(err);
        alert("Erro ao conectar com o servidor.");
    }
});