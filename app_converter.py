import sys
import os
import queue
import threading
import colorsys
from pathlib import Path
import warnings
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from markitdown import MarkItDown

if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

warnings.filterwarnings("ignore")

# Tema Clean Moderno
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AppDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, master, resultados_sucesso):
        super().__init__(master)
        self.title("📄 Resultados - MarkItDown")
        self.geometry("900x650")
        self.minsize(750, 500)
        self.configure(fg_color="#F5F7FA")
        
        self.focus()
        self.after(100, lambda: self.attributes('-topmost', False))

        self.resultados = resultados_sucesso
        self.arquivos_nomes = list(self.resultados.keys())
        self.arquivo_atual = self.arquivos_nomes[0]

        self._construir_interface()
        self._carregar_conteudo(self.arquivo_atual)

    def _construir_interface(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top_frame, text="VISUALIZANDO:", font=ctk.CTkFont(weight="bold", size=12), text_color="#34495E").pack(side="left", padx=(0, 10))

        self.combo_seletor = ctk.CTkOptionMenu(
            top_frame, values=self.arquivos_nomes, command=self._carregar_conteudo, width=280,
            fg_color="#FFFFFF", text_color="#2C3E50", button_color="#E0E6ED", button_hover_color="#D1D8E0"
        )
        self.combo_seletor.pack(side="left")

        ctk.CTkButton(
            top_frame, text="📥 SALVAR TODOS", fg_color="#E67E22", hover_color="#D35400", text_color="white",
            font=ctk.CTkFont(weight="bold", size=12), corner_radius=8, command=self._exportar_todos
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            top_frame, text="💾 SALVAR ESTE", fg_color="#27AE60", hover_color="#2ECC71", text_color="white",
            font=ctk.CTkFont(weight="bold", size=12), corner_radius=8, command=self._exportar_atual
        ).pack(side="right", padx=5)

        self.text_box = ctk.CTkTextbox(
            self, wrap="word", font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#FFFFFF", text_color="#2C3E50", border_width=1, border_color="#BDC3C7", corner_radius=10
        )
        self.text_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _carregar_conteudo(self, nome_arquivo):
        self.arquivo_atual = nome_arquivo
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", self.resultados[nome_arquivo])
        self.text_box.configure(state="disabled")

    def _exportar_atual(self):
        conteudo = self.resultados[self.arquivo_atual]
        caminho = filedialog.asksaveasfilename(
            title="Salvar Arquivo", defaultextension=".md", initialfile=f"descricao_{Path(self.arquivo_atual).stem}.md", filetypes=[("Markdown", "*.md")]
        )
        if caminho:
            try:
                Path(caminho).write_text(conteudo, encoding="utf-8")
                if messagebox.askyesno("Sucesso", "Arquivo salvo! Deseja abrir a pasta?"): os.startfile(Path(caminho).parent)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar:\n{e}")

    def _exportar_todos(self):
        pasta = filedialog.askdirectory(title="Escolha a pasta destino")
        if pasta:
            try:
                for nome, conteudo in self.resultados.items():
                    (Path(pasta) / f"descricao_{Path(nome).stem}.md").write_text(conteudo, encoding="utf-8")
                if messagebox.askyesno("Sucesso", "Arquivos salvos! Abrir pasta?"): os.startfile(pasta)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha no salvamento:\n{e}")


