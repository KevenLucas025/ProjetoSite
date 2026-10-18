
document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("formSugestao");
    const btnEnviar = document.getElementById("btnEnviar");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (btnEnviar.disabled) return;

            const textoBtn = btnEnviar.querySelector(".texto-btn");

            const dados = {
                assunto: document.getElementById("assunto").value,
                nome: document.getElementById("nome").value,
                email: document.getElementById("email").value,
                mensagem: document.getElementById("mensagem").value
            };

            // Ativa a animação
            btnEnviar.disabled = true;
            btnEnviar.classList.add("enviando");
            textoBtn.textContent = "Enviando";

            try {
                console.log("Enviando pro Django:", dados);
                console.log("CSRF Token:", getCookie("csrftoken"));

                const res = await fetch("/enviar_sugestao/", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify(dados)
                });

                console.log("Status da resposta:", res.status);

                const data = await res.json();

                console.log("Resposta do backend:", data);

                if (!res.ok || data.status !== "ok") {
                    throw new Error(
                        data.mensagem || "Não foi possível enviar a sugestão."
                    );
                }

                mostrarToast();
                form.reset();

            } catch (err) {
                console.error("Erro completo:", err);
                alert("Erro ao enviar sugestão.\n" + err.message);

            } finally {
                // Restaura o botão mesmo se ocorrer um erro
                btnEnviar.disabled = false;
                btnEnviar.classList.remove("enviando");
                textoBtn.textContent = "Enviar";
            }
        });
    }

});

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}

function mostrarToast() {
    const toast = document.getElementById("toast");

    if (!toast) return;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}
