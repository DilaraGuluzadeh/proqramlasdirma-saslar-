# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Proqramlaşdırmanın əsasları — 1-ci kurs, qrup 136a1 — SDF 1 (Variant C)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
   Funksiya nəticəni qaytara (`return`) və ya ekrana çıxara (`print`) bilər — hər ikisi qəbul olunur.
3. Faylı işə salın:   python variant_C.py
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
# Tapşırıq T1. range(start, stop, step) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Hansı çağırış dəqiq 10, 7, 4, 1 ədədlərini verir?
#   a) range(10, 0, -3)
#   b) range(1, 10, 3)
#   c) range(10, -3)
#   d) range(10, 1, -3)
# ======================================================================

cavab_T1 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t1():
    assert _h(cavab_T1) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Müsbət, mənfi və ya sıfır (10 bal) — Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Ədədin müsbət, mənfi və ya sıfıra bərabər olduğunu yoxlayan isare(n) funksiyasını yazın.
# Funksiya "Müsbət", "Mənfi" və ya "Sıfır" qaytarsın (və ya məs. "Mənfi ədəd" çap etsin).
#
# Nümunə: isare(-15) → "Mənfi"
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T2"):
    def isare(n):
        # kodunuzu bura yazın
        pass


def test_t2():
    def kind(n):
        r = _call(isare, n)
        if _has_word(r, "müsbət", "musbet", "positive"):
            return "+"
        if _has_word(r, "mənfi", "menfi", "negative"):
            return "-"
        if _has_word(r, "sıfır", "sifir", "zero") or _same(r, 0):
            return "0"
        return None
    return grade(
        (4, "isare(-15) Mənfi olmalıdır", lambda: kind(-15) == "-"),
        (3, "isare(8) Müsbət olmalıdır", lambda: kind(8) == "+"),
        (3, "isare(0) Sıfır olmalıdır", lambda: kind(0) == "0"),
    )
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. Siyahının orta qiyməti (10 bal) — Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Ədəd siyahısı qəbul edən və onun elementlərinin orta qiymətini qaytaran calculate_average(lst) funksiyasını yazın.
#
# Nümunə: calculate_average([10, 20, 30, 40]) → 25.0
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T3"):
    def calculate_average(lst):
        # kodunuzu bura yazın
        pass


def test_t3():
    return grade(
        (5, "calculate_average([10, 20, 30, 40]) 25.0 olmalıdır", lambda: _same(_call(calculate_average, [10, 20, 30, 40]), 25.0)),
        (3, "kəsr nəticə: calculate_average([1, 2]) 1.5 olmalıdır", lambda: _same(_call(calculate_average, [1, 2]), 1.5)),
        (2, "mənfi ədədlər: calculate_average([-4, 4, 3]) 1.0 olmalıdır", lambda: _same(_call(calculate_average, [-4, 4, 3]), 1.0)),
    )
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. İç-içə if və girintilər (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# x = 7
# if x > 0:
#     if x % 2 == 0:
#         print("müsbət cüt")
#     else:
#         print("müsbət tək")
# else:
#     print("müsbət deyil")
#
#   a) müsbət deyil — bütün else-lər ən xarici if-ə aiddir
#   b) müsbət cüt — iç-içə if buraxılır, ona görə onun else hissəsi heç vaxt icra olunmur
#   c) müsbət tək — daxili else daxili if ilə eyni girintidədir, ona görə ona aiddir
#   d) Heç nə — iç-içə if üçün fiqurlu mötərizələr { } lazımdır
# ======================================================================

cavab_T4 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t4():
    assert _h(cavab_T4) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "seçilmiş cavab düzgün deyil"
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. 3 rəqəmli ədədin rəqəmlərinin cəmi (10 bal) — Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# 3 rəqəmli müsbət tam ədədin rəqəmlərinin cəmini hesablayan reqemler_cemi(n) funksiyasını yazın.
#
# Nümunə: reqemler_cemi(384) → 15  (3 + 8 + 4)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T5"):
    def reqemler_cemi(n):
        # kodunuzu bura yazın
        pass


def test_t5():
    return grade(
        (4, "reqemler_cemi(384) 15 olmalıdır", lambda: _same(_call(reqemler_cemi, 384), 15)),
        (2, "reqemler_cemi(999) 27 olmalıdır", lambda: _same(_call(reqemler_cemi, 999), 27)),
        (2, "reqemler_cemi(105) 6 olmalıdır (ortada 0 rəqəmi)", lambda: _same(_call(reqemler_cemi, 105), 6)),
        (2, "reqemler_cemi(100) 1 olmalıdır", lambda: _same(_call(reqemler_cemi, 100), 1)),
    )
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Ədədin bölənləri və onların sayı (10 bal) — Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While)
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Tam ədədin bütün bölənlərini və bölənlərinin sayını tapan bolenler(n) funksiyasını yazın.
# Funksiya iki qiymət qaytarsın: bolenler_siyahisi, say.
#
# Nümunə: bolenler(12) → ([1, 2, 3, 4, 6, 12], 6)  (Bölənlər: 1, 2, 3, 4, 6, 12 (Sayı: 6))
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T6"):
    def bolenler(n):
        # kodunuzu bura yazın
        pass