class MarkItDownProApp(AppDnD):
    def __init__(self):
        super().__init__()
        
        self.title("MarkItDown - Clean RGB Edition")
        self.geometry("1000x750")
        self.minsize(900, 650)
        self.configure(fg_color="#F0F3F5")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

      
        self.menu_aberto = True
        self.largura_sidebar = 260 
        
        self.arquivos_fila = []
        self.widgets_arquivos = [] 
        self.fila_mensagens = queue.Queue()
        self.cache_conversao = {}
        self.falhas_registradas = 0

        self._montar_interface()
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._ao_soltar_arquivos)
        
        self._monitorar_processamento()
        self._iniciar_animacao_rgb()

    def _montar_interface(self):

        self.sidebar_frame = ctk.CTkFrame(self, width=self.largura_sidebar, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color="#E0E0E0")
        self.sidebar_frame.grid_propagate(False) 
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MarkItDown", font=ctk.CTkFont(family="Segoe UI Black", size=28, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 0))
        ctk.CTkLabel(self.sidebar_frame, text="ESCRITÓRIO SOUZA FILHO", font=ctk.CTkFont(size=10, weight="bold"), text_color="#7F8C8D").grid(row=1, column=0, pady=(0, 40))

        btn_estilo = {"height": 45, "font": ctk.CTkFont(weight="bold", size=13), "corner_radius": 8, "fg_color": "#F8F9FA", "text_color": "#2C3E50", "hover_color": "#E9ECEF", "border_width": 1, "border_color": "#D5D8DC"}
        
        ctk.CTkButton(self.sidebar_frame, text="📄 Adicionar Arquivos", command=self._selecionar_arquivos, **btn_estilo).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="📂 Adicionar Pasta", command=self._selecionar_pasta, **btn_estilo).grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.sidebar_frame, text="Arraste arquivos p/ a tela", text_color="#95A5A6", font=ctk.CTkFont(size=11, slant="italic")).grid(row=4, column=0, pady=15)

        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=25, pady=20)
        self.main_area.grid_rowconfigure(2, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(self.main_area, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.btn_menu = ctk.CTkButton(
            top_bar, text="☰ Menu", width=80, height=35, fg_color="#FFFFFF", text_color="#2C3E50",
            hover_color="#E0E6ED", border_width=1, border_color="#D5D8DC", font=ctk.CTkFont(weight="bold"),
            command=self._alternar_menu
        )
        self.btn_menu.pack(side="left")

        self.cb_todos = ctk.CTkCheckBox(
            top_bar, text="Selecionar Todos", font=ctk.CTkFont(weight="bold", size=13), 
            text_color="#2C3E50", fg_color="#3498DB", hover_color="#2980B9", command=self._marcar_todos
        )
        self.cb_todos.pack(side="right")

        self.scroll_lista = ctk.CTkScrollableFrame(self.main_area, corner_radius=12, fg_color="#FFFFFF", border_width=1, border_color="#E5E7E9")
        self.scroll_lista.grid(row=2, column=0, sticky="nsew", pady=(0, 20))

     
        self.borda_rgb_botao = ctk.CTkFrame(self.main_area, corner_radius=10)
        self.borda_rgb_botao.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        self.btn_iniciar = ctk.CTkButton(
            self.borda_rgb_botao, text="⚡ INICIAR CONVERSÃO", height=50, 
            font=ctk.CTkFont(family="Segoe UI Black", size=15), fg_color="#FFFFFF", hover_color="#F1F3F5", text_color="#2C3E50",
            corner_radius=8, command=self._iniciar_motor
        )
        self.btn_iniciar.pack(padx=3, pady=3, expand=True, fill="x")

        self.barra_progresso = ctk.CTkProgressBar(self.main_area, height=6, corner_radius=3, fg_color="#E0E0E0")
        self.barra_progresso.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        self.barra_progresso.set(0)

        self.terminal = ctk.CTkTextbox(
            self.main_area, height=130, corner_radius=10, fg_color="#FFFFFF", border_width=1, 
            border_color="#D5D8DC", text_color="#34495E", font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.terminal.grid(row=5, column=0, sticky="ew")
        self.terminal.configure(state="disabled")


    def _alternar_menu(self):
        """Gatilho que decide se o menu vai abrir ou fechar."""
        if self.menu_aberto:
            self._animar_sidebar(largura_alvo=0)
            self.menu_aberto = False
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew") 
            self._animar_sidebar(largura_alvo=260)
            self.menu_aberto = True

    def _animar_sidebar(self, largura_alvo):
        """Redimensiona o menu pixel por pixel criando um efeito visual de deslize."""
        passo_animacao = 25 
        if self.largura_sidebar < largura_alvo:
            
            self.largura_sidebar = min(self.largura_sidebar + passo_animacao, largura_alvo)
            self.sidebar_frame.configure(width=self.largura_sidebar)
            
            if self.largura_sidebar < largura_alvo:
                self.after(10, lambda: self._animar_sidebar(largura_alvo)) 
                
        elif self.largura_sidebar > largura_alvo:
            
            self.largura_sidebar = max(self.largura_sidebar - passo_animacao, largura_alvo)
            self.sidebar_frame.configure(width=self.largura_sidebar)
            
            if self.largura_sidebar > largura_alvo:
                self.after(10, lambda: self._animar_sidebar(largura_alvo))
            else:
                
                if largura_alvo == 0:
                    self.sidebar_frame.grid_remove()


    def _iniciar_animacao_rgb(self, hue=0.0):
        try:
            r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 0.85) 
            cor_hex = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            
            self.logo_label.configure(text_color=cor_hex)
            self.borda_rgb_botao.configure(fg_color=cor_hex)
            self.barra_progresso.configure(progress_color=cor_hex)
            
            novo_hue = (hue + 0.005) % 1.0 
            self.after(50, self._iniciar_animacao_rgb, novo_hue)
        except:
            pass 


    def _log(self, texto):
        self.terminal.configure(state="normal")
        self.terminal.insert("end", texto + "\n")
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def _obter_arquivos_validos(self, caminhos):
        extensoes = {'.xlsx', '.xlsm', '.xls', '.docx', '.pdf'}
        return [Path(p) for p in caminhos if Path(p).is_file() and Path(p).suffix.lower() in extensoes and not Path(p).name.startswith('~$')]

    def _atualizar_lista_visual(self):
        for item in self.widgets_arquivos: item['cb'].destroy()
        self.widgets_arquivos.clear()
        self.cb_todos.select()
        
        for arq in self.arquivos_fila:
            cb = ctk.CTkCheckBox(self.scroll_lista, text=arq.name, font=ctk.CTkFont(size=13), text_color="#2C3E50", fg_color="#3498DB", hover_color="#2980B9")
            cb.pack(anchor="w", pady=6, padx=15)
            cb.select()
            self.widgets_arquivos.append({'cb': cb, 'path': arq})

    def _selecionar_arquivos(self):
        paths = filedialog.askopenfilenames(filetypes=[("Documentos Suportados", "*.pdf *.docx *.xlsx *.xlsm *.xls")])
        if paths:
            self.arquivos_fila.extend([p for p in self._obter_arquivos_validos(paths) if p not in self.arquivos_fila])
            self._atualizar_lista_visual()

    def _selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.arquivos_fila.clear()
            self.arquivos_fila.extend(self._obter_arquivos_validos(Path(pasta).iterdir()))
            self._atualizar_lista_visual()

    def _ao_soltar_arquivos(self, event):
        paths = self.tk.splitlist(event.data)
        self.arquivos_fila.extend([p for p in self._obter_arquivos_validos(paths) if p not in self.arquivos_fila])
        self._atualizar_lista_visual()

    def _marcar_todos(self):
        estado = self.cb_todos.get()
        for item in self.widgets_arquivos: item['cb'].select() if estado == 1 else item['cb'].deselect()

    def _monitorar_processamento(self):
        while not self.fila_mensagens.empty():
            msg = self.fila_mensagens.get()
            acao = msg.get('acao')

            if acao == 'log': self._log(msg['texto'])
            elif acao == 'progresso': self.barra_progresso.set(msg['valor'])
            elif acao == 'sucesso':
                widget = msg['cb']
                widget.configure(text=f"{widget.cget('text')} ✔", text_color="#27AE60")
                self.cache_conversao[msg['nome']] = msg['conteudo']
            elif acao == 'falha_visual':
                widget = msg['cb']
                widget.configure(text=f"{widget.cget('text')} ✖", text_color="#C0392B")
                self.falhas_registradas += 1
            elif acao == 'fim_processo':
                self._finalizar_conversao()

        self.after(100, self._monitorar_processamento) 

    def _iniciar_motor(self):
        alvos = [item for item in self.widgets_arquivos if item['cb'].get() == 1]
        if not alvos: return

        self.btn_iniciar.configure(state="disabled", text="⚡ PROCESSANDO ARQUIVOS...")
        self.cache_conversao.clear()
        self.falhas_registradas = 0
        
        self._log("\n• " + "-"*50)
        self._log(f"🚀 Iniciando processo para {len(alvos)} arquivo(s).")
        threading.Thread(target=self._processamento_background, args=(alvos,), daemon=True).start()

    def _processamento_background(self, lista_alvos):
        total = len(lista_alvos)

        self.fila_mensagens.put({'acao': 'log', 'texto': "⏳ Carregando Inteligência Artificial..."})
        try:
            md = MarkItDown()
        except Exception as e:
            self.fila_mensagens.put({'acao': 'log', 'texto': f"✖ ERRO FATAL AO INICIAR MOTOR: {e}"})
            self.fila_mensagens.put({'acao': 'fim_processo'})
            return

        for idx, item in enumerate(lista_alvos, start=1):
            path_arq = item['path']
            cb_widget = item['cb']
            nome = path_arq.name
            
            self.fila_mensagens.put({'acao': 'log', 'texto': f"\n📄 Lendo: {nome}"})

            try:
                resultado = md.convert(str(path_arq))
                conteudo = resultado.text_content
                
                if conteudo and conteudo.strip():
                    conteudo_final = f"# ARQUIVO FONTE: {nome}\n\n---\n\n{conteudo.strip()}\n"
                    self.fila_mensagens.put({'acao': 'sucesso', 'nome': nome, 'conteudo': conteudo_final, 'cb': cb_widget})
                    self.fila_mensagens.put({'acao': 'log', 'texto': f"   ✔ Arquivo lido com sucesso."})
                else:
                    self.fila_mensagens.put({'acao': 'falha_visual', 'cb': cb_widget})
                    self.fila_mensagens.put({'acao': 'log', 'texto': f"   ⚠ Falha: Arquivo vazio ou ilegível (Imagem sem texto)."})
                    
            except Exception as erro:
                self.fila_mensagens.put({'acao': 'falha_visual', 'cb': cb_widget})
                self.fila_mensagens.put({'acao': 'log', 'texto': f"   ✖ ERRO: {erro}"})

            self.fila_mensagens.put({'acao': 'progresso', 'valor': idx / total})

        self.fila_mensagens.put({'acao': 'log', 'texto': "\n✨ Processo Concluído!" + "-"*50})
        self.fila_mensagens.put({'acao': 'fim_processo'})

    def _finalizar_conversao(self):
        self.btn_iniciar.configure(state="normal", text="⚡ INICIAR CONVERSÃO")
        self.barra_progresso.set(0)

        if not self.cache_conversao:
            if self.falhas_registradas > 0:
                messagebox.showerror("Erro na Conversão", "Nenhum arquivo retornou texto.\nIsto ocorre se o PDF for escaneado (apenas imagens) ou estiver protegido.")
            return

        PreviewWindow(self, self.cache_conversao)

if __name__ == "__main__":
    app = MarkItDownProApp()
    app.mainloop()