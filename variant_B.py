# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Proqramlaşdırmanın əsasları — 1-ci kurs, qrup 136a1 — SDF 1 (Variant B)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
   Funksiya nəticəni qaytara (`return`) və ya ekrana çıxara (`print`) bilər — hər ikisi qəbul olunur.
3. Faylı işə salın:   python variant_B.py
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
# Tapşırıq T1. İki nöqtə arasındakı məsafə (10 bal) — Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# Müstəvidə (x1, y1) və (x2, y2) nöqtələri arasındakı məsafəni hesablayan mesafe(x1, y1, x2, y2) funksiyasını yazın:
#
# d = √((x2 − x1)² + (y2 − y1)²)
#
# Nümunə: mesafe(0, 0, 3, 4) → 5.0
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T1"):
    def mesafe(x1, y1, x2, y2):
        # kodunuzu bura yazın
        pass


def test_t1():
    assert _same(_call(mesafe, 0, 0, 3, 4), 5.0), "mesafe(0, 0, 3, 4) 5.0 olmalıdır"
    assert _same(_call(mesafe, -1, 2, 5, -6), 10.0), "mesafe(-1, 2, 5, -6) 10.0 olmalıdır"
    assert _same(_call(mesafe, 0, 0, 1, 1), 1.41421356), "mesafe(0, 0, 1, 1) təxminən 1.414 olmalıdır"
    assert _same(_call(mesafe, 2, 3, 2, 3), 0), "eyni nöqtələr arasındakı məsafə 0 olmalıdır"
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Sait və samit hərflərin sayı (10 bal) — Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Mətndəki sait və samit hərflərin sayını ayrı-ayrılıqda hesablayan sait_samit(metn) funksiyasını yazın.
# Saitlər: a, ı, o, u, e, ə, i, ö, ü (böyük hərflər də). Hərf olmayan simvollar (boşluq, rəqəm, işarə) sayılmır.
# Funksiya iki qiymət qaytarsın: sait_sayi, samit_sayi.
#
# Nümunə: sait_samit("Salam Baku") → (4, 5)  (Sait sayı: 4, Samit sayı: 5)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T2"):
    def sait_samit(metn):
        # kodunuzu bura yazın
        pass


