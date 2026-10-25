# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Proqramlaşdırmanın əsasları — 1-ci kurs, qrup 136a1 — SDF 1 (Variant D)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
   Funksiya nəticəni qaytara (`return`) və ya ekrana çıxara (`print`) bilər — hər ikisi qəbul olunur.
3. Faylı işə salın:   python variant_D.py
4. Hər tapşırıq dərhal yoxlanır:
       ✅ Tapşırıq T3: DÜZGÜNDÜR (+10 bal)
       🟡 Tapşırıq T3: QİSMƏN DÜZGÜNDÜR (+6 / 10 bal)   (altında hansı hissənin ödənmədiyi göstərilir)
       ❌ Tapşırıq T3: XƏTA — ...
   Faylın sonunda yekun balınız çap olunur.

Qiymətləndirmə: bəzi kod tapşırıqları yalnız 0 və ya 10 bal, digərləri isə hissə-hissə (0–10 arası) qiymətləndirilir.
Hər tapşırığın başlığında bu qeyd olunub.

Qeyd: bir tapşırıqdakı icra xətası digər tapşırıqları dayandırmır.
SyntaxError (məs. mötərizə və ya girinti səhvi) isə bütün faylın işləməsinə mane olur —
Python xətanın sətrini göstərəcək, onu düzəldib yenidən işlədin.

Bu fayl tools/build_bank.py ilə yaradılıb.
"""

import ast
import contextlib
import copy
import hashlib
import io
import math
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

results = {}
_errors = {}


def _h(x):
    return hashlib.sha256(str(x).strip().lower().encode()).hexdigest()


def _plain(v):
    """tuple / set kimi dəyərləri adi Python siyahısına çevirir (tolerant müqayisə üçün)."""
    if hasattr(v, "tolist"):
        v = v.tolist()
    if isinstance(v, (set, frozenset)):
        try:
            v = sorted(v)
        except TypeError:
            v = list(v)
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    return v


def _close(a, b):
    """Ədəd müqayisəsi: 5 == 5.0; kəsr ədədlər kiçik yuvarlaqlaşdırma fərqi ilə bərabər sayılır (məs. 1.41 və 1.41421)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    try:
        if math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-9):
            return True
        if isinstance(b, float) and not float(b).is_integer():
            return abs(a - b) <= 0.006
        return False
    except TypeError:
        return False


def _eq(a, b):
    """Tolerant bərabərlik: list ≈ tuple, 1.0 ≈ 1, kiçik yuvarlaqlaşdırma fərqi qəbul olunur."""
    a, b = _plain(a), _plain(b)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_eq(a[k], b[k]) for k in a)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return _close(a, b)
    return a == b


_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _nums(text):
    """Mətndəki bütün ədədlər, məs. 'ƏBOB: 6, ƏKOB: 36' -> [6, 36]."""
    return [float(m) if "." in m else int(m) for m in _NUM_RE.findall(str(text))]


def _call(fn, *args):
    """
    Tələbənin funksiyasını arqumentlərin surəti ilə çağırır.
    Qaytarılan dəyər götürülür; funksiya heç nə qaytarmırsa, ekrana çıxardığı mətn götürülür;
    yalnız siyahı arqumentini yerində dəyişibsə (məs. çeşidləmə), həmin siyahı götürülür.
    """
    args = copy.deepcopy(args)
    before = copy.deepcopy(args)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(*args)
    printed = buf.getvalue()
    if printed:
        sys.stdout.write(printed)
    if result is None:
        if printed.strip():
            return printed.strip()
        for now, was in zip(args, before):
            if isinstance(now, list) and now != was:
                return now
    return result


# Bəli / xeyr sözləri (azərbaycanca və ingiliscə). İnkar: deyil, yox, mürəkkəb, -mır/-mir/-mur/-mür (gətirmir, bölünmür) ...
_NO = re.compile(r"\b(not|no|non|isn'?t|aren'?t|doesn'?t|does not|cannot|can'?t|invalid|composite|common|false|"
                 r"deyil|deyildir|yox|xeyr|mürəkkəb|adi|yanlış|səhv)\b|\w+m[ıiuü]r\b")
_YES = re.compile(r"\b(yes|true|prime|leap|valid|palindrome|forms?|triangle|divisible|"
                  r"bəli|hə|doğru|düzgün|sadə|uyğun|palindrom|polindrom|üçbucaq|uzun|bölünür|gətirir)|"
                  r"(dır|dir|dur|dür)\b")


