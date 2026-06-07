import os
import sys
import json
import socket
import base64
import urllib.parse
import ipaddress
from datetime import datetime
from singbox2proxy import SingBoxBatch

# Ограничиваем время ожидания DNS-запросов
socket.setdefaulttimeout(1.0)

CONFIG_FILE = "YaltaVPN - Subscription"
LOG_FILE = "log.csv"
IS_PUBLIC = True
BASE_DIR = os.path.abspath(os.getcwd())

# ===================== ИСТОЧНИКИ =====================
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt",
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass/bypass-all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/light.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/vless.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/mix.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/vless.txt",
    "https://raw.githubusercontent.com/zieng2/wl/refs/heads/main/vless_lite.txt",
]

def parse_vmess_b64(url):
    try:
        payload = url[8:].split('#')[0]
        payload += '=' * (-len(payload) % 4)
        data = json.loads(base64.b64decode(payload).decode('utf-8', errors='ignore'))
        return data
    except:
        return {}

def get_desc_b64(proxy_url, latency):
    try:
        server_address = ''
        sni = ''
        
        # Парсинг VMess
        if proxy_url.startswith('vmess://') and '@' not in proxy_url:
            vmess_data = parse_vmess_b64(proxy_url)
            server_address = vmess_data.get('add', '')
            sni = vmess_data.get('sni', '') or vmess_data.get('host', '')
        else:
            parsed = urllib.parse.urlparse(proxy_url)
            server_address = parsed.hostname or ''
            query_params = urllib.parse.parse_qs(parsed.query)
            sni = query_params.get('sni', [''])[0] or query_params.get('peer', [''])[0] or query_params.get('host', [''])[0]
        
        # Определение IP сервера
        ip = ''
        if server_address:
            try:
                ip = socket.gethostbyname(server_address)
            except Exception:
                ip = server_address
        else:
            ip = '-'

        # Определение SNI
        if not sni:
            if server_address and any(c.isalpha() for c in server_address):
                sni = server_address
            else:
                sni = '-'

        # Определение цветного эмодзи по пингу
        if latency < 120:
            emoji = "🟢"
        elif latency < 200:
            emoji = "🟡"
        else:
            emoji = "🔴"

        desc_str = f"{emoji} SNI: {sni} | IP: {ip}"
        desc_b64 = base64.b64encode(desc_str.encode('utf-8')).decode('utf-8')
        return desc_b64, ip, sni
    except Exception as e:
        desc_str = f"🔴 Ping: {latency}ms"
        desc_b64 = base64.b64encode(desc_str.encode('utf-8')).decode('utf-8')
        return desc_b64, '-', '-'

def append_description(proxy_url, desc_b64):
    if '#' in proxy_url:
        return f"{proxy_url}?serverDescription={desc_b64}"
    else:
        if '?' in proxy_url:
            return f"{proxy_url}&serverDescription={desc_b64}"
        else:
            return f"{proxy_url}?serverDescription={desc_b64}"

def find_original_line(proxy_url, url_map):
    if proxy_url in url_map:
        return url_map[proxy_url]
    
    clean_proxy = proxy_url.split('#')[0].strip()
    if clean_proxy in url_map:
        return url_map[clean_proxy]
        
    try:
        parsed_proxy = urllib.parse.urlparse(proxy_url)
        proxy_host = parsed_proxy.hostname
        proxy_port = parsed_proxy.port
        if proxy_host:
            for key, original_line in url_map.items():
                try:
                    parsed_key = urllib.parse.urlparse(key.split('#')[0])
                    if parsed_key.hostname == proxy_host and parsed_key.port == proxy_port:
                        return original_line
                except:
                    continue
    except:
        pass
        
    return proxy_url

def find_source(proxy_url, source_map):
    # Прямое сопоставление
    if proxy_url in source_map:
        return source_map[proxy_url]
    
    clean_proxy = proxy_url.split('#')[0].strip()
    if clean_proxy in source_map:
        return source_map[clean_proxy]
        
    # Поиск по домену/порту
    try:
        parsed_proxy = urllib.parse.urlparse(proxy_url)
        proxy_host = parsed_proxy.hostname
        proxy_port = parsed_proxy.port
        if proxy_host:
            for key, src in source_map.items():
                try:
                    parsed_key = urllib.parse.urlparse(key.split('#')[0])
                    if parsed_key.hostname == proxy_host and parsed_key.port == proxy_port:
                        return src
                except:
                    continue
    except:
        pass
        
    return "Unknown Source"

def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def log_to_sheet(total, cidr_count, unique_sni):
    path = os.path.join(BASE_DIR, LOG_FILE)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    needed_header = not os.path.exists(path)
    with open(path, 'a', encoding='utf-8') as f:
        if needed_header:
            f.write("timestamp,total,cidr_count,unique_sni\n")
        f.write(f"{now},{total},{cidr_count},{unique_sni}\n")

