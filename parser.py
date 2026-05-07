import re
import requests
import concurrent.futures
import urllib.parse
import base64
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# ==========================================
# SOURCES (замените на свои)
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass/bypass-all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/light.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/vless.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/mix.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/vless.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-checker-backend/main/checked/RU_Best/ru_white.txt",
    "https://raw.githubusercontent.com/zieng2/wl/refs/heads/main/vless_lite.txt"
]
for i in range(1, 23):
    SOURCES.append (
        "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/{i}.txt"
    )

# ==========================================
# БАЗА ФЛАГОВ
# ==========================================
FLAG_DB = {
    "🇦🇨": "Ascension Island", "🇦🇩": "Andorra", "🇦🇪": "UAE", "🇦🇫": "Afghanistan",
    "🇦🇬": "Antigua and Barbuda", "🇦🇮": "Anguilla", "🇦🇱": "Albania", "🇦🇲": "Armenia",
    "🇦🇴": "Angola", "🇦🇶": "Antarctica", "🇦🇷": "Argentina", "🇦🇸": "American Samoa",
    "🇦🇹": "Austria", "🇦🇺": "Australia", "🇦🇼": "Aruba", "🇦🇽": "Åland Islands",
    "🇦🇿": "Azerbaijan", "🇧🇦": "Bosnia", "🇧🇧": "Barbados", "🇧🇩": "Bangladesh",
    "🇧🇪": "Belgium", "🇧🇫": "Burkina Faso", "🇧🇬": "Bulgaria", "🇧🇭": "Bahrain",
    "🇧🇮": "Burundi", "🇧🇯": "Benin", "🇧🇱": "St. Barthélemy", "🇧🇲": "Bermuda",
    "🇧🇳": "Brunei", "🇧🇴": "Bolivia", "🇧🇶": "Caribbean Netherlands", "🇧🇷": "Brazil",
    "🇧🇸": "Bahamas", "🇧🇹": "Bhutan", "🇧🇻": "Bouvet Island", "🇧🇼": "Botswana",
    "🇧🇾": "Belarus", "🇧🇿": "Belize", "🇨🇦": "Canada", "🇨🇨": "Cocos Islands",
    "🇨🇩": "DR Congo", "🇨🇫": "Central African Republic", "🇨🇬": "Congo", "🇨🇭": "Switzerland",
    "🇨🇮": "Côte d'Ivoire", "🇨🇰": "Cook Islands", "🇨🇱": "Chile", "🇨🇲": "Cameroon",
    "🇨🇳": "China", "🇨🇴": "Colombia", "🇨🇵": "Clipperton Island", "🇨🇷": "Costa Rica",
    "🇨🇺": "Cuba", "🇨🇻": "Cape Verde", "🇨🇼": "Curaçao", "🇨🇽": "Christmas Island",
    "🇨🇾": "Cyprus", "🇨🇿": "Czechia", "🇩🇪": "Germany", "🇩🇬": "Diego Garcia", "🇩🇯": "Djibouti",
    "🇩🇰": "Denmark", "🇩🇲": "Dominica", "🇩🇴": "Dominican Republic", "🇩🇿": "Algeria",
    "🇪🇦": "Ceuta & Melilla", "🇪🇨": "Ecuador", "🇪🇪": "Estonia", "🇪🇬": "Egypt",
    "🇪🇭": "Western Sahara", "🇪🇷": "Eritrea", "🇪🇸": "Spain", "🇪🇹": "Ethiopia",
    "🇪🇺": "European Union", "🇫🇮": "Finland", "🇫🇯": "Fiji", "🇫🇰": "Falkland Islands",
    "🇫🇲": "Micronesia", "🇫🇴": "Faroe Islands", "🇫🇷": "France", "🇬🇦": "Gabon",
    "🇬🇧": "UK", "🇬🇩": "Grenada", "🇬🇪": "Georgia", "🇬🇫": "French Guiana", "🇬🇬": "Guernsey",
    "🇬🇭": "Ghana", "🇬🇮": "Gibraltar", "🇬🇱": "Greenland", "🇬🇲": "Gambia", "🇬🇳": "Guinea",
    "🇬🇵": "Guadeloupe", "🇬🇶": "Equatorial Guinea", "🇬🇷": "Greece", "🇬🇸": "South Georgia",
    "🇬🇹": "Guatemala", "🇬🇺": "Guam", "🇬🇼": "Guinea-Bissau", "🇬🇾": "Guyana",
    "🇭🇰": "Hong Kong", "🇭🇲": "Heard & McDonald Islands", "🇭🇳": "Honduras", "🇭🇷": "Croatia",
    "🇭🇹": "Haiti", "🇭🇺": "Hungary", "🇮🇨": "Canary Islands", "🇮🇩": "Indonesia",
    "🇮🇪": "Ireland", "🇮🇱": "Israel", "🇮🇲": "Isle of Man", "🇮🇳": "India",
    "🇮🇴": "British Indian Ocean Territory", "🇮🇶": "Iraq", "🇮🇷": "Iran", "🇮🇸": "Iceland",
    "🇮🇹": "Italy", "🇯🇪": "Jersey", "🇯🇲": "Jamaica", "🇯🇴": "Jordan", "🇯🇵": "Japan",
    "🇰🇪": "Kenya", "🇰🇬": "Kyrgyzstan", "🇰🇭": "Cambodia", "🇰🇮": "Kiribati",
    "🇰🇲": "Comoros", "🇰🇳": "St. Kitts & Nevis", "🇰🇵": "North Korea", "🇰🇷": "South Korea",
    "🇰🇼": "Kuwait", "🇰🇾": "Cayman Islands", "🇰🇿": "Kazakhstan", "🇱🇦": "Laos",
    "🇱🇧": "Lebanon", "🇱🇨": "St. Lucia", "🇱🇮": "Liechtenstein", "🇱🇰": "Sri Lanka",
    "🇱🇷": "Liberia", "🇱🇸": "Lesotho", "🇱🇹": "Lithuania", "🇱🇺": "Luxembourg",
    "🇱🇻": "Latvia", "🇱🇾": "Libya", "🇲🇦": "Morocco", "🇲🇨": "Monaco", "🇲🇩": "Moldova",
    "🇲🇪": "Montenegro", "🇲🇫": "St. Martin", "🇲🇬": "Madagascar", "🇲🇭": "Marshall Islands",
    "🇲🇰": "North Macedonia", "🇲🇱": "Mali", "🇲🇲": "Myanmar", "🇲🇳": "Mongolia",
    "🇲🇴": "Macau", "🇲🇵": "Northern Mariana Islands", "🇲🇶": "Martinique", "🇲🇷": "Mauritania",
    "🇲🇸": "Montserrat", "🇲🇹": "Malta", "🇲🇺": "Mauritius", "🇲🇻": "Maldives",
    "🇲🇼": "Malawi", "🇲🇽": "Mexico", "🇲🇾": "Malaysia", "🇲🇿": "Mozambique",
    "🇳🇦": "Namibia", "🇳🇨": "New Caledonia", "🇳🇪": "Niger", "🇳🇫": "Norfolk Island",
    "🇳🇬": "Nigeria", "🇳🇮": "Nicaragua", "🇳🇱": "Netherlands", "🇳🇴": "Norway",
    "🇳🇵": "Nepal", "🇳🇷": "Nauru", "🇳🇺": "Niue", "🇳🇿": "New Zealand",
    "🇴🇲": "Oman", "🇵🇦": "Panama", "🇵🇪": "Peru", "🇵🇫": "French Polynesia",
    "🇵🇬": "Papua New Guinea", "🇵🇭": "Philippines", "🇵🇰": "Pakistan", "🇵🇱": "Poland",
    "🇵🇲": "St. Pierre & Miquelon", "🇵🇳": "Pitcairn Islands", "🇵🇷": "Puerto Rico",
    "🇵🇸": "Palestine", "🇵🇹": "Portugal", "🇵🇼": "Palau", "🇵🇾": "Paraguay",
    "🇶🇦": "Qatar", "🇷🇪": "Réunion", "🇷🇴": "Romania", "🇷🇸": "Serbia", "🇷🇺": "Russia",
    "🇷🇼": "Rwanda", "🇸🇦": "Saudi Arabia", "🇸🇧": "Solomon Islands", "🇸🇨": "Seychelles",
    "🇸🇩": "Sudan", "🇸🇪": "Sweden", "🇸🇬": "Singapore", "🇸🇭": "St. Helena",
    "🇸🇮": "Slovenia", "🇸🇯": "Svalbard & Jan Mayen", "🇸🇰": "Slovakia", "🇸🇱": "Sierra Leone",
    "🇸🇲": "San Marino", "🇸🇳": "Senegal", "🇸🇴": "Somalia", "🇸🇷": "Suriname",
    "🇸🇸": "South Sudan", "🇸🇹": "São Tomé & Príncipe", "🇸🇻": "El Salvador",
    "🇸🇽": "Sint Maarten", "🇸🇾": "Syria", "🇸🇿": "Eswatini", "🇹🇦": "Tristan da Cunha",
    "🇹🇨": "Turks & Caicos", "🇹🇩": "Chad", "🇹🇫": "French Southern Territories",
    "🇹🇬": "Togo", "🇹🇭": "Thailand", "🇹🇯": "Tajikistan", "🇹🇰": "Tokelau",
    "🇹🇱": "Timor-Leste", "🇹🇲": "Turkmenistan", "🇹🇳": "Tunisia", "🇹🇴": "Tonga",
    "🇹🇷": "Turkey", "🇹🇹": "Trinidad & Tobago", "🇹🇻": "Tuvalu", "🇹🇼": "Taiwan",
    "🇹🇿": "Tanzania", "🇺🇦": "Ukraine", "🇺🇬": "Uganda", "🇺🇲": "US Outlying Islands",
    "🇺🇳": "United Nations", "🇺🇸": "USA", "🇺🇾": "Uruguay", "🇺🇿": "Uzbekistan",
    "🇻🇦": "Vatican City", "🇻🇨": "St. Vincent & Grenadines", "🇻🇪": "Venezuela",
    "🇻🇬": "British Virgin Islands", "🇻🇮": "US Virgin Islands", "🇻🇳": "Vietnam",
    "🇻🇺": "Vanuatu", "🇼🇫": "Wallis & Futuna", "🇼🇸": "Samoa", "🇽🇰": "Kosovo",
    "🇾🇪": "Yemen", "🇾🇹": "Mayotte", "🇿🇦": "South Africa", "🇿🇲": "Zambia", "🇿🇼": "Zimbabwe"
}

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def extract_host(link):
    """Извлекает хост (IP или домен) из ссылки конфига."""
    m = re.search(r'@([\w\.\-]+):', link)
    return m.group(1) if m else None

