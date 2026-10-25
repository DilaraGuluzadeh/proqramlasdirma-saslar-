# -*- coding: utf-8 -*-
"""Qismən bal və tolerantlıq sınağı (build_bank.py --verify istifadə edir).

Hər sınaq bilərəkdən natamam və ya fərqli formatda yazılmış həll və onun alması lazım olan baldır.
Tolerant formatlar (return əvəzinə print, izahlı cavab, funksiyanın adının dəyişdirilməsi, Tab girinti) tam bal almalıdır.
"""

PROBES = {
    # --- natamam həllər -> qismən bal
    "A11": ("def reqemler_cemi(n):\n    return n // 100 + n % 10", 4),                         # orta rəqəm unudulub
    "A16": ("def ilk_son(n):\n    return n // 1000, n % 10, 0", 6),                              # cəm yoxdur
    "B8": ("def qiymet_herfi(bal):\n    if bal > 90:\n        return 'A'\n    elif bal > 80:\n        return 'B'\n"
           "    elif bal > 70:\n        return 'C'\n    else:\n        return 'F'", 5),                 # D, E yoxdur
    "B9": ("def ucbucaqdir(a, b, c):\n    return a + b > c", 7),                                    # yalnız bir bərabərsizlik
    "B14": ("def kalkulyator(a, b, emel):\n    if emel == '+': return a + b\n    if emel == '-': return a - b\n"
            "    if emel == '*': return a * b\n    if emel == '/': return a / b", 8),             # sıfıra bölmə yoxlanmayıb
    "C6": ("def sade_ededdir(n):\n    for d in range(2, n):\n        if n % d == 0:\n            return False\n    return True", 7),
    "C10": ("def ebob_ekob(a, b):\n    import math\n    return math.gcd(a, b), a * b", 5),         # ƏKOB səhv
    "C14": ("def cem_orta(ededler):\n    return sum(ededler), sum(ededler) / len(ededler)", 0),  # 0-dan sonrakılar da sayılır
    "D4": ("def max_min_indeks(lst):\n    return max(lst), 0, min(lst), 0", 6),                  # indekslər səhv
    "D8": ("def unikal(lst):\n    return list(set(lst))", 7),                                     # sıra saxlanmayıb
    "D9": ("def saga_surusdur(lst, k):\n    return lst[-k:] + lst[:-k]", 7),                       # K > uzunluq nəzərə alınmayıb
    "D13": ("def komekci_diaqonal_max(matris):\n    return max(matris[i][i] for i in range(len(matris)))", 0),
    "E4": ("def sait_samit(metn):\n    s = sum(1 for c in metn.lower() if c in 'aeiou')\n"
           "    return s, sum(1 for c in metn if c.isalpha()) - s", 0),                            # ə, ö, ü, ı unudulub
    "B11": ("def rub(x, y):\n    if x > 0 and y > 0:\n        return 'I rüb'\n    elif x < 0 and y > 0:\n        return 'II rüb'\n"
            "    elif x < 0 and y < 0:\n        return 'III rüb'\n    else:\n        return 'IV rüb'", 8),   # oxlar yoxdur
    # --- tolerant formatlar -> tam bal
    "A12": ("def saniye_cevir(saniye):\n    s = saniye // 3600\n    d = saniye % 3600 // 60\n    print(s, 'saat,', d, 'dəqiqə,', saniye % 60, 'saniyə')", 10),
    "C9": ("def ters_eded(n):\n    print('Tərs ədəd:', str(n)[::-1])", 10),
    "B10": ("def uzun_ildir(il):\n    if (il % 4 == 0 and il % 100 != 0) or il % 400 == 0:\n        print('Uzun ildir')\n"
            "    else:\n        print('Uzun il deyil')", 10),
    "B15": ("def uc_ve_bese_bolunur(n):\n    if n % 15 == 0:\n        print('Ədəd həm 3-ə, həm də 5-ə bölünür')\n"
            "    else:\n        print('Bölünmür')", 10),
    "B12": ("def polindrom_eded(n):\n    return 'Polindromdur' if str(n) == str(n)[::-1] else 'Polindrom deyil'", 10),
    "B16": ("def fesil(ay):\n    if ay in [12, 1, 2]: print('Qış fəsli')\n    elif ay <= 5: print('Yaz fəsli')\n"
            "    elif ay <= 8: print('Yay fəsli')\n    else: print('Payız fəsli')", 10),
    "B5": ("def cut_tek(n):\n    print('Cüt ədəd' if n % 2 == 0 else 'Tək ədəd')", 10),
    "E14": ("from collections import Counter\ndef simvol_tezliyi(metn):\n    return Counter(metn)", 10),
    "E12": ("def menim_ebob(a, b):\n\twhile b:\n\t\ta, b = b, a % b\n\treturn a", 10),             # ad dəyişib + Tab
    "D7": ("def bubble_sort(lst):\n    n = len(lst)\n    for i in range(n):\n        for j in range(n - 1):\n"
           "            if lst[j] > lst[j + 1]:\n                lst[j], lst[j + 1] = lst[j + 1], lst[j]", 10),   # return yoxdur
    "A14": ("import math\ndef mesafe(x1, y1, x2, y2):\n    return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 2)", 10),
    "C13": ("def ulduz_ucbucaq(n):\n    return '\\n'.join('*' * i for i in range(1, n + 1))", 10),
    "C15": ("def bolenler(n):\n    b = [d for d in range(1, n + 1) if n % d == 0]\n    print('Bölənlər:', ', '.join(map(str, b)), f'(Sayı: {len(b)})')", 10),
    "D16": ("def kesisme(lst1, lst2):\n    return set(lst1) & set(lst2)", 10),
    "D11": ("def setir_cemleri(matris):\n    for i, s in enumerate(matris, 1):\n        print(f'Sətir {i} cəmi: {sum(s)}')", 10),
    "E13": ("def en_uzun_soz(cumle):\n    print(\"Ən uzun söz: '\" + max(cumle.split(), key=len) + \"'\")", 10),
    "B6": ("def isare(n):\n    print('Müsbət ədəd' if n > 0 else 'Mənfi ədəd' if n < 0 else 'Sıfıra bərabərdir')", 10),
    # --- yuxarı səviyyədə input() -> aydın mesaj, 0 bal
    "E10": ("n = int(input())\ndef factorial_recursive(n):\n    return 1 if n <= 1 else n * factorial_recursive(n - 1)", 0),
}