def test_t2():
    cases = [("Salam Baku", (4, 5)), ("Ölkə 2026!", (2, 2)), ("Python", (1, 5)), ("Azərbaycan", (4, 6))]
    res = [_seq(_call(sait_samit, s), 2) for s, _ in cases]
    return grade(
        (5, "sait hərflərin sayı (ə, ö, ü, ı da saitdir)", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
        (5, "samit hərflərin sayı (boşluq, rəqəm və işarələr sayılmır)", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
    )
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. if-if və if-elif icra fərqi (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# x = 15
# if x > 10:
#     print("A")
# if x > 5:
#     print("B")
# elif x > 0:
#     print("C")
# else:
#     print("D")
#
#   a) Yalnız B — sonuncu doğru şərt əvvəlkiləri ləğv edir
#   b) Yalnız A — ilk doğru şərtdən sonra qalan bütün if-lər buraxılır
#   c) A, B və C — if-elif zəncirində doğru olan bütün bloklar icra olunur
#   d) A və B (iki sətirdə) — ayrı-ayrı if-lər müstəqil yoxlanılır, if-elif-else zəncirində isə yalnız ilk doğru blok icra olunur
# ======================================================================

cavab_T3 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t3():
    assert _h(cavab_T3) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "seçilmiş cavab düzgün deyil"
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. 0 daxil edilənə qədər cəm və ədədi orta (10 bal) — Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While)
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Ədədlər siyahı şəklində verilir; istifadəçi 0 daxil edənə qədər olan ədədlərin cəmini və ədədi ortasını hesablayan
# cem_orta(ededler) funksiyasını yazın (0 və ondan sonrakı ədədlər nəzərə alınmır). Funksiya iki qiymət qaytarsın: cem, orta.
#
# Nümunə: cem_orta([5, 10, 15, 0]) → (30, 10.0)  (Cəm: 30, Ədədi orta: 10.0)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T4"):
    def cem_orta(ededler):
        # kodunuzu bura yazın
        pass


def test_t4():
    cases = [([5, 10, 15, 0], (30, 10.0)), ([4, 0], (4, 4.0)), ([2, 3, 0, 100, 200], (5, 2.5)), ([-6, 12, 3, 0], (9, 3.0))]
    res = [_seq(_call(cem_orta, lst), 2) for lst, _ in cases]
    return grade(
        (5, "cəm (0-a qədər)", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
        (5, "ədədi orta (0-a qədər)", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
    )
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Əsas məlumat tipləri, type() və tip çevrilməsi (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# x = "7"
# y = int(x) + 3
# print(type(x), y, float(y))
#
#   a) <class 'str'> 73 73.0
#   b) <class 'int'> 10 10.0
#   c) <class 'str'> 10 10.0
#   d) <class 'str'> 10 10
# ======================================================================

cavab_T5 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t5():
    assert _h(cavab_T5) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "seçilmiş cavab düzgün deyil"
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Nöqtənin koordinat rübü (10 bal) — Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# (x, y) nöqtəsinin hansı koordinat rübündə (I, II, III, IV rüb) və ya oxlar üzərində olduğunu təyin edən
# rub(x, y) funksiyasını yazın. Mümkün cavablar: "I rüb", "II rüb", "III rüb", "IV rüb", "OX oxu", "OY oxu",
# "Koordinat başlanğıcı". ("II", 2 və ya "2-ci rüb" kimi cavablar da qəbul olunur.)
#
# Nümunə: rub(-3, 5) → "II rüb"
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T6"):
    def rub(x, y):
        # kodunuzu bura yazın
        pass


def test_t6():
    import re
    def where(x, y):
        t = str(_call(rub, x, y)).casefold().replace("-", " ").replace("_", " ")
        if any(w in t for w in ("başlanğıc", "baslangic", "mərkəz", "merkez", "origin", "(0, 0)")):
            return "O"
        if "ox" in t or "oy" in t or "axis" in t or "oxu" in t or "ox " in t:
            if re.search(r"\box\b|\bx\b|abs", t):
                return "X"
            if re.search(r"\boy\b|\by\b|ord", t):
                return "Y"
        t = t.replace("rüb", " ").replace("rub", " ").replace("quadrant", " ")
        for word, q in (("iv", 4), ("iii", 3), ("ii", 2), ("i", 1)):
            if re.search(r"\b" + word + r"\b", t):
                return q
        ns = _nums(t)
        return ns[0] if ns else None
    return grade(
        (2, "rub(4, 7) I rüb olmalıdır", lambda: where(4, 7) == 1),
        (2, "rub(-3, 5) II rüb olmalıdır", lambda: where(-3, 5) == 2),
        (2, "rub(-2, -9) III rüb olmalıdır", lambda: where(-2, -9) == 3),
        (2, "rub(6, -1) IV rüb olmalıdır", lambda: where(6, -1) == 4),
        (2, "oxlar və başlanğıc: (5, 0) OX oxu, (0, -3) OY oxu, (0, 0) Koordinat başlanğıcı",
         lambda: where(5, 0) == "X" and where(0, -3) == "Y" and where(0, 0) == "O"),
    )
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. for və while dövrləri, sonsuz dövr (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Python-da for və while dövrləri haqqında hansı ifadə düzgündür?
#   a) Python-da sonsuz dövr mümkün deyil, çünki interpretator hər dövrü 1000 təkrardan sonra dayandırır
#   b) Siyahı üzərində for dövrü siyahıda 1000-dən çox element olduqda sonsuz dövrə çevrilir
#   c) for ardıcıllığın (iterable) elementlərini gəzir, while isə şərt True olduqca təkrarlanır; şərt heç vaxt False olmursa (məsələn, dövr dəyişəni dövrün içində dəyişdirilmir), while sonsuz dövrə çevrilir
#   d) while dövrü həmişə əvvəlcədən məlum olan sabit sayda təkrarlanmalıdır
# ======================================================================

cavab_T7 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t7():
    assert _h(cavab_T7) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "seçilmiş cavab düzgün deyil"
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Matrisin transponirə edilməsi (10 bal) — Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# N × M ölçülü matrisin transponirə edilmiş (M × N) matrisini quran transpoze(matris) funksiyasını yazın
# (sətirlər sütunlara çevrilir).
#
# Nümunə: transpoze([[1, 2], [3, 4], [5, 6]]) → [[1, 3, 5], [2, 4, 6]]
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T8"):
    def transpoze(matris):
        # kodunuzu bura yazın
        pass


def test_t8():
    return grade(
        (5, "transpoze([[1, 2], [3, 4], [5, 6]]) [[1, 3, 5], [2, 4, 6]] olmalıdır",
         lambda: _same(_call(transpoze, [[1, 2], [3, 4], [5, 6]]), [[1, 3, 5], [2, 4, 6]])),
        (3, "kvadrat matris: [[1, 2], [3, 4]] -> [[1, 3], [2, 4]]", lambda: _same(_call(transpoze, [[1, 2], [3, 4]]), [[1, 3], [2, 4]])),
        (2, "bir sətir: [[7, 8, 9]] -> [[7], [8], [9]]", lambda: _same(_call(transpoze, [[7, 8, 9]]), [[7], [8], [9]])),
    )
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Hərflərin registrini dəyişmək (10 bal) — Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Mətndəki bütün kiçik hərfləri böyük, böyük hərfləri isə kiçik hərflərə çevirən registr_deyis(metn) funksiyasını yazın
# (swapcase() metodundan istifadə etmədən; digər simvollar dəyişmir).
#
# Nümunə: registr_deyis("PyThOn") → "pYtHoN"
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T9"):
    def registr_deyis(metn):
        # kodunuzu bura yazın
        pass


def test_t9():
    return grade(
        (5, 'registr_deyis("PyThOn") "pYtHoN" olmalıdır', lambda: _same(_call(registr_deyis, "PyThOn"), "pYtHoN")),
        (3, 'boşluq və rəqəmlər qalır: registr_deyis("Hello World 2026") "hELLO wORLD 2026" olmalıdır',
         lambda: _same(_call(registr_deyis, "Hello World 2026"), "hELLO wORLD 2026")),
        (2, 'registr_deyis("abc") "ABC" olmalıdır', lambda: _same(_call(registr_deyis, "abc"), "ABC")),
    )
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. Məntiqi və müqayisə operatorları (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# a = 5 və b = 10 olduqda aşağıdakı ifadənin qiyməti nədir?
# python
# not (a > 3 and b < 10) or a == b
#
#   a) 5
#   b) True
#   c) False
#   d) Xəta, çünki not mötərizədən əvvəl yazıla bilməz
# ======================================================================

cavab_T10 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t10():
    assert _h(cavab_T10) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "seçilmiş cavab düzgün deyil"
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