def extract_sni(link):
    """Извлекает значение параметра sni из URL конфига."""
    try:
        base = link.split("#")[0]
        qs = urlparse(base).query
        sni = parse_qs(qs).get('sni', [None])[0]
        return sni.lower() if sni else None
    except:
        return None

def get_flag_info(raw_fragment):
    """Возвращает (флаг, страна) или ('🌐', 'Не определено') по наличию флага в строке."""
    if not raw_fragment:
        return "🌐", "Не определено"
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_fragment)
    if flags:
        flag = flags[0]
        country = FLAG_DB.get(flag, "Unknown")
        return flag, country
    return "🌐", "Не определено"

def parse_source(url):
    """Скачивает конфиги из одного источника и возвращает список чистых ссылок с фрагментами."""
    configs = []
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return configs
        found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<]+', r.text)
        configs.extend(found)
    except:
        pass
    return configs

# ==========================================
# ГЛАВНАЯ ЛОГИКА
# ==========================================
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Сбор конфигов для 🌴ЯлтаВПН")
    all_configs = []

    # Параллельная загрузка
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for result in executor.map(parse_source, SOURCES):
            all_configs.extend(result)

    if not all_configs:
        print("❌ Не найдено ни одного конфига")
        return

    # Перемешиваем и ограничиваем 3000
    random.shuffle(all_configs)
    selected = all_configs[:3000]

    final_lines = []
    hosts_set = set()
    sni_set = set()

    for link in selected:
        # Извлекаем базовую часть и фрагмент
        try:
            base, fragment = link.split("#", 1)
        except ValueError:
            base = link
            fragment = ""

        # Хост
        host = extract_host(base)
        if host:
            hosts_set.add(host)

        # SNI
        sni = extract_sni(base)
        if sni:
            sni_set.add(sni)
        sni_text = sni if sni else "Не определён"

        # Страна по флагу во фрагменте
        flag, country = get_flag_info(fragment)
        if flag == "🌐":
            country_text = "🌐 Не определено"
        else:
            country_text = f"{flag} {country}"

        # Имя конфига
        display_name = f"{country_text} | SNI: {sni_text} | 🌴ЯлтаВПН"
        safe_name = urllib.parse.quote(display_name, safe='')

        final_lines.append(f"{base}#{safe_name}")

    # Подсчёт статистики
    total_hosts = len(hosts_set)
    total_sni = len(sni_set)

    # Вывод описания (для ТГ канала)
    print("\n" + "="*50)
    print("🌴ЯлтаВПН - Курортный ВПН")
    print(f"🌴ЯлтаВПН | CIDR: {total_hosts} | SNI: {total_sni} |")
    print("📢 ТГ канал: https://t.me/YaltaVPN_Obxod")
    print("="*50)

    # Сохранение в файл (Base64)
    content = "\n".join(final_lines)
    b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    filename = "YaltaVPN - Subscription.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(b64)

    print(f"✅ Сохранено {len(final_lines)} конфигов в файл {filename}")

if __name__ == "__main__":
    main()