def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} not found!")
        sys.exit(1)

    # Загружаем карту источников
    source_map = {}
    if os.path.exists("temp_source_map.json"):
        try:
            with open("temp_source_map.json", "r", encoding="utf-8") as f:
                source_map = json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка чтения temp_source_map.json: {e}")

    # Инициализация словаря статистики для Markdown
    stats = {src: {"alive": 0, "dead": 0, "total": 0} for src in SOURCES}
    stats["Unknown Source"] = {"alive": 0, "dead": 0, "total": 0}

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    proxy_lines = []
    url_map = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        proxy_lines.append(line)
        url_map[line] = line
        parts = line.split('#', 1)
        url_map[parts[0].strip()] = line

    print(f"Загружено {len(proxy_lines)} прокси из {CONFIG_FILE} для валидации...")
    valid_proxies = []

    with SingBoxBatch(proxy_lines, batch_size=30, log_level="error") as batch:
        for proxy in batch:
            # Получаем источник текущей конфигурации
            source = find_source(proxy.url, source_map)
            
            try:
                resp = proxy.get("http://www.gstatic.com/generate_204", timeout=2)
                if resp.status_code == 204:
                    latency = int(resp.elapsed.total_seconds() * 1000)
                    print(f"[PASS] {proxy.protocol:<6} | Ping: {latency:>4}ms | {proxy.url[:40]}...")
                    
                    desc_b64, ip, sni = get_desc_b64(proxy.url, latency)
                    original_line = find_original_line(proxy.url, url_map)
                    final_line = append_description(original_line, desc_b64)
                    
                    valid_proxies.append({
                        "line": final_line,
                        "latency": latency,
                        "ip": ip,
                        "sni": sni
                    })
                    
                    stats[source]["alive"] += 1
                    stats[source]["total"] += 1
                else:
                    print(f"[FAIL] {proxy.protocol:<6} | Status: {resp.status_code} | {proxy.url[:40]}...")
                    stats[source]["dead"] += 1
                    stats[source]["total"] += 1
            except Exception as e:
                err_msg = str(e).split('\n')[0]
                print(f"[DEAD] {proxy.protocol:<6} | Error: {err_msg[:40]} | {proxy.url[:40]}...")
                stats[source]["dead"] += 1
                stats[source]["total"] += 1

    # Сортировка рабочих по пингу
    valid_proxies.sort(key=lambda x: x["latency"])

    total_valid = len(valid_proxies)
    unique_sni = len({p["sni"] for p in valid_proxies if p["sni"] and p["sni"] != '-'})
    cidr_count = sum(1 for p in valid_proxies if p["ip"] and is_valid_ip(p["ip"]))

    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    if IS_PUBLIC:
        announce = (f"🌴 ЯлтаВПН - Курортный ВПН | "
                    f"конфигов: {total_valid} (CIDR: {cidr_count}) | SNI: {unique_sni} | "
                    f"обновлено: {timestamp}")
    else:
        announce = (f"🌴 ЯлтаВПН - Курортный ВПН 🔒PRIVATE | "
                    f"конфигов: {total_valid} (CIDR: {cidr_count}) | SNI: {unique_sni} | "
                    f"обновлено: {timestamp}")

    header = [
        "#profile-update-interval: 1",
        "#support-url: https://t.me/YaltaVPN_Obxod",
        f"#profile-title: {announce}",
        "#hide-settings: 1",
        ""
    ]

    # Перезапись файла подписки валидными прокси
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write('\n'.join(header) + '\n')
        for p in valid_proxies:
            f.write(p["line"] + "\n")

    log_to_sheet(total_valid, cidr_count, unique_sni)

    # ================= Генерация statistic.md =================
    markdown_rows = []
    for src, data in stats.items():
        total = data["total"]
        alive = data["alive"]
        dead = data["dead"]
        
        if total > 0:
            alive_pct = (alive / total) * 100
            dead_pct = (dead / total) * 100
            alive_str = f"{alive} ({alive_pct:.1f}%)"
            dead_str = f"{dead} ({dead_pct:.1f}%)"
        else:
            alive_str = "0 (0.0%)"
            dead_str = "0 (0.0%)"
            
        markdown_rows.append((src, alive_str, dead_str, total))

    # Разделяем "Unknown Source" и известные источники для красивой сортировки
    sorted_rows = []
    unknown_row = None
    for src, alive_str, dead_str, total in markdown_rows:
        if src == "Unknown Source":
            if total > 0:
                unknown_row = (src, alive_str, dead_str, total)
        else:
            sorted_rows.append((src, alive_str, dead_str, total))

    # Сортируем источники по количеству живых прокси по убыванию
    sorted_rows.sort(key=lambda x: stats[x[0]]["alive"], reverse=True)
    if unknown_row:
        sorted_rows.append(unknown_row)

    # Запись в файл Markdown
    header_md = """# Статистика работоспособности источников

![uwu](https://i.giphy.com/UuzwffmvtBNGjYyEUe.webp)

| Ссылка | Живых | Мёртвых | Всего |
| :--- | :---: | :---: | :---: |
"""
    with open("statistic.md", "w", encoding="utf-8") as f:
        f.write(header_md)
        for src, alive_str, dead_str, total in sorted_rows:
            src_display = f"[{src}]({src})" if src.startswith("http") else src
            f.write(f"| {src_display} | {alive_str} | {dead_str} | {total} |\n")

    # Удаляем временный файл сопоставления
    if os.path.exists("temp_source_map.json"):
        try:
            os.remove("temp_source_map.json")
        except:
            pass

    print(f"Готово! Сохранено {total_valid} работающих прокси в {CONFIG_FILE}. Статистика сохранена в statistic.md")

if __name__ == "__main__":
    main()
