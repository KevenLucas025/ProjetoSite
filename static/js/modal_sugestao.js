document.addEventListener("DOMContentLoaded", () => {

  const btnSugestao = document.getElementById("btnSugestao");
  const btnSugestaoMobile = document.getElementById("btnSugestaoMobile");
  const modal = document.getElementById("modalSugestao");
  const fechar = document.getElementById("fecharSugestao");
  const form = document.getElementById("formSugestao");

  const botao = document.getElementById("btnEnviar");
  const texto = botao?.querySelector(".texto-btn");
  const spinner = botao?.querySelector(".spinner");

  function abrirModal(e) {
    e.preventDefault();

    modal.classList.add("ativo");

    // 🔥 TRAVA O BODY (AQUI É O QUE VOCÊ PRECISA)
    document.body.classList.add("modal-open");

    // limpa formulário ao abrir
    if (form) form.reset();

    // reseta botão (caso tenha dado erro antes)
    if (botao && texto && spinner) {
      botao.disabled = false;
      texto.innerText = "Enviar";
      spinner.style.display = "none";
    }
  }

  function fecharModal() {
    modal.classList.remove("ativo");

    // 🔥 libera o body quando fecha
    document.body.classList.remove("modal-open");
  }

  if (btnSugestao && modal) {
    btnSugestao.addEventListener("click", abrirModal);
  }

  if (btnSugestaoMobile && modal) {
    btnSugestaoMobile.addEventListener("click", abrirModal);
  }

  if (fechar && modal) {
    fechar.addEventListener("click", fecharModal);
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        fecharModal();
      }
    });
  }

  if (form) {
    form.addEventListener("submit", () => {
        if (botao && texto && spinner){
            botao.disabled = true;
            botao.classList.add("enviando");
            texto.innerText = "Enviando";
            spinner.style.display = "block";
        } 

        setTimeout(() => {
            botao.disabled = false;
            botao.classList.remove("enviando");
            texto.innerText = "Enviar";
            spinner.style.display = "none";
        }, 3000);
    });
  }

});