def test_t6():
    cases = {12: [1, 2, 3, 4, 6, 12], 7: [1, 7], 36: [1, 2, 3, 4, 6, 9, 12, 18, 36]}
    got = {n: _flat(_call(bolenler, n)) for n in cases}
    return grade(
        (6, "bölənlərin siyahısı", lambda: all(got[n][:len(d)] == d for n, d in cases.items())),
        (4, "bölənlərin sayı", lambda: all(len(got[n]) == len(d) + 1 and got[n][-1] == len(d) for n, d in cases.items())),
    )
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. Yüksək və aşağı səviyyəli dillər; kompilyator və interpretator (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Yüksək və aşağı səviyyəli dillər, kompilyator və interpretator haqqında hansı ifadə düzgündür və Python-u düzgün təsnif edir?
#   a) Yüksək səviyyəli dillər insan dilinə yaxın və daşınandır, aşağı səviyyəli dillər (maşın kodu, assembler) avadanlığa yaxındır; kompilyator proqramı icradan əvvəl bütövlükdə tərcümə edir, interpretator isə əmr-əmr icra edir — Python yüksək səviyyəli, interpretasiya olunan dildir
#   b) Python aşağı səviyyəli dildir, çünki prosessorun registrləri ilə birbaşa işləyir və hər icradan əvvəl .exe faylına kompilyasiya olunur
#   c) Kompilyator proqramı sətir-sətir icra edir, interpretator isə əvvəlcə bütün proqramı maşın koduna çevirib .exe fayl yaradır
#   d) Yüksək səviyyəli dillər həmişə maşın kodundan sürətli işləyir, çünki heç bir tərcüməyə ehtiyac duymur
# ======================================================================

cavab_T7 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t7():
    assert _h(cavab_T7) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Baş diaqonalın cəmi (10 bal) — Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# N × N ölçülü kvadrat matrisin baş diaqonalında yerləşən elementlərin cəmini hesablayan bas_diaqonal_cemi(matris)
# funksiyasını yazın.
#
# Nümunə: bas_diaqonal_cemi([[1, 2], [3, 4]]) → 5  (1 + 4)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T8"):
    def bas_diaqonal_cemi(matris):
        # kodunuzu bura yazın
        pass


def test_t8():
    assert _same(_call(bas_diaqonal_cemi, [[1, 2], [3, 4]]), 5), "[[1, 2], [3, 4]] üçün cavab 5 olmalıdır"
    assert _same(_call(bas_diaqonal_cemi, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]), 15), "3 × 3 matris üçün cavab 15 olmalıdır (1 + 5 + 9)"
    assert _same(_call(bas_diaqonal_cemi, [[-2]]), -2), "[[-2]] üçün cavab -2 olmalıdır"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Sətirlərin dəyişməzliyi və sətir metodları (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod icra olunanda nə baş verir?
# python
# s = "salam"
# s[0] = "S"
#
#   a) TypeError yaranır — sətirlər dəyişməzdir (immutable); yeni sətir yaratmaq lazımdır, məsələn s = "S" + s[1:] və ya s = s.capitalize()
#   b) s dəyişəni "S" olur, çünki bütün sətir yeni simvolla əvəz edilir
#   c) s dəyişəni "Salam" olur, çünki sətirlər siyahılar kimi dəyişdirilə bilər
#   d) Heç nə baş vermir — Python bu əmri səssizcə buraxır
# ======================================================================

cavab_T9 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t9():
    assert _h(cavab_T9) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. 3 rəqəmli polindrom ədəd (10 bal) — Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# 3 rəqəmli ədədin polindrom (soldan sağa və sağdan sola eyni oxunan) olub-olmadığını yoxlayan polindrom_eded(n)
# funksiyasını yazın. Funksiya True / False qaytarsın (və ya "Polindromdur" / "Polindrom deyil" çap etsin).
#
# Nümunə: polindrom_eded(121) → True, polindrom_eded(123) → False
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T10"):
    def polindrom_eded(n):
        # kodunuzu bura yazın
        pass


def test_t10():
    assert _same(_call(polindrom_eded, 121), True), "121 polindromdur"
    assert _same(_call(polindrom_eded, 123), False), "123 polindrom deyil"
    assert _same(_call(polindrom_eded, 707), True), "707 polindromdur"
    assert _same(_call(polindrom_eded, 100), False), "100 polindrom deyil"
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
