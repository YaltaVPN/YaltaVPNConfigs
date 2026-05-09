import re
import requests
import concurrent.futures
import urllib.parse
import base64
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# ==========================================
# SOURCES
# ==========================================
SOURCES = [
     "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt",
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass/bypass-all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/light.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/vless.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/mix.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/vless.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-checker-backend/main/checked/RU_Best/ru_white.txt",
    "https://raw.githubusercontent.com/zieng2/wl/refs/heads/main/vless_lite.txt",
]
for i in range(1, 21):
    SOURCES.append(
        f"https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/{i}.txt"
    )

# ==========================================
# БАЗА ФЛАГОВ (русские названия)
# ==========================================
FLAG_DB = {
    "🇦🇨": "Остров Вознесения", "🇦🇩": "Андорра", "🇦🇪": "ОАЭ", "🇦🇫": "Афганистан",
    "🇦🇬": "Антигуа и Барбуда", "🇦🇮": "Ангилья", "🇦🇱": "Албания", "🇦🇲": "Армения",
    "🇦🇴": "Ангола", "🇦🇶": "Антарктида", "🇦🇷": "Аргентина", "🇦🇸": "Американское Самоа",
    "🇦🇹": "Австрия", "🇦🇺": "Австралия", "🇦🇼": "Аруба", "🇦🇽": "Аландские о-ва",
    "🇦🇿": "Азербайджан", "🇧🇦": "Босния", "🇧🇧": "Барбадос", "🇧🇩": "Бангладеш",
    "🇧🇪": "Бельгия", "🇧🇫": "Буркина-Фасо", "🇧🇬": "Болгария", "🇧🇭": "Бахрейн",
    "🇧🇮": "Бурунди", "🇧🇯": "Бенин", "🇧🇱": "Сен-Бартельми", "🇧🇲": "Бермуды",
    "🇧🇳": "Бруней", "🇧🇴": "Боливия", "🇧🇶": "Карибские Нидерланды", "🇧🇷": "Бразилия",
    "🇧🇸": "Багамы", "🇧🇹": "Бутан", "🇧🇻": "Остров Буве", "🇧🇼": "Ботсвана",
    "🇧🇾": "Беларусь", "🇧🇿": "Белиз", "🇨🇦": "Канада", "🇨🇨": "Кокосовые о-ва",
    "🇨🇩": "ДР Конго", "🇨🇫": "ЦАР", "🇨🇬": "Конго", "🇨🇭": "Швейцария",
    "🇨🇮": "Кот-д’Ивуар", "🇨🇰": "Острова Кука", "🇨🇱": "Чили", "🇨🇲": "Камерун",
    "🇨🇳": "Китай", "🇨🇴": "Колумбия", "🇨🇵": "Клиппертон", "🇨🇷": "Коста-Рика",
    "🇨🇺": "Куба", "🇨🇻": "Кабо-Верде", "🇨🇼": "Кюрасао", "🇨🇽": "Остров Рождества",
    "🇨🇾": "Кипр", "🇨🇿": "Чехия", "🇩🇪": "Германия", "🇩🇬": "Диего-Гарсия", "🇩🇯": "Джибути",
    "🇩🇰": "Дания", "🇩🇲": "Доминика", "🇩🇴": "Доминиканская Респ.", "🇩🇿": "Алжир",
    "🇪🇦": "Сеута и Мелилья", "🇪🇨": "Эквадор", "🇪🇪": "Эстония", "🇪🇬": "Египет",
    "🇪🇭": "Западная Сахара", "🇪🇷": "Эритрея", "🇪🇸": "Испания", "🇪🇹": "Эфиопия",
    "🇪🇺": "Европейский Союз", "🇫🇮": "Финляндия", "🇫🇯": "Фиджи", "🇫🇰": "Фолклендские о-ва",
    "🇫🇲": "Микронезия", "🇫🇴": "Фарерские о-ва", "🇫🇷": "Франция", "🇬🇦": "Габон",
    "🇬🇧": "Великобритания", "🇬🇩": "Гренада", "🇬🇪": "Грузия", "🇬🇫": "Французская Гвиана",
    "🇬🇬": "Гернси", "🇬🇭": "Гана", "🇬🇮": "Гибралтар", "🇬🇱": "Гренландия",
    "🇬🇲": "Гамбия", "🇬🇳": "Гвинея", "🇬🇵": "Гваделупа", "🇬🇶": "Экваториальная Гвинея",
    "🇬🇷": "Греция", "🇬🇸": "Южная Георгия", "🇬🇹": "Гватемала", "🇬🇺": "Гуам",
    "🇬🇼": "Гвинея-Бисау", "🇬🇾": "Гайана", "🇭🇰": "Гонконг", "🇭🇲": "Херд и Макдональд",
    "🇭🇳": "Гондурас", "🇭🇷": "Хорватия", "🇭🇹": "Гаити", "🇭🇺": "Венгрия",
    "🇮🇨": "Канарские о-ва", "🇮🇩": "Индонезия", "🇮🇪": "Ирландия", "🇮🇱": "Израиль",
    "🇮🇲": "Остров Мэн", "🇮🇳": "Индия", "🇮🇴": "Британская Территория в Индийском Океане",
    "🇮🇶": "Ирак", "🇮🇷": "Иран", "🇮🇸": "Исландия", "🇮🇹": "Италия",
    "🇯🇪": "Джерси", "🇯🇲": "Ямайка", "🇯🇴": "Иордания", "🇯🇵": "Япония",
    "🇰🇪": "Кения", "🇰🇬": "Киргизия", "🇰🇭": "Камбоджа", "🇰🇮": "Кирибати",
    "🇰🇲": "Коморы", "🇰🇳": "Сент-Китс и Невис", "🇰🇵": "Северная Корея", "🇰🇷": "Южная Корея",
    "🇰🇼": "Кувейт", "🇰🇾": "Каймановы о-ва", "🇰🇿": "Казахстан", "🇱🇦": "Лаос",
    "🇱🇧": "Ливан", "🇱🇨": "Сент-Люсия", "🇱🇮": "Лихтенштейн", "🇱🇰": "Шри-Ланка",
    "🇱🇷": "Либерия", "🇱🇸": "Лесото", "🇱🇹": "Литва", "🇱🇺": "Люксембург",
    "🇱🇻": "Латвия", "🇱🇾": "Ливия", "🇲🇦": "Марокко", "🇲🇨": "Монако", "🇲🇩": "Молдова",
    "🇲🇪": "Черногория", "🇲🇫": "Сен-Мартен", "🇲🇬": "Мадагаскар", "🇲🇭": "Маршалловы о-ва",
    "🇲🇰": "Северная Македония", "🇲🇱": "Мали", "🇲🇲": "Мьянма", "🇲🇳": "Монголия",
    "🇲🇴": "Макао", "🇲🇵": "Северные Марианские о-ва", "🇲🇶": "Мартиника", "🇲🇷": "Мавритания",
    "🇲🇸": "Монтсеррат", "🇲🇹": "Мальта", "🇲🇺": "Маврикий", "🇲🇻": "Мальдивы",
    "🇲🇼": "Малави", "🇲🇽": "Мексика", "🇲🇾": "Малайзия", "🇲🇿": "Мозамбик",
    "🇳🇦": "Намибия", "🇳🇨": "Новая Каледония", "🇳🇪": "Нигер", "🇳🇫": "Норфолк",
    "🇳🇬": "Нигерия", "🇳🇮": "Никарагуа", "🇳🇱": "Нидерланды", "🇳🇴": "Норвегия",
    "🇳🇵": "Непал", "🇳🇷": "Науру", "🇳🇺": "Ниуэ", "🇳🇿": "Новая Зеландия",
    "🇴🇲": "Оман", "🇵🇦": "Панама", "🇵🇪": "Перу", "🇵🇫": "Французская Полинезия",
    "🇵🇬": "Папуа-Новая Гвинея", "🇵🇭": "Филиппины", "🇵🇰": "Пакистан", "🇵🇱": "Польша",
    "🇵🇲": "Сен-Пьер и Микелон", "🇵🇳": "Острова Питкэрн", "🇵🇷": "Пуэрто-Рико",
    "🇵🇸": "Палестина", "🇵🇹": "Португалия", "🇵🇼": "Палау", "🇵🇾": "Парагвай",
    "🇶🇦": "Катар", "🇷🇪": "Реюньон", "🇷🇴": "Румыния", "🇷🇸": "Сербия", "🇷🇺": "Россия",
    "🇷🇼": "Руанда", "🇸🇦": "Саудовская Аравия", "🇸🇧": "Соломоновы о-ва", "🇸🇨": "Сейшелы",
    "🇸🇩": "Судан", "🇸🇪": "Швеция", "🇸🇬": "Сингапур", "🇸🇭": "Остров Святой Елены",
    "🇸🇮": "Словения", "🇸🇯": "Шпицберген и Ян-Майен", "🇸🇰": "Словакия", "🇸🇱": "Сьерра-Леоне",
    "🇸🇲": "Сан-Марино", "🇸🇳": "Сенегал", "🇸🇴": "Сомали", "🇸🇷": "Суринам",
    "🇸🇸": "Южный Судан", "🇸🇹": "Сан-Томе и Принсипи", "🇸🇻": "Эль-Сальвадор",
    "🇸🇽": "Синт-Мартен", "🇸🇾": "Сирия", "🇸🇿": "Эсватини", "🇹🇦": "Тристан-да-Кунья",
    "🇹🇨": "Теркс и Кайкос", "🇹🇩": "Чад", "🇹🇫": "Южные территории Франции",
    "🇹🇬": "Того", "🇹🇭": "Таиланд", "🇹🇯": "Таджикистан", "🇹🇰": "Токелау",
    "🇹🇱": "Восточный Тимор", "🇹🇲": "Туркменистан", "🇹🇳": "Тунис", "🇹🇴": "Тонга",
    "🇹🇷": "Турция", "🇹🇹": "Тринидад и Тобаго", "🇹🇻": "Тувалу", "🇹🇼": "Тайвань",
    "🇹🇿": "Танзания", "🇺🇦": "Украина", "🇺🇬": "Уганда", "🇺🇲": "Внешние малые острова США",
    "🇺🇳": "ООН", "🇺🇸": "США", "🇺🇾": "Уругвай", "🇺🇿": "Узбекистан",
    "🇻🇦": "Ватикан", "🇻🇨": "Сент-Винсент и Гренадины", "🇻🇪": "Венесуэла",
    "🇻🇬": "Британские Виргинские о-ва", "🇻🇮": "Виргинские о-ва США", "🇻🇳": "Вьетнам",
    "🇻🇺": "Вануату", "🇼🇫": "Уоллис и Футуна", "🇼🇸": "Самоа", "🇽🇰": "Косово",
    "🇾🇪": "Йемен", "🇾🇹": "Майотта", "🇿🇦": "ЮАР", "🇿🇲": "Замбия", "🇿🇼": "Зимбабве"
}

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def extract_host(link):
    m = re.search(r'@([\w\.\-]+):', link)
    return m.group(1) if m else None

