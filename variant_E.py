# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Proqramlaşdırmanın əsasları — 1-ci kurs, qrup 136a1 — SDF 1 (Variant E)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
   Funksiya nəticəni qaytara (`return`) və ya ekrana çıxara (`print`) bilər — hər ikisi qəbul olunur.
3. Faylı işə salın:   python variant_E.py
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
# Tapşırıq T1. Saniyəni saat, dəqiqə və saniyəyə çevirmək (10 bal) — Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Verilmiş saniyə miqdarını saat, dəqiqə və saniyəyə çevirən saniye_cevir(saniye) funksiyasını yazın.
# Funksiya üç qiymət qaytarsın: saat, deqiqe, saniye.
#
# Nümunə: saniye_cevir(3665) → (1, 1, 5)  (1 saat, 1 dəqiqə, 5 saniyə)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T1"):
    def saniye_cevir(saniye):
        # kodunuzu bura yazın
        pass


def test_t1():
    return grade(
        (4, "saniye_cevir(3665) (1, 1, 5) olmalıdır", lambda: _same(_call(saniye_cevir, 3665), (1, 1, 5))),
        (2, "saniye_cevir(59) (0, 0, 59) olmalıdır", lambda: _same(_call(saniye_cevir, 59), (0, 0, 59))),
        (2, "saniye_cevir(7200) (2, 0, 0) olmalıdır", lambda: _same(_call(saniye_cevir, 7200), (2, 0, 0))),
        (2, "saniye_cevir(86399) (23, 59, 59) olmalıdır", lambda: _same(_call(saniye_cevir, 86399), (23, 59, 59))),
    )
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Cüt ədədləri süzgəcdən keçirmək: get_evens(lst) (10 bal) — Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Siyahıdakı cüt ədədləri süzgəcdən keçirib yeni siyahı qaytaran get_evens(lst) funksiyasını yazın.
#
# Nümunə: get_evens([1, 2, 3, 4, 5, 6, 7, 8]) → [2, 4, 6, 8]
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T2"):
    def get_evens(lst):
        # kodunuzu bura yazın
        pass


def test_t2():
    return grade(
        (5, "get_evens([1, 2, 3, 4, 5, 6, 7, 8]) [2, 4, 6, 8] olmalıdır",
         lambda: _same(_call(get_evens, [1, 2, 3, 4, 5, 6, 7, 8]), [2, 4, 6, 8])),
        (3, "mənfi ədədlər və sıfır: get_evens([-4, 0, 7, 10]) [-4, 0, 10] olmalıdır",
         lambda: _same(_call(get_evens, [-4, 0, 7, 10]), [-4, 0, 10])),
        (2, "cüt ədəd yoxdursa: get_evens([1, 3, 5]) [] olmalıdır", lambda: _same(_call(get_evens, [1, 3, 5]), [])),
    )
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. Riyazi operatorlar və icra prioriteti (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Aşağıdakı ifadənin qiyməti nəyə bərabərdir?
# python
# 2 + 3  4  2 // 5 % 4
#
#   a) 3
#   b) 11
#   c) 0
#   d) 9.6
# ======================================================================

cavab_T3 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t3():
    assert _h(cavab_T3) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Matrisin hər sətrinin cəmi (10 bal) — Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# N × M ölçülü matrisin (siyahılar siyahısı) hər sətrinin elementlərinin cəmini ayrıca hesablayıb siyahı kimi qaytaran
# setir_cemleri(matris) funksiyasını yazın.
#
# Nümunə: setir_cemleri([[1, 2, 3], [4, 5, 6]]) → [6, 15]  (Sətir 1 cəmi: 6, Sətir 2 cəmi: 15)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T4"):
    def setir_cemleri(matris):
        # kodunuzu bura yazın
        pass


def test_t4():
    return grade(
        (5, "setir_cemleri([[1, 2, 3], [4, 5, 6]]) [6, 15] olmalıdır", lambda: _same(_call(setir_cemleri, [[1, 2, 3], [4, 5, 6]]), [6, 15])),
        (3, "3 sətirli matris: [[1, 1], [2, 2], [-3, 10]] -> [2, 4, 7]",
         lambda: _same(_call(setir_cemleri, [[1, 1], [2, 2], [-3, 10]]), [2, 4, 7])),
        (2, "bir sətirli matris: [[5, 5, 5, 5]] -> [20]", lambda: _same(_call(setir_cemleri, [[5, 5, 5, 5]]), [20])),
    )
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Qısa qapanma qiymətləndirməsi (Short-Circuit) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# x = 0. Python aşağıdakı şərti qiymətləndirəndə nə baş verir?
# python
# if x != 0 and 10 / x > 1:
#     print("böyük")
#
#   a) Şərt False olur və xəta yaranmır: and ilk yalan operandda dayanır, ona görə 10 / x ümumiyyətlə hesablanmır
#   b) ZeroDivisionError yaranır, çünki Python and-in hər iki tərəfini həmişə hesablayır
#   c) Şərt True olur, çünki 10 / 0 sonsuzluq kimi qəbul edilir
#   d) Python əvvəlcə sağ operandı hesablayır, ona görə nəticə yalnız 10 / x > 1-dən asılıdır
# ======================================================================

cavab_T5 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t5():
    assert _h(cavab_T5) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "seçilmiş cavab düzgün deyil"
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. 7-yə bölündükdə qalığı 3 olan ədədlərin cəmi (10 bal) — Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While)
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# 1-dən N-ə qədər (N daxil) olan ədədlər arasında 7-yə bölündükdə qalıqda 3 alınan ədədlərin cəmini hesablayan
# qaliq_cemi(n) funksiyasını yazın.
#
# Nümunə: qaliq_cemi(100) → 679  (3 + 10 + 17 + … + 94)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T6"):
    def qaliq_cemi(n):
        # kodunuzu bura yazın
        pass


