import platform
import subprocess

def get_current_wifi() -> tuple[str, str] | None:
    system = platform.system().lower()

    try:
        if "windows" in system:
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], encoding="utf-8", errors="ignore"
            )
            ssid_line = next((l for l in output.splitlines() if "SSID" in l and "BSSID" not in l), None)
            if not ssid_line:
                return None
            ssid_name = ssid_line.split(":", 1)[1].strip()

            profile_output = subprocess.check_output(
                ["netsh", "wlan", "show", "profile", ssid_name, "key=clear"], encoding="utf-8", errors="ignore"
            )
            pwd_line = next((l for l in profile_output.splitlines() if "Conteúdo da Chave" in l or "Key Content" in l), None)
            password = pwd_line.split(":", 1)[1].strip() if pwd_line else ""
            return ssid_name, password

        elif "linux" in system:
            output = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], encoding="utf-8", errors="ignore"
            )
            active_line = next((l for l in output.splitlines() if l.startswith(("yes:", "sim:"))), None)
            if not active_line:
                return None
            ssid_name = active_line.split(":", 1)[1]

            try:
                conn_output = subprocess.check_output(
                    ["nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", ssid_name],
                    encoding="utf-8",
                    errors="ignore"
                )
                password = conn_output.strip()
            except subprocess.CalledProcessError:
                password = ""

            return ssid_name, password

        else:
            return None

    except Exception:
        return None


if __name__ == "__main__":
    result = get_current_wifi()
    print(result)