def _yes(v):
    """Bəli-xeyr cavabından True / False: True, 1, 'Sadə ədəddir', 'Polindrom deyil', 'Uzun ildir' ..."""
    if isinstance(v, bool):
        return v
    if isinstance(v, int) and v in (0, 1):
        return bool(v)
    if isinstance(v, str):
        t = v.casefold()
        if _NO.search(t):
            return False
        if _YES.search(t):
            return True
    return None


def _clean_text(s):
    return " ".join(str(s).strip().strip("'\"").split())


def _same(got, exp):
    """Tələbənin cavabı (qaytarılan və ya çap olunan) gözlənilən dəyərə bərabərdirmi? Formata tolerantdır."""
    if isinstance(exp, bool):
        return _yes(got) is exp
    if got is None:
        return False
    if isinstance(exp, str):
        g, e = _clean_text(got), _clean_text(exp)
        if g == e:
            return True
        # cavabdan əvvəl izah ola bilər: "Ən uzun söz: 'Proqramlaşdırma'"
        g = g.rstrip(".!").strip("'\"")
        return g == e or (g.endswith(e) and g[-len(e) - 1] in " :='\"-")
    if isinstance(got, str):
        text = got.strip()
        try:
            if _eq(ast.literal_eval(text), exp):
                return True
        except Exception:
            pass
        if isinstance(exp, dict):
            m = re.search(r"\{.*\}", text, re.S)
            if m:
                try:
                    return _eq(ast.literal_eval(m.group(0)), exp)
                except Exception:
                    return False
            return False
        if isinstance(exp, (list, tuple)) and exp and all(isinstance(x, (int, float)) for x in exp):
            m = re.search(r"\[.*\]|\(.*\)", text, re.S)
            if m:
                try:
                    if _eq(ast.literal_eval(m.group(0)), exp):
                        return True
                except Exception:
                    pass
            after_label = [float(x) if "." in x else int(x) for x in re.findall(r"[:=]\s*(-?\d+(?:\.\d+)?)", text)]
            if after_label and _eq(after_label, list(exp)):
                return True       # "Sətir 1 cəmi: 6, Sətir 2 cəmi: 15" -> [6, 15]
            ns = _nums(text)
            return len(ns) >= len(exp) and _eq(ns[len(ns) - len(exp):], list(exp))
        if isinstance(exp, (list, tuple)) and not exp:
            return text in ("[]", "()", "")
        if isinstance(exp, (int, float)):
            ns = _nums(text)
            after_label = [float(x) if "." in x else int(x) for x in re.findall(r"[:=]\s*(-?\d+(?:\.\d+)?)", text)]
            return any(_close(x, exp) for x in ns[-1:] + after_label)
        return False
    if isinstance(exp, (int, float)) and isinstance(got, (list, tuple)) and len(got) == 1:
        got = got[0]
    return _eq(got, exp)


def _seq(got, n):
    """Cavab n dəyərdən ibarət siyahı kimi (tuple/list-dən və ya çap olunan mətnin son n ədədindən)."""
    if isinstance(got, str):
        ns = _nums(got)
        return ns[len(ns) - n:] if len(ns) >= n else None
    v = _plain(got)
    return v if isinstance(v, list) and len(v) == n else None


def _lines(got):
    """Mətn naxışı sətirlər siyahısı kimi (sondakı boşluqlar və boş sətirlər nəzərə alınmır)."""
    if got is None:
        return []
    if isinstance(got, (list, tuple)):
        rows = [str(x) for x in got]
    else:
        rows = str(got).split("\n")
    return [r.rstrip() for r in rows if r.strip()]



def _flat(got):
    """Cavabdakı bütün ədədlər düz siyahı kimi (iç-içə siyahılar açılır, mətndən ədədlər götürülür)."""
    if got is None:
        return []
    if isinstance(got, str):
        return _nums(got)
    v = _plain(got)
    if isinstance(v, list):
        out = []
        for x in v:
            out += _flat(x) if isinstance(x, (list, tuple, str)) else [x]
        return out
    return [v]


def _same_set(got, exp):
    """Sıradan asılı olmayan müqayisə (məs. iki siyahının kəsişməsi): elementlər eyni olmalıdır."""
    if got is None:
        return False
    return sorted(_flat(got)) == sorted(exp)


