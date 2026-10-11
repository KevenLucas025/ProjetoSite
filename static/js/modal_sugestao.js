
document.addEventListener("DOMContentLoaded", () => {

    const btnSugestao = document.getElementById("btnSugestao");
    const btnSugestaoMobile = document.getElementById("btnSugestaoMobile");

    const modal = document.getElementById("modalIndisponibilidade");
    const btnFechar = document.getElementById("fecharIndisponibilidade");
    const btnFecharRodape = document.getElementById("btnFecharIndisponibilidade");
    const btnContato = document.getElementById("btnIrContato");

    function abrirModal(e) {
        e.preventDefault();

        if (!modal) return;

        modal.classList.add("ativo");
        document.body.classList.add("modal-open");

        btnFechar?.focus();
    }

    function fecharModal() {
        if (!modal) return;

        modal.classList.remove("ativo");
        document.body.classList.remove("modal-open");
    }

    // Desktop
    btnSugestao?.addEventListener("click", abrirModal);

    // Celular
    btnSugestaoMobile?.addEventListener("click", abrirModal);

    // Botões para fechar
    btnFechar?.addEventListener("click", fecharModal);
    btnFecharRodape?.addEventListener("click", fecharModal);

    // Fechar clicando no fundo
    modal?.addEventListener("click", (e) => {
        if (e.target === modal) {
            fecharModal();
        }
    });

    // Fechar com ESC
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal?.classList.contains("ativo")) {
            fecharModal();
        }
    });

    // Ir para a seção Contato
    
  
  btnContato?.addEventListener("click", () => {
      fecharModal();

      window.location.href = "/contato/";
  });



});
