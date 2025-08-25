import customtkinter as ctk
from PIL import Image, ImageTk
import qrcode
import pyperclip
from qr_payloads import *
import platform
import subprocess
from datetime import datetime
try:
    from tkinter import messagebox, filedialog
except ImportError:
    import tkinter.messagebox as messagebox
    import tkinter.filedialog as filedialog

from wifi_utils import get_current_wifi

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class QRApp(ctk.CTk):
    def __init__(self): 
        super().__init__()
        self.title("QR Code Generator Pro")
        self.geometry("1400x900")
        self.minsize(1400, 900)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.colors = {
            'primary': '#6366f1',      # Indigo moderno
            'secondary': '#8b5cf6',    # Purple
            'success': '#10b981',      # Emerald
            'warning': '#f59e0b',      # Amber  
            'danger': '#ef4444',       # Red
            'info': '#06b6d4',         # Cyan
            'dark': '#1e293b',         # Slate dark
            'light': '#f8fafc',        # Slate light
            'accent': '#ec4899'        # Pink
        }

        self.option_var = ctk.StringVar(value="Texto")
        self.entries = {}
        self.qr_img_label = None
        self.last_data = ""
        self.status_label = None
        self.qr_img_pil = None
        self.history = []

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """Configurar estilos personalizados"""
        self.fonts = {
            'title': ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            'subtitle': ctk.CTkFont(family="Segoe UI", size=18, weight="normal"),
            'heading': ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            'subheading': ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            'body': ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),
            'small': ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            'button': ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        }

    def create_widgets(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        main_container.grid_columnconfigure(0, weight=3)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_rowconfigure(1, weight=1)

        self.create_header(main_container)
        self.create_main_content(main_container)
        self.create_footer(main_container)

    def create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, height=60, corner_radius=10, fg_color=["#f1f5f9", "#1e293b"])
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 30))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, pady=5)

        title_label = ctk.CTkLabel(
            title_container,
            text="Gere seu QR Code aqui",
            font=self.fonts['title'],
            text_color=self.colors['primary']
        )
        title_label.pack()

    def create_main_content(self, parent):
        left_panel = ctk.CTkScrollableFrame(
            parent, 
            corner_radius=20,
            fg_color=["#ffffff", "#0f172a"],
            scrollbar_button_color=self.colors['primary'],
            scrollbar_button_hover_color=self.colors['secondary']
        )
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        right_panel = ctk.CTkFrame(
            parent, 
            corner_radius=20,
            fg_color=["#ffffff", "#0f172a"]
        )
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)

    def setup_left_panel(self, panel):
        self.create_section_header(panel, "Tipo de QR Code", "Escolha o tipo de código que deseja gerar")

        type_frame = ctk.CTkFrame(panel, fg_color="transparent")
        type_frame.pack(fill="x", padx=20, pady=(0, 15))

        options = ["Texto", "URL", "Wi-Fi Manual", "Wi-Fi Atual", "Geo", "SMS", "Email", "WhatsApp", "Pix"]
        self.option_menu = ctk.CTkOptionMenu(
            type_frame,
            values=options,
            variable=self.option_var,
            command=self.change_form,
            height=50,
            font=self.fonts['body'],
            dropdown_font=self.fonts['body'],
            fg_color=self.colors['primary'],
            button_color=self.colors['secondary'],
            button_hover_color=self.colors['accent']
        )
        self.option_menu.pack(fill="x")

        self.create_section_header(panel, "Configurações", "Preencha os dados do seu QR code")
        self.inputs_container = ctk.CTkFrame(panel)
        self.inputs_container.pack(fill="x", padx=20, pady=(0, 30))

        self.change_form(self.option_var.get())
        self.create_action_buttons(panel)

    def create_section_header(self, parent, title, description):
        header_frame = ctk.CTkFrame(parent, height=80, corner_radius=15, fg_color=["#e2e8f0", "#334155"])
        header_frame.pack(fill="x", padx=20, pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=self.fonts['heading'],
            text_color=self.colors['primary']
        )
        title_label.pack(pady=(15, 5))

        desc_label = ctk.CTkLabel(
            header_frame,
            text=description,
            font=self.fonts['small'],
            text_color=["#64748b", "#94a3b8"]
        )
        desc_label.pack()

    def create_action_buttons(self, panel):
        actions_frame = ctk.CTkFrame(panel, corner_radius=15, fg_color=["#f8fafc", "#1e293b"])
        actions_frame.pack(fill="x", padx=20, pady=(0, 30))

        self.generate_btn = ctk.CTkButton(
            actions_frame,
            text="Gerar QR Code",
            command=self.generate_qr,
            height=55,
            font=self.fonts['button'],
            corner_radius=15,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        self.generate_btn.pack(fill="x", padx=20, pady=20)

        button_grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        button_grid.pack(fill="x", padx=20, pady=(0, 20))
        button_grid.grid_columnconfigure((0, 1), weight=1)

        self.save_btn = ctk.CTkButton(
            button_grid,
            text="Salvar",
            command=self.save_qr,
            height=45,
            font=self.fonts['body'],
            fg_color=self.colors['success'],
            hover_color="#059669",
            corner_radius=10
        )
        self.save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

        self.copy_btn = ctk.CTkButton(
            button_grid,
            text="Copiar",
            command=self.copy_content,
            height=45,
            font=self.fonts['body'],
            fg_color=self.colors['warning'],
            hover_color="#d97706",
            corner_radius=10
        )
        self.copy_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))

        self.show_data_btn = ctk.CTkButton(
            button_grid,
            text="Ver Dados",
            command=self.show_data,
            height=45,
            font=self.fonts['body'],
            fg_color=self.colors['info'],
            hover_color="#0891b2",
            corner_radius=10
        )
        self.show_data_btn.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

        self.history_btn = ctk.CTkButton(
            button_grid,
            text="Histórico",
            command=self.show_history,
            height=45,
            font=self.fonts['body'],
            fg_color=self.colors['accent'],
            hover_color="#db2777",
            corner_radius=10
        )
        self.history_btn.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))

        self.clear_btn = ctk.CTkButton(
            button_grid,
            text="Limpar Tudo",
            command=self.clear_fields,
            height=40,
            font=self.fonts['body'],
            fg_color=self.colors['danger'],
            hover_color="#dc2626",
            corner_radius=10
        )
        self.clear_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 0))

    def setup_right_panel(self, panel):
        preview_header = ctk.CTkFrame(panel, height=80, corner_radius=15, fg_color=["#e2e8f0", "#334155"])
        preview_header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        preview_header.grid_propagate(False)

        preview_title = ctk.CTkLabel(
            preview_header,
            text="Visualização do QR Code",
            font=self.fonts['heading'],
            text_color=self.colors['primary']
        )
        preview_title.pack(pady=20)

        qr_container = ctk.CTkFrame(panel, corner_radius=20, fg_color=["#f8fafc", "#1e293b"])
        qr_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        qr_container.grid_columnconfigure(0, weight=1)
        qr_container.grid_rowconfigure(0, weight=1)

        qr_display_frame = ctk.CTkFrame(qr_container, corner_radius=15, fg_color="#ffffff")
        qr_display_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=10)
        qr_display_frame.grid_columnconfigure(0, weight=1)
        qr_display_frame.grid_rowconfigure(0, weight=1)

        self.qr_img_label = ctk.CTkLabel(
            qr_display_frame,
            text=" QR Code será exibido aqui\n\n"
                 "1 Selecione um tipo de QR Code\n"
                 "2 Preencha os campos necessários\n" 
                 "3 Clique em 'Gerar QR Code'\n\n"
                 "Seu código aparecerá nesta área",
            font=self.fonts['body'],
            text_color=["#64748b", "#64748b"],
            justify="center"
        )
        self.qr_img_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=15)

        tips_frame = ctk.CTkFrame(qr_container, corner_radius=15, fg_color=["#dbeafe", "#1e40af"])
        tips_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 30))

        tips_label = ctk.CTkLabel(
            tips_frame,
            text="💡 Dica: Após gerar o QR Code, você pode salvá-lo, copiar os dados ou ver o histórico!",
            font=self.fonts['small'],
            text_color=["#1e40af", "#dbeafe"],
            wraplength=350
        )
        tips_label.pack(pady=15)

        self.create_status_bar(panel)

    def create_status_bar(self, panel):
        status_frame = ctk.CTkFrame(panel, height=60, corner_radius=15, fg_color=["#e2e8f0", "#334155"])
        status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        status_frame.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto para gerar códigos QR",
            font=self.fonts['body'],
            text_color=["#64748b", "#94a3b8"]
        )
        self.status_label.pack(pady=15)

    def create_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, height=60, corner_radius=15, fg_color=["#f1f5f9", "#1e293b"])
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(30, 0))
        footer_frame.grid_propagate(False)

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="Feito para facilitar a criação de códigos QR • Versão Pro 2025",
            font=self.fonts['small'],
            text_color=["#64748b", "#94a3b8"]
        )
        footer_label.pack(pady=15)

    def add_entry(self, label, default="", placeholder="", entry_type="normal", state="normal"):
        """Adicionar campo de entrada com estilo melhorado"""
        field_frame = ctk.CTkFrame(self.inputs_container, fg_color="transparent")
        field_frame.pack(fill="x", padx=20, pady=12)
        field_frame.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(
            field_frame,
            text=f"{label}:",
            font=self.fonts['subheading'],
            anchor="w",
            text_color=self.colors['primary']
        )
        lbl.grid(row=0, column=0, sticky="w", pady=(0, 8))

        if entry_type == "textbox":
            entry = ctk.CTkTextbox(
                field_frame,
                height=100,
                font=self.fonts['body'],
                corner_radius=10,
                state=state,
                border_width=2,
                border_color=["#e2e8f0", "#475569"]
            )
            if default:
                entry.insert("1.0", default)
            entry.grid(row=1, column=0, sticky="ew")
        else:
            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text=placeholder or f"Digite {label.lower()}...",
                height=45,
                font=self.fonts['body'],
                corner_radius=10,
                state=state,
                border_width=2,
                border_color=["#e2e8f0", "#475569"]
            )
            if default:
                entry.insert(0, default)
            entry.grid(row=1, column=0, sticky="ew")

        self.entries[label] = entry

    def get_entry_value(self, label):
        """Obter valor do campo de entrada"""
        entry = self.entries[label]
        if isinstance(entry, ctk.CTkTextbox):
            return entry.get("1.0", "end-1c").strip()
        else:
            return entry.get().strip()

    def load_current_wifi(self):
        """Detectar Wi-Fi atual com feedback visual melhorado"""
        try:
            self.status_label.configure(text="Detectando rede Wi-Fi atual...")
            self.update()

            wifi_info = get_current_wifi()
            if wifi_info:
                ssid, password = wifi_info

                if "SSID" in self.entries:
                    self.entries["SSID"].delete(0, "end")
                    self.entries["SSID"].insert(0, ssid)

                if "Senha" in self.entries:
                    self.entries["Senha"].delete(0, "end")
                    if password:
                        self.entries["Senha"].insert(0, password)

                self.status_label.configure(
                    text=f"Wi-Fi detectado: {ssid}",
                    text_color=self.colors['success']
                )
                messagebox.showinfo(
                    "Wi-Fi Detectado", 
                    f"Rede detectada: {ssid}\n Senha: {'***' if password else 'Não disponível'}"
                )
            else:
                self.status_label.configure(
                    text="Não foi possível detectar rede Wi-Fi",
                    text_color=self.colors['warning']
                )
                messagebox.showwarning(
                    "Wi-Fi não detectado",
                    "Não foi possível detectar informações da rede Wi-Fi atual.\n"
                    "Verifique se você está conectado a uma rede ou use a opção 'Wi-Fi Manual'."
                )
        except Exception as e:
            error_msg = f"Erro ao detectar Wi-Fi: {str(e)}"
            self.status_label.configure(text=error_msg, text_color=self.colors['danger'])
            messagebox.showerror("Erro", error_msg)

    def change_form(self, tipo):
        """Alterar formulário com animação suave"""
        for widget in self.inputs_container.winfo_children():
            if widget != self.inputs_container:
                widget.destroy()
        self.entries.clear()
        if tipo == "Texto":
            self.add_entry("Conteúdo", placeholder="Digite seu texto aqui...", entry_type="textbox")

        elif tipo == "URL":
            self.add_entry("Link", placeholder="https://exemplo.com")

        elif tipo == "Wi-Fi Manual":
            self.add_entry("SSID", placeholder="Nome da rede Wi-Fi")
            self.add_entry("Senha", placeholder="Senha da rede")
            self.add_entry("Tipo de Autenticação", "WPA", "WPA, WEP ou NOPASS")
            self.add_entry("Rede Oculta", "false", "true ou false")

        elif tipo == "Wi-Fi Atual":
            detect_frame = ctk.CTkFrame(self.inputs_container, fg_color="transparent")
            detect_frame.pack(fill="x", padx=20, pady=15)

            detect_btn = ctk.CTkButton(
                detect_frame,
                text="Detectar Wi-Fi Atual",
                command=self.load_current_wifi,
                height=50,
                font=self.fonts['button'],
                fg_color=self.colors['info'],
                hover_color="#0891b2",
                corner_radius=15
            )
            detect_btn.pack(fill="x")

            info_label = ctk.CTkLabel(
                detect_frame,
                text="Clique no botão acima para detectar automaticamente\n"
                    "as informações da rede Wi-Fi conectada",
                font=self.fonts['small'],
                text_color=["#64748b", "#94a3b8"],
                justify="center"
            )
            info_label.pack(pady=(10, 0))

            self.add_entry("SSID", state="normal")
            self.add_entry("Senha", state="normal")
            self.add_entry("Tipo de Autenticação", "WPA", "WPA, WEP ou NOPASS")
            self.add_entry("Rede Oculta", "false", "true ou false")

        elif tipo == "Geo":
            self.add_entry("Latitude", placeholder="-23.550520 (coordenada)")
            self.add_entry("Longitude", placeholder="-46.633308 (coordenada)")

        elif tipo == "SMS":
            self.add_entry("Número", placeholder="+5511999999999")
            self.add_entry("Mensagem", placeholder="Sua mensagem aqui...", entry_type="textbox")

        elif tipo == "Email":
            self.add_entry("Destinatário", placeholder="exemplo@email.com")
            self.add_entry("Assunto", placeholder="Assunto do email")
            self.add_entry("Corpo", placeholder="Conteúdo do email...", entry_type="textbox")

        elif tipo == "WhatsApp":
            self.add_entry("Número", placeholder="5511999999999 (sem +)")
            self.add_entry("Mensagem", placeholder="Olá! Como você está?", entry_type="textbox")

        elif tipo == "Pix":
            self.add_entry("Chave Pix", placeholder="email@exemplo.com, CPF ou telefone")
            self.add_entry("Valor", placeholder="0.00")


    def generate_qr(self):
        """Gerar QR Code com feedback visual melhorado"""
        tipo = self.option_var.get()
        data = ""
        
        try:
            self.status_label.configure(
                text="Gerando QR Code...",
                text_color=self.colors['warning']
            )
            self.update()

            if tipo == "Texto":
                data = payload_text(self.get_entry_value("Conteúdo"))

            elif tipo == "URL":
                data = payload_url(self.get_entry_value("Link"))

            elif tipo in ["Wi-Fi Manual", "Wi-Fi Atual"]:
                ssid = self.get_entry_value("SSID")
                senha = self.get_entry_value("Senha")
                auth = self.get_entry_value("Tipo de Autenticação")
                hidden = self.get_entry_value("Rede Oculta").lower() == "true"

                if not ssid:
                    raise ValueError("SSID é obrigatório para gerar QR Code Wi-Fi")

                data = payload_wifi(ssid, senha, auth, hidden)

            elif tipo == "Geo":
                lat = float(self.get_entry_value("Latitude"))
                lng = float(self.get_entry_value("Longitude"))
                data = payload_geo(lat, lng)

            elif tipo == "SMS":
                numero = self.get_entry_value("Número")
                msg = self.get_entry_value("Mensagem")
                data = payload_sms(numero, msg)

            elif tipo == "Email":
                to = self.get_entry_value("Destinatário")
                assunto = self.get_entry_value("Assunto")
                corpo = self.get_entry_value("Corpo")
                data = payload_email(to, assunto, corpo)

            elif tipo == "WhatsApp":
                numero = self.get_entry_value("Número")
                mensagem = self.get_entry_value("Mensagem")
                data = payload_whatsapp(numero, mensagem)

            elif tipo == "Pix":
                chave = self.get_entry_value("Chave Pix")
                valor = self.get_entry_value("Valor")
                valor = float(valor) if valor else 0.0
                data = payload_pix(chave, valor)

            if not data.strip():
                raise ValueError("Por favor, preencha pelo menos um campo obrigatório")

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=12,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")

            window_width = self.winfo_width()
            qr_size = min(400, max(300, int(window_width * 0.25)))

            self.qr_img_pil = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            qr_photo = ImageTk.PhotoImage(self.qr_img_pil)

            self.qr_img_label.configure(image=qr_photo, text="")
            self.qr_img_label.image = qr_photo
            self.last_data = data

            self.history.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo, data))

            self.status_label.configure(
                text="QR Code gerado com sucesso!",
                text_color=self.colors['success']
            )

        except ValueError as e:
            error_msg = f"Erro de validação: {str(e)}"
            self.qr_img_label.configure(
                text=f"{error_msg}\n\n"
                    "Verifique os campos e tente novamente",
                font=self.fonts['body'],
                text_color=self.colors['danger']
            )
            self.status_label.configure(text=error_msg, text_color=self.colors['danger'])

        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            self.qr_img_label.configure(
                text=f"{error_msg}\n\n"
                    "Tente novamente ou contate o suporte",
                font=self.fonts['body'],
                text_color=self.colors['danger']
            )
            self.status_label.configure(text=error_msg, text_color=self.colors['danger'])

    def save_qr(self):
        """Salvar QR Code com melhor UX"""
        if self.qr_img_pil:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tipo = self.option_var.get().replace(" ", "_").lower()
                default_name = f"qrcode_{tipo}_{timestamp}.png"

                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[
                        ("PNG files", "*.png"), 
                        ("JPEG files", "*.jpg"), 
                        ("All files", "*.*")
                    ],
                    initialfile=default_name,
                    title="Salvar QR Code"
                )

                if filename:
                    self.qr_img_pil.save(filename)
                    self.status_label.configure(
                        text=f"QR Code salvo: {filename}",
                        text_color=self.colors['success']
                    )
                    messagebox.showinfo(
                        "Sucesso", 
                        f"QR Code salvo com sucesso!\n {filename}"
                    )

            except Exception as e:
                error_msg = f"Erro ao salvar: {str(e)}"
                self.status_label.configure(text=error_msg, text_color=self.colors['danger'])
                messagebox.showerror("Erro", error_msg)
        else:
            msg = "Gere um QR Code primeiro antes de salvar"
            self.status_label.configure(text=msg, text_color=self.colors['warning'])
            messagebox.showwarning("Aviso", msg)

    def copy_content(self):
        """Copiar dados com feedback melhorado"""
        if self.last_data:
            try:
                pyperclip.copy(self.last_data)
                self.status_label.configure(
                    text="Dados copiados para área de transferência!",
                    text_color=self.colors['success']
                )
                messagebox.showinfo(
                    "Sucesso", 
                    "Conteúdo copiado para área de transferência!"
                )
            except Exception as e:
                error_msg = f"Erro ao copiar: {str(e)}"
                self.status_label.configure(text=error_msg, text_color=self.colors['danger'])
                messagebox.showerror("Erro", error_msg)
        else:
            msg = "Gere um QR Code primeiro para copiar os dados"
            self.status_label.configure(text=msg, text_color=self.colors['warning'])
            messagebox.showwarning("Aviso", msg)

    def clear_fields(self):
        """Limpar campos com confirmação"""
        result = messagebox.askyesno(
            "Confirmar Limpeza", 
            "Tem certeza que deseja limpar todos os campos?\n\n"
            "Esta ação não pode ser desfeita."
        )
        
        if result:
            for entry in self.entries.values():
                if isinstance(entry, ctk.CTkTextbox):
                    entry.delete("1.0", "end")
                else:
                    entry.delete(0, "end")

            self.qr_img_label.configure(
                image=None,
                text=" QR Code será exibido aqui\n\n"
                    "1 Selecione um tipo de QR Code\n"
                    "2 Preencha os campos necessários\n" 
                    "3 Clique em 'Gerar QR Code'\n\n"
                    " Seu código aparecerá nesta área",
                text_color=["#64748b", "#64748b"]
            )
            if hasattr(self.qr_img_label, 'image'):
                delattr(self.qr_img_label, 'image')
            
            self.qr_img_pil = None
            self.last_data = ""
            self.status_label.configure(
                text="Campos limpos - Pronto para novo QR Code",
                text_color=self.colors['info']
            )

    def show_data(self):
        """Mostrar dados do QR Code com interface melhorada"""
        if not self.last_data:
            messagebox.showwarning(
                "Aviso", 
                "Gere um QR Code primeiro para visualizar os dados."
            )
            return
            
        data_window = ctk.CTkToplevel(self)
        data_window.title("Dados do QR Code")
        data_window.geometry("700x500")
        data_window.grid_columnconfigure(0, weight=1)
        data_window.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            data_window, 
            height=80, 
            corner_radius=15,
            fg_color=self.colors['primary']
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header.grid_propagate(False)

        header_label = ctk.CTkLabel(
            header,
            text="Visualização dos Dados do QR Code",
            font=self.fonts['heading'],
            text_color="white"
        )
        header_label.pack(pady=20)

        text_box = ctk.CTkTextbox(
            data_window, 
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=10
        )
        text_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        text_box.insert("1.0", self.last_data)
        text_box.configure(state="disabled")

        button_frame = ctk.CTkFrame(data_window, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=20, pady=(0, 20))

        copy_btn = ctk.CTkButton(
            button_frame,
            text="Copiar Dados",
            command=lambda: pyperclip.copy(self.last_data),
            font=self.fonts['body'],
            fg_color=self.colors['success'],
            hover_color="#059669"
        )
        copy_btn.pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(
            button_frame,
            text="Fechar",
            command=data_window.destroy,
            font=self.fonts['body'],
            fg_color=self.colors['danger'],
            hover_color="#dc2626"
        )
        close_btn.pack(side="left")

    def show_history(self):
        """Mostrar histórico com interface melhorada"""
        if not self.history:
            messagebox.showinfo(
                "Histórico", 
                "Nenhum QR Code gerado ainda.\n\n"
                "Gere alguns códigos QR para ver o histórico!"
            )
            return
            
        history_window = ctk.CTkToplevel(self)
        history_window.title("Histórico de QR Codes")
        history_window.geometry("900x600")
        history_window.grid_columnconfigure(0, weight=1)
        history_window.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            history_window, 
            height=100, 
            corner_radius=15,
            fg_color=self.colors['accent']
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header.grid_propagate(False)

        header_label = ctk.CTkLabel(
            header,
            text="Histórico de QR Codes Gerados",
            font=self.fonts['heading'],
            text_color="white"
        )
        header_label.pack(pady=(20, 5))

        count_label = ctk.CTkLabel(
            header,
            text=f"Total de códigos gerados: {len(self.history)}",
            font=self.fonts['body'],
            text_color="white"
        )
        count_label.pack()

        history_text = ctk.CTkTextbox(
            history_window, 
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10
        )
        history_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        lines = ["Data e Hora            | Tipo           | Dados"]
        lines.append("=" * 100)
        
        for timestamp, tipo, data in reversed(self.history[-50:]):
            formatted_data = data[:80] + "..." if len(data) > 80 else data
            formatted_data = formatted_data.replace('\n', ' ').replace('\r', ' ')
            line = f"{timestamp} | {tipo:<14} | {formatted_data}"
            lines.append(line)

        history_text.insert("1.0", "\n".join(lines))
        history_text.configure(state="disabled")

        close_btn = ctk.CTkButton(
            history_window,
            text="Fechar",
            command=history_window.destroy,
            font=self.fonts['body'],
            fg_color=self.colors['danger'],
            hover_color="#dc2626"
        )
        close_btn.grid(row=2, column=0, pady=(0, 20))


if __name__ == "__main__":
    app = QRApp()
    app.mainloop()