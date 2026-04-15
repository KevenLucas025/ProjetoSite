document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("formSugestao");

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();

      const dados = {
        assunto: document.getElementById("assunto").value,
        nome: document.getElementById("nome").value,
        email: document.getElementById("email").value,
        mensagem: document.getElementById("mensagem").value
      };

      console.log("Enviando pro Django:", dados);
      console.log("CSRF Token:", getCookie("csrftoken"));

      fetch("/enviar_sugestao/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(dados)
      })
      .then(res => {
        console.log("Status da resposta:", res.status);

        if (!res.ok) {
          return res.json().then(err => {
            throw new Error(err.erro || "Erro desconhecido");
          });
        }
        return res.json();
      })
      .then(data => {
        console.log("Resposta do backend:", data);

        if (data.status === "ok") {
          mostrarToast();
          form.reset();
        } else {
          throw new Error("Erro retornado pelo servidor");
        }
      })
      .catch(err => {
        console.error("Erro completo:", err.message);
        alert("Erro ao enviar sugestão ❌\n" + err.message);
      });

    });
  }

});

function getCookie(name){
  let cookieValue = null;
  if (document.cookie && document.cookie !== ""){
    const cookies = document.cookie.split(";");
    for (let cookie of cookies){
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = cookie.substring(name.length + 1);
        break;
      }
    }
  }
  return cookieValue;
}

function mostrarToast() {
  const toast = document.getElementById("toast");
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}