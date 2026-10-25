# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Proqramlaşdırmanın əsasları — 1-ci kurs, qrup 136a1 — SDF 1 (Variant A)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
   Funksiya nəticəni qaytara (`return`) və ya ekrana çıxara (`print`) bilər — hər ikisi qəbul olunur.
3. Faylı işə salın:   python variant_A.py
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
# Tapşırıq T1. pass operatoru (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Şərt bloklarında pass operatorunun təyinatı nədir?
#   a) Dövrün cari təkrarının qalan hissəsini buraxır, continue kimi
#   b) Bütün proqramı dərhal dayandırır
#   c) Heç nə etməyən yer tutucudur: if / else / def sonrakı blok boş ola bilməz, pass onu sintaksis xətası olmadan boş saxlamağa imkan verir
#   d) Funksiyadan çıxıb dəyər qaytarır, return kimi
# ======================================================================

cavab_T1 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t1():
    assert _h(cavab_T1) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "seçilmiş cavab düzgün deyil"
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Selsidən Farenheytə çevirmə (10 bal) — Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# Temperaturu Selsidən (Celsius) Farenheytə (Fahrenheit) çevirən selsi_farenheyt(c) funksiyasını yazın: F = C · 1.8 + 32.
#
# Nümunə: selsi_farenheyt(25) → 77.0
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T2"):
    def selsi_farenheyt(c):
        # kodunuzu bura yazın
        pass


def test_t2():
    assert _same(_call(selsi_farenheyt, 25), 77.0), "selsi_farenheyt(25) 77.0 olmalıdır"
    assert _same(_call(selsi_farenheyt, 0), 32.0), "selsi_farenheyt(0) 32.0 olmalıdır"
    assert _same(_call(selsi_farenheyt, -40), -40.0), "selsi_farenheyt(-40) -40.0 olmalıdır"
    assert _same(_call(selsi_farenheyt, 36.6), 97.88), "selsi_farenheyt(36.6) 97.88 olmalıdır"
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. İkiölçülü massivlər (matrislər) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# m = [[1, 2, 3], [4, 5, 6]] matrisi üçün hansı ifadə düzgündür?
#   a) Matrisi yalnız bir dövrlə gəzmək olar; iç-içə dövr TypeError verir
#   b) m[2][1] 6-ya bərabərdir; xarici dövr sütunları, daxili dövr sətirləri gəzir
#   c) m[1][2] 5-ə bərabərdir, çünki indekslər 1-dən başlayır
#   d) m[1][2] 6-ya bərabərdir; iç-içə dövrdə xarici dövr sətirləri (for row in m), daxili dövr həmin sətrin elementlərini (for x in row) gəzir
# ======================================================================

cavab_T3 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t3():
    assert _h(cavab_T3) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "seçilmiş cavab düzgün deyil"
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Düzbucaqlının sahəsi və perimetri (10 bal) — Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Düzbucaqlının eni və uzunluğuna görə onun sahəsini və perimetrini hesablayan duzbucaqli(en, uzunluq) funksiyasını yazın.
# Funksiya iki qiymət qaytarsın: sahe, perimetr.
#
# Nümunə: duzbucaqli(5, 10) → (50, 30)  (Sahə: 50, Perimetr: 30)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T4"):
    def duzbucaqli(en, uzunluq):
        # kodunuzu bura yazın
        pass


