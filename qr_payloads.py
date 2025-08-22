import urllib.parse

def payload_url(url: str) -> str:
    return url

def payload_text(text: str) -> str:
    return text

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

def payload_pix(chave: str, valor: float = 0.0, nome: str = "", cidade: str = "") -> str:
    """
    Gera payload simples de Pix (formato EMV simplificado).
    """
    payload = f"00020126580014BR.GOV.BCB.PIX01{len(chave):02}{chave}"
    if valor > 0:
        payload += f"54{len(str(valor))}{valor}"
    if nome:
        payload += f"59{len(nome):02}{nome}"
    if cidade:
        payload += f"60{len(cidade):02}{cidade}"
    payload += "6304"
    return payload