def _has_word(got, *words):
    """Cavab mətnində sözlərdən biri varmı (kiçik/böyük hərf fərqi nəzərə alınmır)."""
    if got is None:
        return False
    t = str(got).casefold()
    return any(re.search(r"(?<!\w)" + re.escape(w.casefold()), t) for w in words)


def grade(*items):
    """
    Qismən bal üçün: items = (çəki, "yoxlanılan hissə", çağırıla bilən) ...
    Hər hissə ayrıca yoxlanılır; ödənən hissələrin çəkisi toplanır.
    Qaytarır: (qazanılan_çəki, ümumi_çəki, [ödənməyən hissələrin təsviri]).
    """
    got = tot = 0
    failed = []
    for w, label, fn in items:
        tot += w
        try:
            r = fn()
            if r is None or (isinstance(r, bool) and not r):
                raise AssertionError
            got += w
        except AssertionError:
            failed.append(label)
        except Exception as e:
            failed.append(f"{label} ({type(e).__name__}: {e})")
    return (got, tot, failed)


class hell:
    """Tapşırıq blokunu qoruyur: blokdakı xəta yadda saxlanır, fayl isə işləməyə davam edir."""

    def __init__(self, task_id):
        self.task_id = task_id

    def __enter__(self):
        _errors.pop(self.task_id, None)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            return False
        _errors[self.task_id] = f"kodunuz icra olunarkən xəta baş verdi → {exc_type.__name__}: {exc}"
        return True


def check(task_id, points, test):
    """Testi işlədir, nəticəni `results`-də saxlayır və ekrana rəy çıxarır (tam və ya qismən bal)."""
    tid = task_id.split("_")[0]
    reason = ""
    try:
        res = test()
        if isinstance(res, tuple) and len(res) == 3:
            got, tot, failed = res
            pts = int(points * got / tot + 0.5) if tot else 0
            results[task_id] = pts
            if pts >= points:
                print(f"✅ Tapşırıq {tid}: DÜZGÜNDÜR (+{points} bal)")
                return
            reason = "Ödənməyən hissələr: " + "; ".join(failed)
            if pts > 0:
                print(f"🟡 Tapşırıq {tid}: QİSMƏN DÜZGÜNDÜR (+{pts} / {points} bal)")
                print(f"   ↳ {reason}")
                return
        else:
            results[task_id] = points
            print(f"✅ Tapşırıq {tid}: DÜZGÜNDÜR (+{points} bal)")
            return
    except AssertionError as e:
        reason = str(e) or "test şərti ödənmədi"
    except NameError as e:
        reason = f"tələb olunan funksiya / dəyişən təyin edilməyib ({e})"
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
    results[task_id] = 0
    if tid in _errors:
        reason = _errors[tid]
    print(f"❌ Tapşırıq {tid}: XƏTA — qaytarılan / çap olunan nəticə gözlənilən nəticəyə uyğun deyil!")
    print(f"   ↳ Səbəb: {reason}")


ad_soyad = "..."      # Bura ad və soyadınızı yazın
qrup = "136a1"        # Qrup nömrəniz


# ======================================================================
# Tapşırıq T1. break, continue və dövrün else bloku (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# for i in range(1, 6):
#     if i == 2:
#         continue
#     if i == 4:
#         break
#     print(i)
# else:
#     print("bitdi")
#
#   a) 1 və 3 — continue 2-ni buraxır, break 4-də dövrü dayandırır, break olduğu üçün else bloku icra olunmur
#   b) 1, 3, 5 və bitdi — break yalnız cari təkrarı dayandırır
#   c) 1, 2 və 3 — continue dövrü tamamilə dayandırır
#   d) 1, 3 və bitdi — dövrün else bloku həmişə icra olunur
# ======================================================================

cavab_T1 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t1():
    assert _h(cavab_T1) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Köməkçi diaqonalın maksimumu (10 bal) — Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# N × N ölçülü kvadrat matrisin köməkçi diaqonalında (sağ yuxarı küncdən sol aşağı küncə) yerləşən elementlərin
# maksimumunu tapan komekci_diaqonal_max(matris) funksiyasını yazın.
#
# Nümunə: komekci_diaqonal_max([[1, 9], [3, 4]]) → 9  (9 və 3-dən ən böyüyü)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T2"):
    def komekci_diaqonal_max(matris):
        # kodunuzu bura yazın
        pass