def test_t4():
    cases = [((5, 10), (50, 30)), ((3, 3), (9, 12)), ((2.5, 4), (10.0, 13.0))]
    res = [_seq(_call(duzbucaqli, *a), 2) for a, _ in cases]
    return grade(
        (5, "sahə (en × uzunluq)", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
        (5, "perimetr (2 × (en + uzunluq))", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
    )
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. X ədədinin təkrar sayı və ilk indeksi (10 bal) — Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# Siyahıda verilmiş X ədədinin neçə dəfə təkrarlandığını və ilk rast gəlindiyi indeksi tapan tekrar_ve_indeks(lst, x)
# funksiyasını yazın. Funksiya iki qiymət qaytarsın: say, ilk_indeks.
#
# Nümunə: tekrar_ve_indeks([5, 3, 5, 2, 5, 8], 5) → (3, 0)  (Təkrar sayı: 3, İlk indeks: 0)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T5"):
    def tekrar_ve_indeks(lst, x):
        # kodunuzu bura yazın
        pass


def test_t5():
    cases = [(([5, 3, 5, 2, 5, 8], 5), (3, 0)), (([1, 2, 3, 2, 2], 2), (3, 1)), (([4, 6, 9], 9), (1, 2))]
    res = [_seq(_call(tekrar_ve_indeks, *a), 2) for a, _ in cases]
    return grade(
        (5, "təkrar sayı", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
        (5, "ilk indeks", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
    )
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Stack və Heap yaddaş sahələri (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Python-un yaddaş modelində Stack və Heap sahələrinin rolu haqqında hansı ifadə düzgündür?
#   a) Python-da Heap yaddaşını proqramçı free() funksiyası ilə əl ilə boşaltmalıdır, əks halda proqram dayanır
#   b) Heap yalnız qlobal dəyişənlər, Stack isə yalnız sətirlər (str) üçün istifadə olunur
#   c) Stack funksiya çağırışlarının çərçivələrini və lokal adları (istinadları) saxlayır və funksiya bitəndə avtomatik boşalır; Heap obyektlərin özlərini (int, str, list …) saxlayır və onlara istinad qalmayanda istinad sayğacı / zibil toplayıcı (garbage collector) onları silir
#   d) Bütün obyektlər, o cümlədən siyahılar, Stack-də saxlanılır və hər mənimsətmədə yeni dəyişənə tam surəti çıxarılır
# ======================================================================

cavab_T6 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t6():
    assert _h(cavab_T6) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "seçilmiş cavab düzgün deyil"
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. ƏBOB və ƏKOB (10 bal) — Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While)
# qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)
#
# İki natural ədədin ƏBOB-unu (ən böyük ortaq bölən) və ƏKOB-unu (ən kiçik ortaq bölünən) hesablayan
# ebob_ekob(a, b) funksiyasını yazın. Funksiya iki qiymət qaytarsın: ebob, ekob.
#
# Nümunə: ebob_ekob(12, 18) → (6, 36)
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T7"):
    def ebob_ekob(a, b):
        # kodunuzu bura yazın
        pass


def test_t7():
    cases = [((12, 18), (6, 36)), ((7, 13), (1, 91)), ((20, 5), (5, 20)), ((21, 6), (3, 42))]
    res = [_seq(_call(ebob_ekob, *a), 2) for a, _ in cases]
    return grade(
        (5, "ƏBOB", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
        (5, "ƏKOB", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
    )
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. İndeksləmə, mənfi indekslər və dilimləmə (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bu kod ekrana nə çıxarır?
# python
# lst = [10, 20, 30, 40, 50]
# print(lst[-2], lst[1:4], lst[::2])
#
#   a) 40 [20, 30, 40] [20, 40]
#   b) 40 [20, 30, 40] [10, 30, 50]
#   c) 30 [20, 30, 40] [10, 30, 50]
#   d) 40 [20, 30, 40, 50] [10, 30, 50]
# ======================================================================

cavab_T8 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t8():
    assert _h(cavab_T8) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "seçilmiş cavab düzgün deyil"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Həm 3-ə, həm də 5-ə bölünmə (10 bal) — Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# Ədədin həm 3-ə, həm də 5-ə qalıqsız bölünüb-bölünmədiyini şərt operatoru ilə yoxlayan uc_ve_bese_bolunur(n)
# funksiyasını yazın. Funksiya True / False qaytarsın (və ya "Ədəd həm 3-ə, həm də 5-ə bölünür" / "Bölünmür" çap etsin).
#
# Nümunə: uc_ve_bese_bolunur(15) → True
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T9"):
    def uc_ve_bese_bolunur(n):
        # kodunuzu bura yazın
        pass


def test_t9():
    assert _same(_call(uc_ve_bese_bolunur, 15), True), "15 həm 3-ə, həm də 5-ə bölünür"
    assert _same(_call(uc_ve_bese_bolunur, 45), True), "45 həm 3-ə, həm də 5-ə bölünür"
    assert _same(_call(uc_ve_bese_bolunur, 9), False), "9 yalnız 3-ə bölünür"
    assert _same(_call(uc_ve_bese_bolunur, 10), False), "10 yalnız 5-ə bölünür"
    assert _same(_call(uc_ve_bese_bolunur, 7), False), "7 heç birinə bölünmür"
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. Rekursiv faktorial (10 bal) — Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar
# qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
#
# Ədədin faktorialını hesablayan rekursiv funksiya factorial_recursive(n) yazın (funksiya özünü çağırır; 0! = 1).
#
# Nümunə: factorial_recursive(5) → 120
#
# Nəticəni funksiyadan qaytarın (return); ekrana çıxarmaq (print) da qəbul olunur. input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.
# ======================================================================

with hell("T10"):
    def factorial_recursive(n):
        # kodunuzu bura yazın
        pass


def test_t10():
    assert _same(_call(factorial_recursive, 5), 120), "factorial_recursive(5) 120 olmalıdır"
    assert _same(_call(factorial_recursive, 1), 1), "factorial_recursive(1) 1 olmalıdır"
    assert _same(_call(factorial_recursive, 0), 1), "factorial_recursive(0) 1 olmalıdır"
    assert _same(_call(factorial_recursive, 10), 3628800), "factorial_recursive(10) 3628800 olmalıdır"
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