def extract_sni(link):
    try:
        base = link.split("#")[0]
        qs = urlparse(base).query
        sni = parse_qs(qs).get('sni', [None])[0]
        return sni.lower() if sni else None
    except:
        return None

def get_flag_info(raw_fragment):
    if not raw_fragment:
        return "🌐", "Не определено"
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_fragment)
    if flags:
        flag = flags[0]
        country = FLAG_DB.get(flag, "🌐 Не определено")
        return flag, country
    return "🌐", "Не определено"

def parse_source(url):
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for result in executor.map(parse_source, SOURCES):
            all_configs.extend(result)

    if not all_configs:
        print("❌ Не найдено ни одного конфига")
        return

    random.shuffle(all_configs)
    selected = all_configs[:3000]

    final_lines = []
    hosts_set = set()
    sni_set = set()

    for link in selected:
        try:
            base, fragment = link.split("#", 1)
        except ValueError:
            base = link
            fragment = ""

        host = extract_host(base)
        if host:
            hosts_set.add(host)

        sni = extract_sni(base)
        if sni:
            sni_set.add(sni)
        sni_text = sni if sni else "Не определён"

        flag, country = get_flag_info(fragment)
        if flag == "🌐":
            country_text = "🌐 Не определено"
        else:
            country_text = f"{flag} {country}"

        display_name = f"{country_text} | SNI: {sni_text} | 🌴ЯлтаВПН"
        safe_name = urllib.parse.quote(display_name, safe='')

        final_lines.append(f"{base}#{safe_name}")

    total_hosts = len(hosts_set)
    total_sni = len(sni_set)

    # Собираем полный текст с заголовками профиля
    content = "\n".join(final_lines)
    full_text = f"""#profile-update-interval: 1
#support-url: https://t.me/YaltaVPN_Obxod
#profile-title: 🌴ЯлтаВПН - Курортный ВПН
#hide-settings: 1
{content}"""

    b64 = base64.b64encode(full_text.encode("utf-8")).decode("utf-8")
    filename = "YaltaVPN.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(b64)

    print("\n" + "="*50)
    print("🌴ЯлтаВПН - Курортный ВПН")
    print(f"🌴ЯлтаВПН | CIDR: {total_hosts} | SNI: {total_sni} |")
    print("📢 ТГ канал: https://t.me/YaltaVPN_Obxod")
    print("="*50)
    print(f"✅ Сохранено {len(final_lines)} конфигов в файл {filename} (с мета-заголовками в base64)")

if __name__ == "__main__":
    main()