def test_t2():
    return grade(
        (4, "komekci_diaqonal_max([[1, 9], [3, 4]]) 9 olmalıdır", lambda: _same(_call(komekci_diaqonal_max, [[1, 9], [3, 4]]), 9)),
        (4, "3 × 3: [[1, 2, 3], [4, 5, 6], [70, 8, 9]] -> 70 (köməkçi diaqonal: 3, 5, 70)",
         lambda: _same(_call(komekci_diaqonal_max, [[1, 2, 3], [4, 5, 6], [70, 8, 9]]), 70)),
        (2, "baş diaqonal yox, köməkçi diaqonal: [[100, 1], [2, 100]] -> 2",
         lambda: _same(_call(komekci_diaqonal_max, [[100, 1], [2, 100]]), 2)),
    )
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. Dinamik tipləşdirmə və girintilər (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Python-da dinamik tipləşdirmə və girintilər (indentation) haqqında hansı ifadə düzgündür?
#   a) Hər dəyişən tipi ilə elan olunmalıdır, məsələn int x = 5, və bu tip sonradan heç vaxt dəyişə bilməz
#   b) Tip dəyişənə deyil, obyektə aiddir, ona görə eyni ad əvvəl int, sonra str obyektinə istinad edə bilər; girinti sintaksisin hissəsidir — if, for, def … sonrakı blokları müəyyən edir, səhv girinti IndentationError yaradır
#   c) x = 5 yazıldıqdan sonra x = "salam" əmri TypeError verir, çünki x artıq tam ədəd tipindədir
#   d) Girintilər yalnız oxunaqlılıq üçündür; Python blokları fiqurlu mötərizələrlə { } müəyyən edir
# ======================================================================

cavab_T3 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t3():
    assert _h(cavab_T3) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "seçilmiş cavab düzgün deyil"
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Polindrom söz (10 bal) — Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# Sözün polindrom (soldan sağa və sağdan sola eyni oxunan, məs. 'ana', 'kələk', 'radar') olub-olmadığını yoxlayan
# polindrom_soz(soz) funksiyasını yazın. Funksiya True / False qaytarsın (və ya "Polindromdur" / "Polindrom deyil" çap etsin).
#
# Nümunə: polindrom_soz("radar") → True
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T4"):
    def polindrom_soz(soz):
        # kodunuzu bura yazın
        pass


def test_t4():
    assert _same(_call(polindrom_soz, "radar"), True), "'radar' polindromdur"
    assert _same(_call(polindrom_soz, "kələk"), True), "'kələk' polindromdur"
    assert _same(_call(polindrom_soz, "ana"), True), "'ana' polindromdur"
    assert _same(_call(polindrom_soz, "python"), False), "'python' polindrom deyil"
    assert _same(_call(polindrom_soz, "abca"), False), "'abca' polindrom deyil"
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Truthy və falsy dəyərlər (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Hansı siyahıda yalnız şərt daxilində False kimi qiymətləndirilən (falsy) dəyərlər var?
#   a) 0, 0.0, '', [], {}, None, False
#   b) None, [0], 0.0, ''
#   c) 0, '0', [], None
#   d) False, ' ' (boşluq simvolu), (), 0
# ======================================================================

cavab_T5 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t5():
    assert _h(cavab_T5) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. 1-dən N-ə qədər ədədlərin cəmi (10 bal) — Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While)
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# 1-dən N-ə qədər (N daxil) olan tam ədədlərin cəmini dövr vasitəsilə hesablayan cem_1_n(n) funksiyasını yazın.
#
# Nümunə: cem_1_n(10) → 55  (Cəm = 55)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T6"):
    def cem_1_n(n):
        # kodunuzu bura yazın
        pass


def test_t6():
    assert _same(_call(cem_1_n, 10), 55), "cem_1_n(10) 55 olmalıdır"
    assert _same(_call(cem_1_n, 1), 1), "cem_1_n(1) 1 olmalıdır"
    assert _same(_call(cem_1_n, 100), 5050), "cem_1_n(100) 5050 olmalıdır (N özü də daxildir)"
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. Siyahı metodları (append, insert, remove, pop) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# a = [3, 1, 2]
# a.append(5)
# a.insert(0, 9)
# a.remove(1)
# x = a.pop()
# print(a, x)
#
#   a) [9, 2, 5] 3
#   b) [3, 2, 5] 9
#   c) [9, 3, 2, 5] 5
#   d) [9, 3, 2] 5
# ======================================================================

cavab_T7 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t7():
    assert _h(cavab_T7) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "seçilmiş cavab düzgün deyil"
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. İki dəyişənin qiymətlərinin yerini dəyişmək (10 bal) — Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# İki dəyişənin (a və b) qiymətlərini üçüncü köməkçi dəyişəndən istifadə etmədən (Pythonic swap) dəyişən
# yer_deyis(a, b) funksiyasını yazın. Funksiya yeni qiymətləri a, b ardıcıllığı ilə qaytarsın.
#
# Nümunə: yer_deyis(5, 9) → (9, 5)  (a = 9, b = 5)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T8"):
    def yer_deyis(a, b):
        # kodunuzu bura yazın
        pass


def test_t8():
    assert _same(_call(yer_deyis, 5, 9), (9, 5)), "yer_deyis(5, 9) (9, 5) olmalıdır"
    assert _same(_call(yer_deyis, -1, 7), (7, -1)), "yer_deyis(-1, 7) (7, -1) olmalıdır"
    assert _same(_call(yer_deyis, 4, 4), (4, 4)), "yer_deyis(4, 4) (4, 4) olmalıdır"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Bala görə qiymət hərfi (10 bal) — Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Tələbənin imtahan balına (0–100) görə qiymət hərfini qaytaran qiymet_herfi(bal) funksiyasını yazın:
# 91–100: A, 81–90: B, 71–80: C, 61–70: D, 51–60: E, 0–50: F.
#
# Nümunə: qiymet_herfi(85) → "B"  (Qiymət: B)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T9"):
    def qiymet_herfi(bal):
        # kodunuzu bura yazın
        pass


def test_t9():
    return grade(
        (3, "qiymet_herfi(85) B, qiymet_herfi(95) A olmalıdır",
         lambda: _same(_call(qiymet_herfi, 85), "B") and _same(_call(qiymet_herfi, 95), "A")),
        (3, "qiymet_herfi(75) C, (65) D, (55) E olmalıdır",
         lambda: _same(_call(qiymet_herfi, 75), "C") and _same(_call(qiymet_herfi, 65), "D") and _same(_call(qiymet_herfi, 55), "E")),
        (2, "qiymet_herfi(30) F olmalıdır", lambda: _same(_call(qiymet_herfi, 30), "F")),
        (2, "sərhəd qiymətləri: 91 → A, 90 → B, 51 → E, 50 → F",
         lambda: all(_same(_call(qiymet_herfi, b), h) for b, h in ((91, "A"), (90, "B"), (51, "E"), (50, "F")))),
    )
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. Rəqəmlərin sayı və cəmi (while ilə) (10 bal) — Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While)
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Tam ədədin rəqəmlərinin sayını və rəqəmlərinin cəmini while dövrü ilə hesablayan reqem_say_cem(n) funksiyasını yazın.
# Funksiya iki qiymət qaytarsın: say, cem.
#
# Nümunə: reqem_say_cem(4052) → (4, 11)  (Rəqəm sayı: 4, Rəqəm cəmi: 11)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T10"):
    def reqem_say_cem(n):
        # kodunuzu bura yazın
        pass


