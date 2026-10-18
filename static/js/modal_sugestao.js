
document.addEventListener("DOMContentLoaded", () => {

    const btnSugestao = document.getElementById("btnSugestao");
    const btnSugestaoMobile = document.getElementById("btnSugestaoMobile");

    const modal = document.getElementById("modalSugestao");
    const btnFechar = document.getElementById("fecharSugestao");

    function abrirModal(e) {
        e.preventDefault();

        if (!modal) return;

        modal.classList.add("ativo");
        document.body.classList.add("modal-open");

        btnFechar?.focus();
    }

    function fecharModalSugestao() {
        if (!modal) return;

        modal.classList.remove("ativo");
        document.body.classList.remove("modal-open");
    }

    // Abrir pelo botão desktop
    btnSugestao?.addEventListener("click", abrirModal);

    // Abrir pelo botão mobile
    btnSugestaoMobile?.addEventListener("click", abrirModal);

    // Fechar pelo X
    btnFechar?.addEventListener("click", fecharModalSugestao);

    // Fechar pelo botão Cancelar
    document.querySelector("#modalSugestao .btn-cancelar")
        ?.addEventListener("click", fecharModalSugestao);

    // Fechar clicando fora do conteúdo
    modal?.addEventListener("click", (e) => {
        if (e.target === modal) {
            fecharModalSugestao();
        }
    });

    // Fechar com ESC
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal?.classList.contains("ativo")) {
            fecharModalSugestao();
        }
    });

});