def test_t6():
    return grade(
        (5, "qaliq_cemi(100) 679 olmalıdır", lambda: _same(_call(qaliq_cemi, 100), 679)),
        (3, "qaliq_cemi(20) 30 olmalıdır (3 + 10 + 17)", lambda: _same(_call(qaliq_cemi, 20), 30)),
        (2, "N özü də daxildir: qaliq_cemi(10) 13 olmalıdır (3 + 10)", lambda: _same(_call(qaliq_cemi, 10), 13)),
    )
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. Tək ədədləri 0 ilə əvəz etmək (10 bal) — Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# Siyahıdakı bütün tək ədədləri 0 ilə əvəz edən tekleri_sifirla(lst) funksiyasını yazın.
#
# Nümunə: tekleri_sifirla([1, 2, 3, 4, 5, 6]) → [0, 2, 0, 4, 0, 6]
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T7"):
    def tekleri_sifirla(lst):
        # kodunuzu bura yazın
        pass


def test_t7():
    assert _same(_call(tekleri_sifirla, [1, 2, 3, 4, 5, 6]), [0, 2, 0, 4, 0, 6]), "[1, 2, 3, 4, 5, 6] -> [0, 2, 0, 4, 0, 6] olmalıdır"
    assert _same(_call(tekleri_sifirla, [-3, -2, 7]), [0, -2, 0]), "mənfi tək ədədlər də: [-3, -2, 7] -> [0, -2, 0] olmalıdır"
    assert _same(_call(tekleri_sifirla, [2, 4, 8]), [2, 4, 8]), "tək ədəd yoxdursa siyahı dəyişməməlidir"
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Funksiyalar, return və lokal / qlobal dəyişənlər (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# x = 10
# def f():
#     x = 5
#     return x  2
# y = f()
# print(x, y)
#
#   a) 10 20 — funksiya qlobal x-dən istifadə edir
#   b) Xəta — global açar sözü olmadan funksiyada x adlı dəyişən yaratmaq olmaz
#   c) 10 10 — funksiyanın içindəki x lokal dəyişəndir və qlobal x-i dəyişmir; return 5 * 2 = 10 qaytarır
#   d) 5 10 — funksiyadakı mənimsətmə qlobal x-i dəyişir
# ======================================================================

cavab_T8 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t8():
    assert _h(cavab_T8) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "seçilmiş cavab düzgün deyil"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Üçbucaq əmələ gəlirmi? (10 bal) — Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Üç tərəfin uzunluğuna (a, b, c) görə üçbucaq əmələ gəlib-gəlmədiyini yoxlayan ucbucaqdir(a, b, c) funksiyasını yazın.
# Üçbucaq bərabərsizliyi: a + b > c, a + c > b, b + c > a.
# Funksiya True / False qaytarsın (və ya "Üçbucaq əmələ gətirir" / "Üçbucaq əmələ gətirmir" çap etsin).
#
# Nümunə: ucbucaqdir(3, 4, 5) → True
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T9"):
    def ucbucaqdir(a, b, c):
        # kodunuzu bura yazın
        pass


def test_t9():
    return grade(
        (3, "ucbucaqdir(3, 4, 5) True olmalıdır", lambda: _same(_call(ucbucaqdir, 3, 4, 5), True)),
        (2, "ucbucaqdir(7, 10, 5) True olmalıdır", lambda: _same(_call(ucbucaqdir, 7, 10, 5), True)),
        (2, "ucbucaqdir(1, 2, 3) False olmalıdır (a + b = c kifayət deyil)", lambda: _same(_call(ucbucaqdir, 1, 2, 3), False)),
        (3, "ucbucaqdir(10, 1, 2) və ucbucaqdir(1, 10, 2) False olmalıdır (hər tərəf yoxlanmalıdır)",
         lambda: _same(_call(ucbucaqdir, 10, 1, 2), False) and _same(_call(ucbucaqdir, 1, 10, 2), False)),
    )
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. Şərt operatorunun üçlü forması (Ternary) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# parity dəyişəninə "cüt" və ya "tək" yazan düzgün üçlü (ternary) şərt ifadəsi hansıdır?
#   a) parity = "cüt" if n % 2 == 0
#   b) parity = if n % 2 == 0 "cüt" else "tək"
#   c) parity = n % 2 == 0 ? "cüt" : "tək"
#   d) parity = "cüt" if n % 2 == 0 else "tək"
# ======================================================================

cavab_T10 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t10():
    assert _h(cavab_T10) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "seçilmiş cavab düzgün deyil"
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