def test_t10():
    cases = [(4052, (4, 11)), (7, (1, 7)), (99999, (5, 45)), (1000, (4, 1))]
    res = [_seq(_call(reqem_say_cem, n), 2) for n, _ in cases]
    return grade(
        (5, "rəqəmlərin sayı", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
        (5, "rəqəmlərin cəmi", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
    )
check("T10", 10, test_t10)



# ======================================================================
# YEKUN NƏTİCƏ
# ======================================================================
MAX_POINTS = {'T1': 10, 'T2': 10, 'T3': 10, 'T4': 10, 'T5': 10, 'T6': 10, 'T7': 10, 'T8': 10, 'T9': 10, 'T10': 10}

total = 0
print()
print(f"{'Tapşırıq':<12}{'Nəticə':<10}{'Bal':>6}")
print("-" * 30)
for k, p in MAX_POINTS.items():
    got = results.get(k)
    if got is None:
        status, earned = "—", 0
    elif got == p:
        status, earned = "✅", got
    elif got > 0:
        status, earned = "🟡", got
    else:
        status, earned = "❌", got
    total += earned
    print(f"{k:<12}{status:<10}{earned:>3}/{p}")

max_total = sum(MAX_POINTS.values())
print("-" * 30)
print(f"YEKUN İMTAHAN BALI: {total} / {max_total}  ({total / max_total * 100:.0f}%)")
