import warnings
from pathlib import Path
from markitdown import MarkItDown


warnings.filterwarnings("ignore", category=UserWarning)


def listar_arquivos_suportados(pasta_origem: str = ".") -> list[Path]:
    """Lista todos os arquivos compatíveis na pasta usando pathlib."""
    extensoes = {'.xlsx', '.xlsm', '.xls', '.docx', '.pdf'}
    pasta = Path(pasta_origem)
    
    return [
        f for f in pasta.iterdir() 
        if f.is_file() and f.suffix.lower() in extensoes and not f.name.startswith('~$')
    ]


def gerar_prompt_markdown(arquivo_origem: str, conteudo: str, caminho_saida: Path) -> None:
    """Gera o arquivo com Markdown nativo renderizável."""
    conteudo_limpo = (
        f"# ARQUIVO FONTE: {arquivo_origem}\n\n"
        f"---\n\n"
        f"{conteudo.strip()}\n"
    )

    
    caminho_saida.write_text(conteudo_limpo, encoding="utf-8")


def auditoria_automatica(lista_arquivos: list[Path]) -> None:
    """Executa a verificação automatizada logo após o término da conversão."""
    print("\n" + "="*50)
    print("🔍 AUDITORIA AUTOMÁTICA DE INTEGRIDADE")
    print("="*50)

    sucessos = 0
    faltantes = 0
    vazios = 0

    for arq in lista_arquivos:
        
        caminho_md = Path(f"descricao_{arq.stem}.md")

        if not caminho_md.exists():
            print(f"❌ AUSENTE: '{arq.name}' -> Não gerou '{caminho_md.name}'.")
            faltantes += 1
            continue

        tamanho_bytes = caminho_md.stat().st_size
        if tamanho_bytes == 0:
            print(f"⚠️ VAZIO: '{caminho_md.name}' está com 0 bytes.")
            vazios += 1
            continue

        print(f"✅ OK: '{arq.name}' -> Validado ({tamanho_bytes} bytes)")
        sucessos += 1

    total = len(lista_arquivos)
    print("-" * 50)
    print(f"📊 RESUMO: {sucessos}/{total} validados com sucesso.")
    if faltantes > 0 or vazios > 0:
        print(f"⚠️ Alerta: {faltantes} ausentes, {vazios} vazios.")
    print("="*50 + "\n")



def converter_arquivos(lista_arquivos: list[Path], executar_auditoria: bool = False) -> None:
    """Processa e salva os arquivos diretamente na raiz."""
    md = MarkItDown()
    print("\nConvertendo...")

    for arq in lista_arquivos:
        caminho_saida = Path(f"descricao_{arq.stem}.md")
        
        try:
            resultado = md.convert(str(arq))
            conteudo = resultado.text_content
            
            
            if not conteudo or not conteudo.strip():
                print(f"⚠️ AVISO em {arq.name}: O arquivo original parece estar vazio ou não pôde ser lido.")
                continue

            gerar_prompt_markdown(arq.name, conteudo, caminho_saida)
            print(f"✔ Criado: {caminho_saida.name}")
            
        except Exception as e:
            print(f"✖ Erro em {arq.name}: {e}")

    if executar_auditoria:
        auditoria_automatica(lista_arquivos)



def menu_principal() -> None:
    """Exibe o menu iterativo em um loop contínuo."""
    while True:
        arquivos = listar_arquivos_suportados()

        if not arquivos:
            print("Nenhum arquivo compatível encontrado na pasta.")
            break

        print("\n--- CONVERSOR MARKITDOWN ---")
        print("1. Converter TODOS os arquivos (com verificação)")
        print("2. Escolher UM arquivo (com verificação)")
        print("0. Sair")

        opcao = input("\nOpção: ").strip()

        if opcao == '1':
            converter_arquivos(arquivos, executar_auditoria=True)

        elif opcao == '2':
            print("\nArquivos disponíveis:")
            for i, arq in enumerate(arquivos, start=1):
                print(f"[{i}] {arq.name}")
            
            escolha = input("\nEscolha o número (ou pressione Enter para cancelar): ").strip()
            
            if escolha.isdigit() and 1 <= int(escolha) <= len(arquivos):
               
                converter_arquivos([arquivos[int(escolha) - 1]], executar_auditoria=True)
            else:
                print("Opção inválida ou cancelada.")

        elif opcao == '0':
            print("Saindo do programa... Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()