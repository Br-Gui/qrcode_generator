import urllib.parse
import io
from PIL import Image
from pypix.pix import Pix
from pypix.core.styles.qr_styler import GradientMode
from pypix.core.styles.marker_styles import MarkerStyle
from pypix.core.styles.border_styles import BorderStyle
from pypix.core.styles.line_styles import LineStyle
from pypix.core.styles.frame_styles import FrameStyle

def payload_url(url: str) -> str:
    return url.strip()

def payload_text(text: str) -> str:
    return text.strip()

def payload_wifi(ssid: str, password: str = "", auth: str = "WPA", hidden: bool = False) -> str:
    auth_up = auth.upper()
    if auth_up not in {"WPA", "WEP", "NOPASS"}:
        raise ValueError("Autenticação inválida. Use WPA, WEP ou NOPASS.")
    hidden_str = "true" if hidden else "false"
    if auth_up == "NOPASS":
        return f"WIFI:T:nopass;S:{ssid};H:{hidden_str};;"
    return f"WIFI:T:{auth_up};S:{ssid};P:{password};H:{hidden_str};;"

def payload_geo(lat: float, lng: float) -> str:
    return f"geo:{lat},{lng}"

def payload_sms(numero: str, msg: str = "") -> str:
    return f"SMSTO:{numero}:{msg}"

def payload_email(to: str, subject: str = "", body: str = "") -> str:
    qs = []
    if subject:
        qs.append("subject=" + urllib.parse.quote(subject))
    if body:
        qs.append("body=" + urllib.parse.quote(body))
    query = ("?" + "&".join(qs)) if qs else ""
    return f"mailto:{to}{query}"

def payload_whatsapp(numero: str, mensagem: str = "") -> str:
    return f"https://wa.me/{numero}?text={urllib.parse.quote(mensagem)}"

def payload_pix(chave: str, valor: float) -> str:
    """
    Gera QR Code Pix usando PyPix, exibe o QR Code e retorna o BR Code.
    """
    pix = Pix()
    pix.set_key(chave)
    pix.set_name_receiver('cliente')
    pix.set_city_receiver('São paulo')
    pix.set_description("Pagamento Pix")
    pix.set_amount(valor)

    br_code = pix.get_br_code()

    qr_img = pix.save_qrcode(
        data=br_code,
        box_size=10,
        border=4,
        marker_style=MarkerStyle.ROUNDED,
        border_style=BorderStyle.ROUNDED,
        line_style=LineStyle.ROUNDED,
        gradient_color="#000000",
        gradient_mode=GradientMode.NORMAL,
        frame_style=FrameStyle.CLEAN,
        style_mode="Simple"
    )

    print("QR Code Pix gerado")

    return br_code