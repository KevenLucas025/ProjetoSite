import os

TERMO = ""
PASTA_PROJETO = r"C:\Users\KevenJesus\Documents\ProjeSite"

for raiz, dirs, arquivos in os.walk(PASTA_PROJETO):
    for arquivo in arquivos:

        if arquivo == "procurar_codigo.py":
            continue

        caminho = os.path.join(raiz, arquivo)

        if arquivo.endswith((
            ".html", ".js", ".jsx", ".ts",
            ".tsx", ".py", ".php", ".vue"
        )):

            print(f"Analisando: {caminho}")

            try:
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    for numero_linha, linha in enumerate(f, start=1):
                        if TERMO.lower() in linha.lower():
                            print("\n====================")
                            print(f"Arquivo: {caminho}")
                            print(f"Linha: {numero_linha}")
                            print(f"Código: {linha.strip()}")

            except Exception as e:
                print(f"Erro: {caminho} -> {e}")