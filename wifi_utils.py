import platform
import subprocess

def get_current_wifi() -> tuple[str, str] | None:
    """
    Tenta obter SSID e senha da rede Wi-Fi atual (funciona em Windows e Linux).
    Retorna (ssid, senha) ou None se não conseguir.
    """
    system = platform.system().lower()
    try:
        if "windows" in system:
            ssid = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], encoding="utf-8"
            )
            ssid_line = [l for l in ssid.splitlines() if "SSID" in l and "BSSID" not in l][0]
            ssid_name = ssid_line.split(":", 1)[1].strip()

            profile = subprocess.check_output(
                ["netsh", "wlan", "show", "profile", ssid_name, "key=clear"], encoding="utf-8"
            )
            pwd_line = [l for l in profile.splitlines() if "Conteúdo da Chave" in l or "Key Content" in l]
            password = pwd_line[0].split(":", 1)[1].strip() if pwd_line else ""
            return ssid_name, password

        elif "linux" in system:
            ssid = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], encoding="utf-8"
            )
            active_line = [l for l in ssid.splitlines() if l.startswith("yes:")]
            if not active_line:
                return None
            ssid_name = active_line[0].split(":")[1]

            try:
                password = subprocess.check_output(
                    ["nmcli", "dev", "wifi", "show-password"], encoding="utf-8"
                ).strip()
            except Exception:
                password = ""
            return ssid_name, password

    except Exception:
        return None
