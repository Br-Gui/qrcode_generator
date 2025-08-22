import customtkinter as ctk
import qrcode
from PIL import Image, ImageTk
from qr_payloads import *
from wifi_utils import get_current_wifi

class QRApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de QR Code")
        self.geometry("600x500")

        self.option_var = ctk.StringVar(value="Texto")
        self.input_frame = None
        self.qr_label = None

        self.create_widgets()

    def create_widgets(self):
        
        options = ["Texto", "URL", "Wi-Fi", "Geo", "SMS", "Email", "WhatsApp", "Pix"]
        option_menu = ctk.CTkOptionMenu(self, values=options, variable=self.option_var, command=self.change_form)
        option_menu.pack(pady=10)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="both", expand=True, pady=10)

        self.generate_btn = ctk.CTkButton(self, text="Gerar QR Code", command=self.generate_qr)
        self.generate_btn.pack(pady=10)

        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.pack(pady=10)

        self.change_form("Texto")

    def change_form(self, tipo):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        self.entries = {}

        if tipo == "Texto":
            self._add_entry("Conteúdo")
        elif tipo == "URL":
            self._add_entry("Link")
        elif tipo == "Wi-Fi":
            wifi = get_current_wifi()
            self._add_entry("SSID", default=wifi[0] if wifi else "")
            self._add_entry("Senha", default=wifi[1] if wifi else "")
            self._add_entry("Autenticação (WPA/WEP/NOPASS)", default="WPA")
            self._add_entry("Oculta (true/false)", default="false")
        elif tipo == "Geo":
            self._add_entry("Latitude")
            self._add_entry("Longitude")
        elif tipo == "SMS":
            self._add_entry("Número")
            self._add_entry("Mensagem")
        elif tipo == "Email":
            self._add_entry("Destinatário")
            self._add_entry("Assunto")
            self._add_entry("Corpo")
        elif tipo == "WhatsApp":
            self._add_entry("Número (ex: 5511999999999)")
            self._add_entry("Mensagem")
        elif tipo == "Pix":
            self._add_entry("Chave")
            self._add_entry("Valor (opcional)")
            self._add_entry("Nome (opcional)")
            self._add_entry("Cidade (opcional)")

    def _add_entry(self, label, default=""):
        frame = ctk.CTkFrame(self.form_frame)
        frame.pack(fill="x", pady=5)
        lbl = ctk.CTkLabel(frame, text=label, width=200, anchor="w")
        lbl.pack(side="left", padx=5)
        entry = ctk.CTkEntry(frame)
        entry.insert(0, default)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        self.entries[label] = entry

    def generate_qr(self):
        tipo = self.option_var.get()
        data = ""

        try:
            if tipo == "Texto":
                data = payload_text(self.entries["Conteúdo"].get())
            elif tipo == "URL":
                data = payload_url(self.entries["Link"].get())
            elif tipo == "Wi-Fi":
                ssid = self.entries["SSID"].get()
                senha = self.entries["Senha"].get()
                auth = self.entries["Autenticação (WPA/WEP/NOPASS)"].get()
                oculta = self.entries["Oculta (true/false)"].get().lower() == "true"
                data = payload_wifi(ssid, senha, auth, oculta)
            elif tipo == "Geo":
                lat = float(self.entries["Latitude"].get())
                lng = float(self.entries["Longitude"].get())
                data = payload_geo(lat, lng)
            elif tipo == "SMS":
                numero = self.entries["Número"].get()
                msg = self.entries["Mensagem"].get()
                data = payload_sms(numero, msg)
            elif tipo == "Email":
                to = self.entries["Destinatário"].get()
                assunto = self.entries["Assunto"].get()
                corpo = self.entries["Corpo"].get()
                data = payload_email(to, assunto, corpo)
            elif tipo == "WhatsApp":
                numero = self.entries["Número (ex: 5511999999999)"].get()
                mensagem = self.entries["Mensagem"].get()
                data = payload_whatsapp(numero, mensagem)
            elif tipo == "Pix":
                chave = self.entries["Chave"].get()
                valor = self.entries["Valor (opcional)"].get()
                nome = self.entries["Nome (opcional)"].get()
                cidade = self.entries["Cidade (opcional)"].get()
                valor_f = float(valor) if valor else 0.0
                data = payload_pix(chave, valor_f, nome, cidade)

        except Exception as e:
            self.qr_label.configure(text=f"Erro: {e}")
            return

        qr = qrcode.make(data)
        qr_img = ImageTk.PhotoImage(qr.resize((200, 200)))
        self.qr_label.configure(image=qr_img, text="")
        self.qr_label.image = qr_img

if __name__ == "__main__":
    app = QRApp()
    app.mainloop()
