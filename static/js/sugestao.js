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
      
      fetch("/enviar_sugestao/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(dados)
      })
      .then(res => res.json())
      .then(data => {
        mostrarToast();
        form.reset();
      })
      .catch(err =>{
        console.error("Erro",err);
        alert("Erro ao enviar sugestão ❌");
      })
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