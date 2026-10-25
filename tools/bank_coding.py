# -*- coding: utf-8 -*-
"""proqramlasdirmanin_esaslari_imtahan_suallari_v2.docx — 60 kod yazma tapşırığı (5 kateqoriya).

A: 8, B: 12, C: 13, D: 13, E: 14 tapşırıq. Hər variantda 6 kod tapşırığı var (5 kateqoriyanın hər birindən ən azı 1),
yəni 5 variantda 30 tapşırıq istifadə olunur, qalan 30 tapşırıq ehtiyatdır (təkrar imtahan üçün).

Hər tapşırıq funksiya yazmaq formasındadır ki, avtomatik yoxlanıla bilsin. Yoxlama nəticəyə əsaslanır və tolerantdır
(bax: grader_core.py): funksiya cavabı qaytara (return) və ya ekrana çıxara (print) bilər, cavabın əvvəlində izah ola bilər,
list / tuple və 5 / 5.0 eyni sayılır, istənilən düzgün alqoritm qəbul olunur.

partial=True  -> 0–10 bal arası (hər test halı / hissə öz balını qazandırır; çəkilərin cəmi 10-dur)
partial=False -> yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)
"""
import textwrap

CATEGORIES = {
    "A": "Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar",
    "B": "Şərt Operatorları və Budaqlanan Alqoritmlər",
    "C": "Dövr Operatorları və İterasiya (For, While)",
    "D": "Birölçülü və İkiölçülü Massivlər / Siyahılar",
    "E": "Mətn Sətirləri (Strings) və Funksiyalar",
}

# Məzmunca bir-birinə çox oxşayan tapşırıqlar eyni variantda olmasın
SIMILAR = [("C6", "E9"), ("C5", "E10"), ("C7", "E16"), ("C10", "E12"), ("A11", "C8"), ("B12", "E5"),
           ("C6", "C12"), ("B5", "D15"), ("C4", "E11"), ("D6", "E11"), ("B7", "D4"), ("C9", "E8"), ("A16", "C8")]

CODING = {}

FOOT = ("\n\n*Nəticəni funksiyadan qaytarın (`return`); ekrana çıxarmaq (`print`) da qəbul olunur. "
        "`input()` lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.*")


def task(tid, title, desc, starter, solution, test, partial=True):
    CODING[tid] = dict(id=tid, cat=tid[0], num=int(tid[1:]), title=title,
                       desc=textwrap.dedent(desc).strip() + FOOT,
                       starter=textwrap.dedent(starter).strip("\n"), solution=textwrap.dedent(solution).strip("\n"),
                       test=textwrap.dedent(test).strip("\n"), partial=partial)


def _starter(sig):
    return f"def {sig}:\n    # kodunuzu bura yazın\n    pass"


# =====================================================================
# Kateqoriya A: Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar
# =====================================================================
task("A9", "Düzbucaqlının sahəsi və perimetri",
 """
 Düzbucaqlının eni və uzunluğuna görə onun **sahəsini** və **perimetrini** hesablayan `duzbucaqli(en, uzunluq)` funksiyasını yazın.
 Funksiya iki qiymət qaytarsın: `sahe, perimetr`.

 Nümunə: `duzbucaqli(5, 10)` → `(50, 30)`  (Sahə: 50, Perimetr: 30)
 """,
 _starter("duzbucaqli(en, uzunluq)"),
 """
 def duzbucaqli(en, uzunluq):
     return en * uzunluq, 2 * (en + uzunluq)
 """,
 """
 cases = [((5, 10), (50, 30)), ((3, 3), (9, 12)), ((2.5, 4), (10.0, 13.0))]
 res = [_seq(_call(duzbucaqli, *a), 2) for a, _ in cases]
 return grade(
     (5, "sahə (en × uzunluq)", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "perimetr (2 × (en + uzunluq))", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("A10", "Dairənin sahəsi və çevrənin uzunluğu",
 """
 Radius `r` verilir. Dairənin sahəsini (S = π · r²) və çevrənin uzunluğunu (L = 2 · π · r) hesablayan `daire(r)` funksiyasını yazın
 (**π = 3.14** götürün). Funksiya iki qiymət qaytarsın: `sahe, uzunluq`.

 Nümunə: `daire(4)` → `(50.24, 25.12)`
 """,
 _starter("daire(r)"),
 """
 def daire(r):
     pi = 3.14
     return pi * r ** 2, 2 * pi * r
 """,
 """
 cases = [(4, (50.24, 25.12)), (1, (3.14, 6.28)), (10, (314.0, 62.8))]
 res = [_seq(_call(daire, r), 2) for r, _ in cases]
 return grade(
     (5, "sahə (π · r²)", lambda: all(x and _same(x[0], e[0]) for x, (_, e) in zip(res, cases))),
     (5, "çevrənin uzunluğu (2 · π · r)", lambda: all(x and _same(x[1], e[1]) for x, (_, e) in zip(res, cases))),
 )
 """)

task("A11", "3 rəqəmli ədədin rəqəmlərinin cəmi",
 """
 3 rəqəmli müsbət tam ədədin **rəqəmlərinin cəmini** hesablayan `reqemler_cemi(n)` funksiyasını yazın.

 Nümunə: `reqemler_cemi(384)` → `15`  (3 + 8 + 4)
 """,
 _starter("reqemler_cemi(n)"),
 """
 def reqemler_cemi(n):
     return n // 100 + n // 10 % 10 + n % 10
 """,
 """
 return grade(
     (4, "reqemler_cemi(384) 15 olmalıdır", lambda: _same(_call(reqemler_cemi, 384), 15)),
     (2, "reqemler_cemi(999) 27 olmalıdır", lambda: _same(_call(reqemler_cemi, 999), 27)),
     (2, "reqemler_cemi(105) 6 olmalıdır (ortada 0 rəqəmi)", lambda: _same(_call(reqemler_cemi, 105), 6)),
     (2, "reqemler_cemi(100) 1 olmalıdır", lambda: _same(_call(reqemler_cemi, 100), 1)),
 )
 """)

task("A12", "Saniyəni saat, dəqiqə və saniyəyə çevirmək",
 """
 Verilmiş saniyə miqdarını **saat, dəqiqə və saniyəyə** çevirən `saniye_cevir(saniye)` funksiyasını yazın.
 Funksiya üç qiymət qaytarsın: `saat, deqiqe, saniye`.

 Nümunə: `saniye_cevir(3665)` → `(1, 1, 5)`  (1 saat, 1 dəqiqə, 5 saniyə)
 """,
 _starter("saniye_cevir(saniye)"),
 """
 def saniye_cevir(saniye):
     return saniye // 3600, saniye % 3600 // 60, saniye % 60
 """,
 """
 return grade(
     (4, "saniye_cevir(3665) (1, 1, 5) olmalıdır", lambda: _same(_call(saniye_cevir, 3665), (1, 1, 5))),
     (2, "saniye_cevir(59) (0, 0, 59) olmalıdır", lambda: _same(_call(saniye_cevir, 59), (0, 0, 59))),
     (2, "saniye_cevir(7200) (2, 0, 0) olmalıdır", lambda: _same(_call(saniye_cevir, 7200), (2, 0, 0))),
     (2, "saniye_cevir(86399) (23, 59, 59) olmalıdır", lambda: _same(_call(saniye_cevir, 86399), (23, 59, 59))),
 )
 """)

task("A13", "İki dəyişənin qiymətlərinin yerini dəyişmək",
 """
 İki dəyişənin (`a` və `b`) qiymətlərini **üçüncü köməkçi dəyişəndən istifadə etmədən** (Pythonic swap) dəyişən
 `yer_deyis(a, b)` funksiyasını yazın. Funksiya yeni qiymətləri `a, b` ardıcıllığı ilə qaytarsın.

 Nümunə: `yer_deyis(5, 9)` → `(9, 5)`  (a = 9, b = 5)
 """,
 _starter("yer_deyis(a, b)"),
 """
 def yer_deyis(a, b):
     a, b = b, a
     return a, b
 """,
 """
 assert _same(_call(yer_deyis, 5, 9), (9, 5)), "yer_deyis(5, 9) (9, 5) olmalıdır"
 assert _same(_call(yer_deyis, -1, 7), (7, -1)), "yer_deyis(-1, 7) (7, -1) olmalıdır"
 assert _same(_call(yer_deyis, 4, 4), (4, 4)), "yer_deyis(4, 4) (4, 4) olmalıdır"
 """, partial=False)

task("A14", "İki nöqtə arasındakı məsafə",
 """
 Müstəvidə (x1, y1) və (x2, y2) nöqtələri arasındakı məsafəni hesablayan `mesafe(x1, y1, x2, y2)` funksiyasını yazın:

 d = √((x2 − x1)² + (y2 − y1)²)

 Nümunə: `mesafe(0, 0, 3, 4)` → `5.0`
 """,
 _starter("mesafe(x1, y1, x2, y2)"),
 """
 def mesafe(x1, y1, x2, y2):
     return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
 """,
 """
 assert _same(_call(mesafe, 0, 0, 3, 4), 5.0), "mesafe(0, 0, 3, 4) 5.0 olmalıdır"
 assert _same(_call(mesafe, -1, 2, 5, -6), 10.0), "mesafe(-1, 2, 5, -6) 10.0 olmalıdır"
 assert _same(_call(mesafe, 0, 0, 1, 1), 1.41421356), "mesafe(0, 0, 1, 1) təxminən 1.414 olmalıdır"
 assert _same(_call(mesafe, 2, 3, 2, 3), 0), "eyni nöqtələr arasındakı məsafə 0 olmalıdır"
 """, partial=False)

task("A15", "Selsidən Farenheytə çevirmə",
 """
 Temperaturu Selsidən (Celsius) Farenheytə (Fahrenheit) çevirən `selsi_farenheyt(c)` funksiyasını yazın: **F = C · 1.8 + 32**.

 Nümunə: `selsi_farenheyt(25)` → `77.0`
 """,
 _starter("selsi_farenheyt(c)"),
 """
 def selsi_farenheyt(c):
     return c * 1.8 + 32
 """,
 """
 assert _same(_call(selsi_farenheyt, 25), 77.0), "selsi_farenheyt(25) 77.0 olmalıdır"
 assert _same(_call(selsi_farenheyt, 0), 32.0), "selsi_farenheyt(0) 32.0 olmalıdır"
 assert _same(_call(selsi_farenheyt, -40), -40.0), "selsi_farenheyt(-40) -40.0 olmalıdır"
 assert _same(_call(selsi_farenheyt, 36.6), 97.88), "selsi_farenheyt(36.6) 97.88 olmalıdır"
 """, partial=False)

task("A16", "4 rəqəmli ədədin ilk və son rəqəmi",
 """
 4 rəqəmli müsbət tam ədədin **ilk rəqəmini**, **son rəqəmini** və onların **cəmini** tapan `ilk_son(n)` funksiyasını yazın.
 Funksiya üç qiymət qaytarsın: `ilk, son, cem`.

 Nümunə: `ilk_son(4579)` → `(4, 9, 13)`  (İlk rəqəm: 4, Son rəqəm: 9, Cəm: 13)
 """,
 _starter("ilk_son(n)"),
 """
 def ilk_son(n):
     ilk = n // 1000
     son = n % 10
     return ilk, son, ilk + son
 """,
 """
 cases = {4579: (4, 9, 13), 1000: (1, 0, 1), 9081: (9, 1, 10), 2222: (2, 2, 4)}
 res = {n: _seq(_call(ilk_son, n), 3) for n in cases}
 return grade(
     (3, "ilk rəqəm", lambda: all(res[n] and _same(res[n][0], e[0]) for n, e in cases.items())),
     (3, "son rəqəm", lambda: all(res[n] and _same(res[n][1], e[1]) for n, e in cases.items())),
     (4, "ilk və son rəqəmin cəmi", lambda: all(res[n] and _same(res[n][2], e[2]) for n, e in cases.items())),
 )
 """)

# =====================================================================
# Kateqoriya B: Şərt Operatorları və Budaqlanan Alqoritmlər
# =====================================================================
task("B5", "Cüt və ya tək ədəd",
 """
 Tam ədədin **cüt** və ya **tək** olduğunu müəyyən edən `cut_tek(n)` funksiyasını yazın.
 Funksiya `"Cüt"` və ya `"Tək"` qaytarsın (və ya `"Cüt ədəd"` / `"Tək ədəd"` çap etsin).

 Nümunə: `cut_tek(7)` → `"Tək"`
 """,
 _starter("cut_tek(n)"),
 """
 def cut_tek(n):
     if n % 2 == 0:
         return "Cüt"
     else:
         return "Tək"
 """,
 """
 def kind(n):
     r = _call(cut_tek, n)
     if _has_word(r, "cüt", "cut", "even"):
         return "cüt"
     if _has_word(r, "tək", "tek", "odd"):
         return "tək"
     return None
 return grade(
     (4, "cut_tek(7) Tək olmalıdır", lambda: kind(7) == "tək"),
     (3, "cut_tek(10) Cüt olmalıdır", lambda: kind(10) == "cüt"),
     (3, "0 və mənfi ədədlər: cut_tek(0) Cüt, cut_tek(-3) Tək olmalıdır", lambda: kind(0) == "cüt" and kind(-3) == "tək"),
 )
 """)

task("B6", "Müsbət, mənfi və ya sıfır",
 """
 Ədədin **müsbət**, **mənfi** və ya **sıfıra bərabər** olduğunu yoxlayan `isare(n)` funksiyasını yazın.
 Funksiya `"Müsbət"`, `"Mənfi"` və ya `"Sıfır"` qaytarsın (və ya məs. `"Mənfi ədəd"` çap etsin).

 Nümunə: `isare(-15)` → `"Mənfi"`
 """,
 _starter("isare(n)"),
 """
 def isare(n):
     if n > 0:
         return "Müsbət"
     elif n < 0:
         return "Mənfi"
     else:
         return "Sıfır"
 """,
 """
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
 """)

task("B7", "Üç ədədin ən böyüyü və ən kiçiyi",
 """
 3 müxtəlif tam ədəd arasından **ən böyüyünü** və **ən kiçiyini** tapan `en_boyuk_kicik(a, b, c)` funksiyasını yazın.
 Funksiya iki qiymət qaytarsın: `en_boyuk, en_kicik`.

 Nümunə: `en_boyuk_kicik(12, 45, 23)` → `(45, 12)`
 """,
 _starter("en_boyuk_kicik(a, b, c)"),
 """
 def en_boyuk_kicik(a, b, c):
     boyuk = a
     if b > boyuk:
         boyuk = b
     if c > boyuk:
         boyuk = c
     kicik = a
     if b < kicik:
         kicik = b
     if c < kicik:
         kicik = c
     return boyuk, kicik
 """,
 """
 cases = [((12, 45, 23), (45, 12)), ((7, 3, 9), (9, 3)), ((-3, -7, -1), (-1, -7)), ((5, 8, 1), (8, 1))]
 res = [_seq(_call(en_boyuk_kicik, *a), 2) for a, _ in cases]
 return grade(
     (5, "ən böyük ədəd", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "ən kiçik ədəd", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("B8", "Bala görə qiymət hərfi",
 """
 Tələbənin imtahan balına (0–100) görə **qiymət hərfini** qaytaran `qiymet_herfi(bal)` funksiyasını yazın:
 91–100: A, 81–90: B, 71–80: C, 61–70: D, 51–60: E, 0–50: F.

 Nümunə: `qiymet_herfi(85)` → `"B"`  (Qiymət: B)
 """,
 _starter("qiymet_herfi(bal)"),
 """
 def qiymet_herfi(bal):
     if bal >= 91:
         return "A"
     elif bal >= 81:
         return "B"
     elif bal >= 71:
         return "C"
     elif bal >= 61:
         return "D"
     elif bal >= 51:
         return "E"
     else:
         return "F"
 """,
 """
 return grade(
     (3, "qiymet_herfi(85) B, qiymet_herfi(95) A olmalıdır",
      lambda: _same(_call(qiymet_herfi, 85), "B") and _same(_call(qiymet_herfi, 95), "A")),
     (3, "qiymet_herfi(75) C, (65) D, (55) E olmalıdır",
      lambda: _same(_call(qiymet_herfi, 75), "C") and _same(_call(qiymet_herfi, 65), "D") and _same(_call(qiymet_herfi, 55), "E")),
     (2, "qiymet_herfi(30) F olmalıdır", lambda: _same(_call(qiymet_herfi, 30), "F")),
     (2, "sərhəd qiymətləri: 91 → A, 90 → B, 51 → E, 50 → F",
      lambda: all(_same(_call(qiymet_herfi, b), h) for b, h in ((91, "A"), (90, "B"), (51, "E"), (50, "F")))),
 )
 """)

task("B9", "Üçbucaq əmələ gəlirmi?",
 """
 Üç tərəfin uzunluğuna (a, b, c) görə **üçbucaq əmələ gəlib-gəlmədiyini** yoxlayan `ucbucaqdir(a, b, c)` funksiyasını yazın.
 Üçbucaq bərabərsizliyi: a + b > c, a + c > b, b + c > a.
 Funksiya `True` / `False` qaytarsın (və ya `"Üçbucaq əmələ gətirir"` / `"Üçbucaq əmələ gətirmir"` çap etsin).

 Nümunə: `ucbucaqdir(3, 4, 5)` → `True`
 """,
 _starter("ucbucaqdir(a, b, c)"),
 """
 def ucbucaqdir(a, b, c):
     return a + b > c and a + c > b and b + c > a
 """,
 """
 return grade(
     (3, "ucbucaqdir(3, 4, 5) True olmalıdır", lambda: _same(_call(ucbucaqdir, 3, 4, 5), True)),
     (2, "ucbucaqdir(7, 10, 5) True olmalıdır", lambda: _same(_call(ucbucaqdir, 7, 10, 5), True)),
     (2, "ucbucaqdir(1, 2, 3) False olmalıdır (a + b = c kifayət deyil)", lambda: _same(_call(ucbucaqdir, 1, 2, 3), False)),
     (3, "ucbucaqdir(10, 1, 2) və ucbucaqdir(1, 10, 2) False olmalıdır (hər tərəf yoxlanmalıdır)",
      lambda: _same(_call(ucbucaqdir, 10, 1, 2), False) and _same(_call(ucbucaqdir, 1, 10, 2), False)),
 )
 """)

task("B10", "Uzun il (Leap Year)",
 """
 İlin **uzun il** (366 gün) olub-olmadığını müəyyən edən `uzun_ildir(il)` funksiyasını yazın.
 Qayda: il 4-ə bölünməli və 100-ə bölünməməlidir, **VƏ YA** 400-ə bölünməlidir.
 Funksiya `True` / `False` qaytarsın (və ya `"Uzun ildir"` / `"Uzun il deyil"` çap etsin).

 Nümunə: `uzun_ildir(2024)` → `True`
 """,
 _starter("uzun_ildir(il)"),
 """
 def uzun_ildir(il):
     return (il % 4 == 0 and il % 100 != 0) or il % 400 == 0
 """,
 """
 assert _same(_call(uzun_ildir, 2024), True), "2024 uzun ildir"
 assert _same(_call(uzun_ildir, 2023), False), "2023 uzun il deyil"
 assert _same(_call(uzun_ildir, 1900), False), "1900 uzun il deyil (100-ə bölünür, 400-ə bölünmür)"
 assert _same(_call(uzun_ildir, 2000), True), "2000 uzun ildir (400-ə bölünür)"
 """, partial=False)

task("B11", "Nöqtənin koordinat rübü",
 """
 (x, y) nöqtəsinin hansı **koordinat rübündə** (I, II, III, IV rüb) və ya **oxlar üzərində** olduğunu təyin edən
 `rub(x, y)` funksiyasını yazın. Mümkün cavablar: `"I rüb"`, `"II rüb"`, `"III rüb"`, `"IV rüb"`, `"OX oxu"`, `"OY oxu"`,
 `"Koordinat başlanğıcı"`. (`"II"`, `2` və ya `"2-ci rüb"` kimi cavablar da qəbul olunur.)

 Nümunə: `rub(-3, 5)` → `"II rüb"`
 """,
 _starter("rub(x, y)"),
 """
 def rub(x, y):
     if x == 0 and y == 0:
         return "Koordinat başlanğıcı"
     elif y == 0:
         return "OX oxu"
     elif x == 0:
         return "OY oxu"
     elif x > 0 and y > 0:
         return "I rüb"
     elif x < 0 and y > 0:
         return "II rüb"
     elif x < 0:
         return "III rüb"
     else:
         return "IV rüb"
 """,
 """
 import re
 def where(x, y):
     t = str(_call(rub, x, y)).casefold().replace("-", " ").replace("_", " ")
     if any(w in t for w in ("başlanğıc", "baslangic", "mərkəz", "merkez", "origin", "(0, 0)")):
         return "O"
     if "ox" in t or "oy" in t or "axis" in t or "oxu" in t or "ox " in t:
         if re.search(r"\\box\\b|\\bx\\b|abs", t):
             return "X"
         if re.search(r"\\boy\\b|\\by\\b|ord", t):
             return "Y"
     t = t.replace("rüb", " ").replace("rub", " ").replace("quadrant", " ")
     for word, q in (("iv", 4), ("iii", 3), ("ii", 2), ("i", 1)):
         if re.search(r"\\b" + word + r"\\b", t):
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
 """)

task("B12", "3 rəqəmli polindrom ədəd",
 """
 3 rəqəmli ədədin **polindrom** (soldan sağa və sağdan sola eyni oxunan) olub-olmadığını yoxlayan `polindrom_eded(n)`
 funksiyasını yazın. Funksiya `True` / `False` qaytarsın (və ya `"Polindromdur"` / `"Polindrom deyil"` çap etsin).

 Nümunə: `polindrom_eded(121)` → `True`, `polindrom_eded(123)` → `False`
 """,
 _starter("polindrom_eded(n)"),
 """
 def polindrom_eded(n):
     return n // 100 == n % 10
 """,
 """
 assert _same(_call(polindrom_eded, 121), True), "121 polindromdur"
 assert _same(_call(polindrom_eded, 123), False), "123 polindrom deyil"
 assert _same(_call(polindrom_eded, 707), True), "707 polindromdur"
 assert _same(_call(polindrom_eded, 100), False), "100 polindrom deyil"
 """, partial=False)

task("B13", "4 ədəd arasında mənfilərin sayı",
 """
 4 tam ədəd arasında neçə **mənfi** ədəd olduğunu tapan `menfi_say(a, b, c, d)` funksiyasını yazın (0 mənfi deyil).

 Nümunə: `menfi_say(-2, 5, -8, 0)` → `2`  (2 mənfi ədəd var)
 """,
 _starter("menfi_say(a, b, c, d)"),
 """
 def menfi_say(a, b, c, d):
     say = 0
     for x in (a, b, c, d):
         if x < 0:
             say += 1
     return say
 """,
 """
 return grade(
     (4, "menfi_say(-2, 5, -8, 0) 2 olmalıdır", lambda: _same(_call(menfi_say, -2, 5, -8, 0), 2)),
     (2, "menfi_say(-1, -2, -3, -4) 4 olmalıdır", lambda: _same(_call(menfi_say, -1, -2, -3, -4), 4)),
     (2, "menfi_say(1, 2, 3, 4) 0 olmalıdır", lambda: _same(_call(menfi_say, 1, 2, 3, 4), 0)),
     (2, "sıfır mənfi sayılmır: menfi_say(0, 0, -5, 0) 1 olmalıdır", lambda: _same(_call(menfi_say, 0, 0, -5, 0), 1)),
 )
 """)

task("B14", "Sadə kalkulyator",
 """
 İki ədəd və bir əməl simvoluna (`+`, `-`, `*`, `/`) görə nəticəni hesablayan `kalkulyator(a, b, emel)` funksiyasını yazın.
 **Sıfıra bölmə** halında xəbərdarlıq mesajı qaytarın (məs. `"Xəta: Sıfıra bölmə yolverilməzdir!"`).

 Nümunə: `kalkulyator(10, 4, '*')` → `40`, `kalkulyator(10, 0, '/')` → `"Xəta: Sıfıra bölmə yolverilməzdir!"`
 """,
 _starter("kalkulyator(a, b, emel)"),
 """
 def kalkulyator(a, b, emel):
     if emel == "+":
         return a + b
     elif emel == "-":
         return a - b
     elif emel == "*":
         return a * b
     elif emel == "/":
         if b == 0:
             return "Xəta: Sıfıra bölmə yolverilməzdir!"
         return a / b
 """,
 """
 def err(r):
     return isinstance(r, str) and _has_word(r, "xəta", "xeta", "sıfır", "sifir", "yolverilməz", "mümkün deyil", "error", "zero")
 return grade(
     (2, "toplama: kalkulyator(10, 4, '+') 14 olmalıdır", lambda: _same(_call(kalkulyator, 10, 4, "+"), 14)),
     (2, "çıxma: kalkulyator(10, 4, '-') 6 olmalıdır", lambda: _same(_call(kalkulyator, 10, 4, "-"), 6)),
     (2, "vurma: kalkulyator(10, 4, '*') 40 olmalıdır", lambda: _same(_call(kalkulyator, 10, 4, "*"), 40)),
     (2, "bölmə: kalkulyator(10, 4, '/') 2.5 olmalıdır", lambda: _same(_call(kalkulyator, 10, 4, "/"), 2.5)),
     (2, "sıfıra bölmə: kalkulyator(10, 0, '/') xəbərdarlıq mesajı verməlidir (proqram xəta ilə dayanmamalıdır)",
      lambda: err(_call(kalkulyator, 10, 0, "/"))),
 )
 """)

task("B15", "Həm 3-ə, həm də 5-ə bölünmə",
 """
 Ədədin **həm 3-ə, həm də 5-ə** qalıqsız bölünüb-bölünmədiyini şərt operatoru ilə yoxlayan `uc_ve_bese_bolunur(n)`
 funksiyasını yazın. Funksiya `True` / `False` qaytarsın (və ya `"Ədəd həm 3-ə, həm də 5-ə bölünür"` / `"Bölünmür"` çap etsin).

 Nümunə: `uc_ve_bese_bolunur(15)` → `True`
 """,
 _starter("uc_ve_bese_bolunur(n)"),
 """
 def uc_ve_bese_bolunur(n):
     return n % 3 == 0 and n % 5 == 0
 """,
 """
 assert _same(_call(uc_ve_bese_bolunur, 15), True), "15 həm 3-ə, həm də 5-ə bölünür"
 assert _same(_call(uc_ve_bese_bolunur, 45), True), "45 həm 3-ə, həm də 5-ə bölünür"
 assert _same(_call(uc_ve_bese_bolunur, 9), False), "9 yalnız 3-ə bölünür"
 assert _same(_call(uc_ve_bese_bolunur, 10), False), "10 yalnız 5-ə bölünür"
 assert _same(_call(uc_ve_bese_bolunur, 7), False), "7 heç birinə bölünmür"
 """, partial=False)

task("B16", "Ayın nömrəsinə görə fəsil",
 """
 Ayın nömrəsinə (1–12) görə həmin ayın aid olduğu **fəsli** qaytaran `fesil(ay)` funksiyasını yazın:
 12, 1, 2 → `"Qış"`; 3, 4, 5 → `"Yaz"`; 6, 7, 8 → `"Yay"`; 9, 10, 11 → `"Payız"`.

 Nümunə: `fesil(11)` → `"Payız"`  (Payız fəsli)
 """,
 _starter("fesil(ay)"),
 """
 def fesil(ay):
     if ay in (12, 1, 2):
         return "Qış"
     elif ay in (3, 4, 5):
         return "Yaz"
     elif ay in (6, 7, 8):
         return "Yay"
     else:
         return "Payız"
 """,
 """
 import re
 def season(m):
     t = str(_call(fesil, m)).casefold()
     for name, keys in (("qış", ("qış", "qis", "winter")), ("payız", ("payız", "payiz", "autumn", "fall")),
                        ("yaz", ("yaz", "spring")), ("yay", ("yay", "summer"))):
         if any(re.search(r"\\b" + k + r"\\b", t) for k in keys):
             return name
     return None
 return grade(
     (2, "fesil(11) Payız olmalıdır", lambda: season(11) == "payız"),
     (2, "qış ayları: 12, 1, 2", lambda: all(season(m) == "qış" for m in (12, 1, 2))),
     (2, "yaz ayları: 3, 4, 5", lambda: all(season(m) == "yaz" for m in (3, 4, 5))),
     (2, "yay ayları: 6, 7, 8", lambda: all(season(m) == "yay" for m in (6, 7, 8))),
     (2, "payız ayları: 9, 10", lambda: all(season(m) == "payız" for m in (9, 10))),
 )
 """)

# =====================================================================
# Kateqoriya C: Dövr Operatorları və İterasiya (For, While)
# =====================================================================
task("C4", "1-dən N-ə qədər ədədlərin cəmi",
 """
 1-dən N-ə qədər (N daxil) olan tam ədədlərin **cəmini** dövr vasitəsilə hesablayan `cem_1_n(n)` funksiyasını yazın.

 Nümunə: `cem_1_n(10)` → `55`  (Cəm = 55)
 """,
 _starter("cem_1_n(n)"),
 """
 def cem_1_n(n):
     cem = 0
     for i in range(1, n + 1):
         cem += i
     return cem
 """,
 """
 assert _same(_call(cem_1_n, 10), 55), "cem_1_n(10) 55 olmalıdır"
 assert _same(_call(cem_1_n, 1), 1), "cem_1_n(1) 1 olmalıdır"
 assert _same(_call(cem_1_n, 100), 5050), "cem_1_n(100) 5050 olmalıdır (N özü də daxildir)"
 """, partial=False)

task("C5", "N ədədinin faktorialı (dövr ilə)",
 """
 N ədədinin **faktorialını** (N! = 1 · 2 · 3 · … · N) dövr vasitəsilə hesablayan `faktorial(n)` funksiyasını yazın (0! = 1).

 Nümunə: `faktorial(5)` → `120`  (5! = 120)
 """,
 _starter("faktorial(n)"),
 """
 def faktorial(n):
     f = 1
     for i in range(2, n + 1):
         f *= i
     return f
 """,
 """
 return grade(
     (5, "faktorial(5) 120 olmalıdır", lambda: _same(_call(faktorial, 5), 120)),
     (3, "faktorial(10) 3628800 olmalıdır", lambda: _same(_call(faktorial, 10), 3628800)),
     (2, "faktorial(0) və faktorial(1) 1 olmalıdır", lambda: _same(_call(faktorial, 0), 1) and _same(_call(faktorial, 1), 1)),
 )
 """)

task("C6", "Sadə və ya mürəkkəb ədəd",
 """
 Müsbət tam ədədin **sadə** və ya **mürəkkəb** olduğunu müəyyən edən `sade_ededdir(n)` funksiyasını yazın.
 Funksiya `True` / `False` qaytarsın (və ya `"Sadə ədəddir"` / `"Mürəkkəb ədəddir"` çap etsin). Yadda saxlayın: 1 sadə deyil.

 Nümunə: `sade_ededdir(17)` → `True`
 """,
 _starter("sade_ededdir(n)"),
 """
 def sade_ededdir(n):
     if n < 2:
         return False
     i = 2
     while i * i <= n:
         if n % i == 0:
             return False
         i += 1
     return True
 """,
 """
 return grade(
     (4, "17, 2 və 97 sadədir (True)", lambda: all(_same(_call(sade_ededdir, p), True) for p in (17, 2, 97))),
     (3, "15, 91 (7 × 13) və 49 mürəkkəbdir (False)", lambda: all(_same(_call(sade_ededdir, c), False) for c in (15, 91, 49))),
     (3, "1 sadə ədəd deyil", lambda: _same(_call(sade_ededdir, 1), False)),
 )
 """)

task("C7", "Fibonacci ardıcıllığının ilk N həddi",
 """
 Fibonacci ardıcıllığının **ilk N həddini** siyahı kimi qaytaran `fibonacci_siyahi(n)` funksiyasını yazın
 (0, 1, 1, 2, 3, 5, 8, …).

 Nümunə: `fibonacci_siyahi(7)` → `[0, 1, 1, 2, 3, 5, 8]`
 """,
 _starter("fibonacci_siyahi(n)"),
 """
 def fibonacci_siyahi(n):
     a, b = 0, 1
     netice = []
     for _ in range(n):
         netice.append(a)
         a, b = b, a + b
     return netice
 """,
 """
 return grade(
     (5, "fibonacci_siyahi(7) [0, 1, 1, 2, 3, 5, 8] olmalıdır",
      lambda: _same(_call(fibonacci_siyahi, 7), [0, 1, 1, 2, 3, 5, 8])),
     (3, "fibonacci_siyahi(10) 34 ilə bitməlidir",
      lambda: _same(_call(fibonacci_siyahi, 10), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])),
     (2, "fibonacci_siyahi(2) [0, 1] olmalıdır", lambda: _same(_call(fibonacci_siyahi, 2), [0, 1])),
 )
 """)

task("C8", "Rəqəmlərin sayı və cəmi (while ilə)",
 """
 Tam ədədin **rəqəmlərinin sayını** və **rəqəmlərinin cəmini** `while` dövrü ilə hesablayan `reqem_say_cem(n)` funksiyasını yazın.
 Funksiya iki qiymət qaytarsın: `say, cem`.

 Nümunə: `reqem_say_cem(4052)` → `(4, 11)`  (Rəqəm sayı: 4, Rəqəm cəmi: 11)
 """,
 _starter("reqem_say_cem(n)"),
 """
 def reqem_say_cem(n):
     say, cem = 0, 0
     while n > 0:
         say += 1
         cem += n % 10
         n //= 10
     return say, cem
 """,
 """
 cases = [(4052, (4, 11)), (7, (1, 7)), (99999, (5, 45)), (1000, (4, 1))]
 res = [_seq(_call(reqem_say_cem, n), 2) for n, _ in cases]
 return grade(
     (5, "rəqəmlərin sayı", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "rəqəmlərin cəmi", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("C9", "Ədədin tərsi",
 """
 Müsbət tam ədədin **tərsini** (rəqəmlərinin əks sırası ilə yazılmış ədədi) quran `ters_eded(n)` funksiyasını yazın.

 Nümunə: `ters_eded(1234)` → `4321`  (Tərs ədəd: 4321)
 """,
 _starter("ters_eded(n)"),
 """
 def ters_eded(n):
     t = 0
     while n > 0:
         t = t * 10 + n % 10
         n //= 10
     return t
 """,
 """
 assert _same(_call(ters_eded, 1234), 4321), "ters_eded(1234) 4321 olmalıdır"
 assert _same(_call(ters_eded, 7), 7), "ters_eded(7) 7 olmalıdır"
 assert _same(_call(ters_eded, 90817), 71809), "ters_eded(90817) 71809 olmalıdır"
 assert _same(_call(ters_eded, 1200), 21), "ters_eded(1200) 21 olmalıdır"
 """, partial=False)

task("C10", "ƏBOB və ƏKOB",
 """
 İki natural ədədin **ƏBOB**-unu (ən böyük ortaq bölən) və **ƏKOB**-unu (ən kiçik ortaq bölünən) hesablayan
 `ebob_ekob(a, b)` funksiyasını yazın. Funksiya iki qiymət qaytarsın: `ebob, ekob`.

 Nümunə: `ebob_ekob(12, 18)` → `(6, 36)`
 """,
 _starter("ebob_ekob(a, b)"),
 """
 def ebob_ekob(a, b):
     x, y = a, b
     while y:
         x, y = y, x % y
     return x, a * b // x
 """,
 """
 cases = [((12, 18), (6, 36)), ((7, 13), (1, 91)), ((20, 5), (5, 20)), ((21, 6), (3, 42))]
 res = [_seq(_call(ebob_ekob, *a), 2) for a, _ in cases]
 return grade(
     (5, "ƏBOB", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "ƏKOB", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("C11", "Armstrong ədədləri",
 """
 `baslangic … son` aralığındakı (hər ikisi daxil) bütün 3 rəqəmli **Armstrong ədədlərini** siyahı kimi qaytaran
 `armstrong_ededleri(baslangic, son)` funksiyasını yazın. Armstrong ədədi — rəqəmlərinin kubları cəmi özünə bərabər olan ədəddir,
 məsələn 153 = 1³ + 5³ + 3³.

 Nümunə: `armstrong_ededleri(100, 999)` → `[153, 370, 371, 407]`
 """,
 _starter("armstrong_ededleri(baslangic, son)"),
 """
 def armstrong_ededleri(baslangic, son):
     netice = []
     for n in range(baslangic, son + 1):
         if (n // 100) ** 3 + (n // 10 % 10) ** 3 + (n % 10) ** 3 == n:
             netice.append(n)
     return netice
 """,
 """
 return grade(
     (5, "armstrong_ededleri(100, 999) [153, 370, 371, 407] olmalıdır",
      lambda: _same(_call(armstrong_ededleri, 100, 999), [153, 370, 371, 407])),
     (3, "armstrong_ededleri(150, 380) [153, 370, 371] olmalıdır",
      lambda: _same(_call(armstrong_ededleri, 150, 380), [153, 370, 371])),
     (2, "aralığın sonu daxildir: armstrong_ededleri(400, 407) [407] olmalıdır",
      lambda: _same(_call(armstrong_ededleri, 400, 407), [407])),
 )
 """)

task("C12", "N-ə qədər bütün sadə ədədlər",
 """
 N-ə qədər (N daxil) olan bütün **sadə ədədləri** siyahı kimi qaytaran `sadeler(n)` funksiyasını yazın.

 Nümunə: `sadeler(20)` → `[2, 3, 5, 7, 11, 13, 17, 19]`
 """,
 _starter("sadeler(n)"),
 """
 def sadeler(n):
     netice = []
     for k in range(2, n + 1):
         for d in range(2, int(k ** 0.5) + 1):
             if k % d == 0:
                 break
         else:
             netice.append(k)
     return netice
 """,
 """
 return grade(
     (5, "sadeler(20) [2, 3, 5, 7, 11, 13, 17, 19] olmalıdır", lambda: _same(_call(sadeler, 20), [2, 3, 5, 7, 11, 13, 17, 19])),
     (3, "sadeler(29) 23, 29 ilə bitməlidir (N özü də daxildir)",
      lambda: _same(_call(sadeler, 29), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])),
     (2, "sadeler(2) [2] olmalıdır", lambda: _same(_call(sadeler, 2), [2])),
 )
 """)

task("C13", "Ulduzlu üçbucaq (iç-içə dövrlər)",
 """
 **İç-içə dövrlərdən** istifadə edərək N sətirdən ibarət ulduzlu üçbucaq quran `ulduz_ucbucaq(n)` funksiyasını yazın.
 Sətirləri ekrana çıxara, ya da bir mətn kimi (sətirlər `\\n` ilə ayrılmış) və ya sətirlər siyahısı kimi qaytara bilərsiniz.

 Nümunə: `ulduz_ucbucaq(4)` ekrana çıxarır:

 ```
 *
 **
 ***
 ****
 ```
 """,
 _starter("ulduz_ucbucaq(n)"),
 """
 def ulduz_ucbucaq(n):
     for i in range(1, n + 1):
         setir = ""
         for j in range(i):
             setir += "*"
         print(setir)
 """,
 """
 def rows(n):
     return [r.replace(" ", "") for r in _lines(_call(ulduz_ucbucaq, n))]
 return grade(
     (5, "ulduz_ucbucaq(4) 4 sətir verməlidir: *, **, ***, ****", lambda: rows(4) == ["*" * i for i in range(1, 5)]),
     (3, "ulduz_ucbucaq(6) 6 sətir verməlidir", lambda: rows(6) == ["*" * i for i in range(1, 7)]),
     (2, "ulduz_ucbucaq(1) bir sətir verməlidir: *", lambda: rows(1) == ["*"]),
 )
 """)

task("C14", "0 daxil edilənə qədər cəm və ədədi orta",
 """
 Ədədlər siyahı şəklində verilir; istifadəçi **0 daxil edənə qədər** olan ədədlərin **cəmini** və **ədədi ortasını** hesablayan
 `cem_orta(ededler)` funksiyasını yazın (0 və ondan sonrakı ədədlər nəzərə alınmır). Funksiya iki qiymət qaytarsın: `cem, orta`.

 Nümunə: `cem_orta([5, 10, 15, 0])` → `(30, 10.0)`  (Cəm: 30, Ədədi orta: 10.0)
 """,
 _starter("cem_orta(ededler)"),
 """
 def cem_orta(ededler):
     cem, say = 0, 0
     i = 0
     while ededler[i] != 0:
         cem += ededler[i]
         say += 1
         i += 1
     return cem, cem / say
 """,
 """
 cases = [([5, 10, 15, 0], (30, 10.0)), ([4, 0], (4, 4.0)), ([2, 3, 0, 100, 200], (5, 2.5)), ([-6, 12, 3, 0], (9, 3.0))]
 res = [_seq(_call(cem_orta, lst), 2) for lst, _ in cases]
 return grade(
     (5, "cəm (0-a qədər)", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "ədədi orta (0-a qədər)", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("C15", "Ədədin bölənləri və onların sayı",
 """
 Tam ədədin **bütün bölənlərini** və **bölənlərinin sayını** tapan `bolenler(n)` funksiyasını yazın.
 Funksiya iki qiymət qaytarsın: `bolenler_siyahisi, say`.

 Nümunə: `bolenler(12)` → `([1, 2, 3, 4, 6, 12], 6)`  (Bölənlər: 1, 2, 3, 4, 6, 12 (Sayı: 6))
 """,
 _starter("bolenler(n)"),
 """
 def bolenler(n):
     lst = [d for d in range(1, n + 1) if n % d == 0]
     return lst, len(lst)
 """,
 """
 cases = {12: [1, 2, 3, 4, 6, 12], 7: [1, 7], 36: [1, 2, 3, 4, 6, 9, 12, 18, 36]}
 got = {n: _flat(_call(bolenler, n)) for n in cases}
 return grade(
     (6, "bölənlərin siyahısı", lambda: all(got[n][:len(d)] == d for n, d in cases.items())),
     (4, "bölənlərin sayı", lambda: all(len(got[n]) == len(d) + 1 and got[n][-1] == len(d) for n, d in cases.items())),
 )
 """)

task("C16", "7-yə bölündükdə qalığı 3 olan ədədlərin cəmi",
 """
 1-dən N-ə qədər (N daxil) olan ədədlər arasında **7-yə bölündükdə qalıqda 3** alınan ədədlərin cəmini hesablayan
 `qaliq_cemi(n)` funksiyasını yazın.

 Nümunə: `qaliq_cemi(100)` → `679`  (3 + 10 + 17 + … + 94)
 """,
 _starter("qaliq_cemi(n)"),
 """
 def qaliq_cemi(n):
     cem = 0
     for i in range(1, n + 1):
         if i % 7 == 3:
             cem += i
     return cem
 """,
 """
 return grade(
     (5, "qaliq_cemi(100) 679 olmalıdır", lambda: _same(_call(qaliq_cemi, 100), 679)),
     (3, "qaliq_cemi(20) 30 olmalıdır (3 + 10 + 17)", lambda: _same(_call(qaliq_cemi, 20), 30)),
     (2, "N özü də daxildir: qaliq_cemi(10) 13 olmalıdır (3 + 10)", lambda: _same(_call(qaliq_cemi, 10), 13)),
 )
 """)

# =====================================================================
# Kateqoriya D: Birölçülü və İkiölçülü Massivlər / Siyahılar
# =====================================================================
task("D4", "Ən böyük və ən kiçik element və onların indeksləri",
 """
 Siyahının **ən böyük** və **ən kiçik** elementini, həmçinin onların **indekslərini** tapan `max_min_indeks(lst)` funksiyasını
 yazın. Funksiya dörd qiymət qaytarsın: `max_deyer, max_indeks, min_deyer, min_indeks` (qiymət bir neçə dəfə varsa, ilk indeksi).

 Nümunə: `max_min_indeks([12, 45, 2, 89, 34])` → `(89, 3, 2, 2)`  — Max: 89 (indeks 3), Min: 2 (indeks 2)
 """,
 _starter("max_min_indeks(lst)"),
 """
 def max_min_indeks(lst):
     mx_i = mn_i = 0
     for i in range(len(lst)):
         if lst[i] > lst[mx_i]:
             mx_i = i
         if lst[i] < lst[mn_i]:
             mn_i = i
     return lst[mx_i], mx_i, lst[mn_i], mn_i
 """,
 """
 cases = [([12, 45, 2, 89, 34], (89, 3, 2, 2)), ([-5, -1, -9, 0], (0, 3, -9, 2)), ([7, 3, 7, 3], (7, 0, 3, 1))]
 res = [_seq(_call(max_min_indeks, lst), 4) for lst, _ in cases]
 return grade(
     (3, "ən böyük element", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (2, "ən böyük elementin indeksi", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
     (3, "ən kiçik element", lambda: all(r and _same(r[2], e[2]) for r, (_, e) in zip(res, cases))),
     (2, "ən kiçik elementin indeksi", lambda: all(r and _same(r[3], e[3]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("D5", "Cüt indekslərdəki elementlərin cəmi",
 """
 Siyahının **cüt indekslərində** (0, 2, 4, …) yerləşən elementlərin cəmini hesablayan `cut_indeks_cemi(lst)` funksiyasını yazın.

 Nümunə: `cut_indeks_cemi([10, 20, 30, 40, 50])` → `90`  (10 + 30 + 50)
 """,
 _starter("cut_indeks_cemi(lst)"),
 """
 def cut_indeks_cemi(lst):
     cem = 0
     for i in range(0, len(lst), 2):
         cem += lst[i]
     return cem
 """,
 """
 return grade(
     (5, "cut_indeks_cemi([10, 20, 30, 40, 50]) 90 olmalıdır", lambda: _same(_call(cut_indeks_cemi, [10, 20, 30, 40, 50]), 90)),
     (3, "cut_indeks_cemi([1, 100, 2, 100]) 3 olmalıdır (indekslər, qiymətlər yox)",
      lambda: _same(_call(cut_indeks_cemi, [1, 100, 2, 100]), 3)),
     (2, "cut_indeks_cemi([7]) 7 olmalıdır", lambda: _same(_call(cut_indeks_cemi, [7]), 7)),
 )
 """)

task("D6", "Müsbət ədədlərin ədədi ortası",
 """
 Siyahıdakı **yalnız müsbət** ədədlərin ədədi ortasını tapan `musbet_orta(lst)` funksiyasını yazın.

 Nümunə: `musbet_orta([-5, 10, -2, 20, 30])` → `20.0`  (Müsbətlərin ədədi ortası: 20.0)
 """,
 _starter("musbet_orta(lst)"),
 """
 def musbet_orta(lst):
     musbetler = [x for x in lst if x > 0]
     return sum(musbetler) / len(musbetler)
 """,
 """
 assert _same(_call(musbet_orta, [-5, 10, -2, 20, 30]), 20.0), "musbet_orta([-5, 10, -2, 20, 30]) 20.0 olmalıdır"
 assert _same(_call(musbet_orta, [3, 4]), 3.5), "musbet_orta([3, 4]) 3.5 olmalıdır"
 assert _same(_call(musbet_orta, [0, -1, 6, 0]), 6.0), "0 müsbət deyil: musbet_orta([0, -1, 6, 0]) 6.0 olmalıdır"
 """, partial=False)

task("D7", "Bubble Sort ilə çeşidləmə",
 """
 Siyahının elementlərini **Bubble Sort** alqoritmi ilə (yanaşı elementləri müqayisə edib yerini dəyişməklə) **artan sıra** ilə
 çeşidləyən `bubble_sort(lst)` funksiyasını yazın.

 Nümunə: `bubble_sort([64, 34, 25, 12, 22])` → `[12, 22, 25, 34, 64]`
 """,
 _starter("bubble_sort(lst)"),
 """
 def bubble_sort(lst):
     n = len(lst)
     for i in range(n - 1):
         for j in range(n - 1 - i):
             if lst[j] > lst[j + 1]:
                 lst[j], lst[j + 1] = lst[j + 1], lst[j]
     return lst
 """,
 """
 return grade(
     (5, "bubble_sort([64, 34, 25, 12, 22]) [12, 22, 25, 34, 64] olmalıdır",
      lambda: _same(_call(bubble_sort, [64, 34, 25, 12, 22]), [12, 22, 25, 34, 64])),
     (3, "mənfi və təkrarlanan ədədlər: [5, -1, 3, -1, 0] -> [-1, -1, 0, 3, 5]",
      lambda: _same(_call(bubble_sort, [5, -1, 3, -1, 0]), [-1, -1, 0, 3, 5])),
     (2, "tərs sıralı siyahı: [5, 4, 3, 2, 1] -> [1, 2, 3, 4, 5]",
      lambda: _same(_call(bubble_sort, [5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])),
 )
 """)

task("D8", "Təkrarlanan elementləri silmək",
 """
 Siyahıdakı təkrarlanan elementləri silərək yalnız **unikal** elementlərdən ibarət **yeni siyahı** quran `unikal(lst)`
 funksiyasını yazın. Elementlər ilk rast gəlindikləri ardıcıllıqla qalsın.

 Nümunə: `unikal([1, 2, 2, 3, 4, 4, 5])` → `[1, 2, 3, 4, 5]`
 """,
 _starter("unikal(lst)"),
 """
 def unikal(lst):
     netice = []
     for x in lst:
         if x not in netice:
             netice.append(x)
     return netice
 """,
 """
 return grade(
     (5, "unikal([1, 2, 2, 3, 4, 4, 5]) [1, 2, 3, 4, 5] olmalıdır", lambda: _same(_call(unikal, [1, 2, 2, 3, 4, 4, 5]), [1, 2, 3, 4, 5])),
     (3, "ilk rast gəlinmə sırası: unikal([3, 1, 3, 2, 1]) [3, 1, 2] olmalıdır", lambda: _same(_call(unikal, [3, 1, 3, 2, 1]), [3, 1, 2])),
     (2, "hamısı eyni: unikal([7, 7, 7]) [7] olmalıdır", lambda: _same(_call(unikal, [7, 7, 7]), [7])),
 )
 """)

task("D9", "Siyahını K mövqe sağa dövri sürüşdürmək",
 """
 Siyahının elementlərini **K mövqe sağa dövri sürüşdürən** (Cyclic Shift) `saga_surusdur(lst, k)` funksiyasını yazın
 (K siyahının uzunluğundan böyük ola bilər).

 Nümunə: `saga_surusdur([1, 2, 3, 4, 5], 2)` → `[4, 5, 1, 2, 3]`
 """,
 _starter("saga_surusdur(lst, k)"),
 """
 def saga_surusdur(lst, k):
     k = k % len(lst)
     return lst[-k:] + lst[:-k] if k else lst[:]
 """,
 """
 return grade(
     (5, "saga_surusdur([1, 2, 3, 4, 5], 2) [4, 5, 1, 2, 3] olmalıdır",
      lambda: _same(_call(saga_surusdur, [1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3])),
     (2, "K = 1: saga_surusdur([10, 20, 30], 1) [30, 10, 20] olmalıdır",
      lambda: _same(_call(saga_surusdur, [10, 20, 30], 1), [30, 10, 20])),
     (3, "K uzunluqdan böyükdür: saga_surusdur([1, 2, 3, 4, 5], 7) [4, 5, 1, 2, 3] olmalıdır",
      lambda: _same(_call(saga_surusdur, [1, 2, 3, 4, 5], 7), [4, 5, 1, 2, 3])),
 )
 """)

task("D10", "X ədədinin təkrar sayı və ilk indeksi",
 """
 Siyahıda verilmiş X ədədinin **neçə dəfə təkrarlandığını** və **ilk rast gəlindiyi indeksi** tapan `tekrar_ve_indeks(lst, x)`
 funksiyasını yazın. Funksiya iki qiymət qaytarsın: `say, ilk_indeks`.

 Nümunə: `tekrar_ve_indeks([5, 3, 5, 2, 5, 8], 5)` → `(3, 0)`  (Təkrar sayı: 3, İlk indeks: 0)
 """,
 _starter("tekrar_ve_indeks(lst, x)"),
 """
 def tekrar_ve_indeks(lst, x):
     return lst.count(x), lst.index(x)
 """,
 """
 cases = [(([5, 3, 5, 2, 5, 8], 5), (3, 0)), (([1, 2, 3, 2, 2], 2), (3, 1)), (([4, 6, 9], 9), (1, 2))]
 res = [_seq(_call(tekrar_ve_indeks, *a), 2) for a, _ in cases]
 return grade(
     (5, "təkrar sayı", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "ilk indeks", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("D11", "Matrisin hər sətrinin cəmi",
 """
 N × M ölçülü matrisin (siyahılar siyahısı) **hər sətrinin elementlərinin cəmini** ayrıca hesablayıb siyahı kimi qaytaran
 `setir_cemleri(matris)` funksiyasını yazın.

 Nümunə: `setir_cemleri([[1, 2, 3], [4, 5, 6]])` → `[6, 15]`  (Sətir 1 cəmi: 6, Sətir 2 cəmi: 15)
 """,
 _starter("setir_cemleri(matris)"),
 """
 def setir_cemleri(matris):
     netice = []
     for setir in matris:
         cem = 0
         for x in setir:
             cem += x
         netice.append(cem)
     return netice
 """,
 """
 return grade(
     (5, "setir_cemleri([[1, 2, 3], [4, 5, 6]]) [6, 15] olmalıdır", lambda: _same(_call(setir_cemleri, [[1, 2, 3], [4, 5, 6]]), [6, 15])),
     (3, "3 sətirli matris: [[1, 1], [2, 2], [-3, 10]] -> [2, 4, 7]",
      lambda: _same(_call(setir_cemleri, [[1, 1], [2, 2], [-3, 10]]), [2, 4, 7])),
     (2, "bir sətirli matris: [[5, 5, 5, 5]] -> [20]", lambda: _same(_call(setir_cemleri, [[5, 5, 5, 5]]), [20])),
 )
 """)

task("D12", "Baş diaqonalın cəmi",
 """
 N × N ölçülü kvadrat matrisin **baş diaqonalında** yerləşən elementlərin cəmini hesablayan `bas_diaqonal_cemi(matris)`
 funksiyasını yazın.

 Nümunə: `bas_diaqonal_cemi([[1, 2], [3, 4]])` → `5`  (1 + 4)
 """,
 _starter("bas_diaqonal_cemi(matris)"),
 """
 def bas_diaqonal_cemi(matris):
     cem = 0
     for i in range(len(matris)):
         cem += matris[i][i]
     return cem
 """,
 """
 assert _same(_call(bas_diaqonal_cemi, [[1, 2], [3, 4]]), 5), "[[1, 2], [3, 4]] üçün cavab 5 olmalıdır"
 assert _same(_call(bas_diaqonal_cemi, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]), 15), "3 × 3 matris üçün cavab 15 olmalıdır (1 + 5 + 9)"
 assert _same(_call(bas_diaqonal_cemi, [[-2]]), -2), "[[-2]] üçün cavab -2 olmalıdır"
 """, partial=False)

task("D13", "Köməkçi diaqonalın maksimumu",
 """
 N × N ölçülü kvadrat matrisin **köməkçi diaqonalında** (sağ yuxarı küncdən sol aşağı küncə) yerləşən elementlərin
 **maksimumunu** tapan `komekci_diaqonal_max(matris)` funksiyasını yazın.

 Nümunə: `komekci_diaqonal_max([[1, 9], [3, 4]])` → `9`  (9 və 3-dən ən böyüyü)
 """,
 _starter("komekci_diaqonal_max(matris)"),
 """
 def komekci_diaqonal_max(matris):
     n = len(matris)
     mx = matris[0][n - 1]
     for i in range(n):
         if matris[i][n - 1 - i] > mx:
             mx = matris[i][n - 1 - i]
     return mx
 """,
 """
 return grade(
     (4, "komekci_diaqonal_max([[1, 9], [3, 4]]) 9 olmalıdır", lambda: _same(_call(komekci_diaqonal_max, [[1, 9], [3, 4]]), 9)),
     (4, "3 × 3: [[1, 2, 3], [4, 5, 6], [70, 8, 9]] -> 70 (köməkçi diaqonal: 3, 5, 70)",
      lambda: _same(_call(komekci_diaqonal_max, [[1, 2, 3], [4, 5, 6], [70, 8, 9]]), 70)),
     (2, "baş diaqonal yox, köməkçi diaqonal: [[100, 1], [2, 100]] -> 2",
      lambda: _same(_call(komekci_diaqonal_max, [[100, 1], [2, 100]]), 2)),
 )
 """)

task("D14", "Matrisin transponirə edilməsi",
 """
 N × M ölçülü matrisin **transponirə edilmiş** (M × N) matrisini quran `transpoze(matris)` funksiyasını yazın
 (sətirlər sütunlara çevrilir).

 Nümunə: `transpoze([[1, 2], [3, 4], [5, 6]])` → `[[1, 3, 5], [2, 4, 6]]`
 """,
 _starter("transpoze(matris)"),
 """
 def transpoze(matris):
     netice = []
     for j in range(len(matris[0])):
         setir = []
         for i in range(len(matris)):
             setir.append(matris[i][j])
         netice.append(setir)
     return netice
 """,
 """
 return grade(
     (5, "transpoze([[1, 2], [3, 4], [5, 6]]) [[1, 3, 5], [2, 4, 6]] olmalıdır",
      lambda: _same(_call(transpoze, [[1, 2], [3, 4], [5, 6]]), [[1, 3, 5], [2, 4, 6]])),
     (3, "kvadrat matris: [[1, 2], [3, 4]] -> [[1, 3], [2, 4]]", lambda: _same(_call(transpoze, [[1, 2], [3, 4]]), [[1, 3], [2, 4]])),
     (2, "bir sətir: [[7, 8, 9]] -> [[7], [8], [9]]", lambda: _same(_call(transpoze, [[7, 8, 9]]), [[7], [8], [9]])),
 )
 """)

task("D15", "Tək ədədləri 0 ilə əvəz etmək",
 """
 Siyahıdakı bütün **tək ədədləri 0 ilə əvəz edən** `tekleri_sifirla(lst)` funksiyasını yazın.

 Nümunə: `tekleri_sifirla([1, 2, 3, 4, 5, 6])` → `[0, 2, 0, 4, 0, 6]`
 """,
 _starter("tekleri_sifirla(lst)"),
 """
 def tekleri_sifirla(lst):
     return [0 if x % 2 != 0 else x for x in lst]
 """,
 """
 assert _same(_call(tekleri_sifirla, [1, 2, 3, 4, 5, 6]), [0, 2, 0, 4, 0, 6]), "[1, 2, 3, 4, 5, 6] -> [0, 2, 0, 4, 0, 6] olmalıdır"
 assert _same(_call(tekleri_sifirla, [-3, -2, 7]), [0, -2, 0]), "mənfi tək ədədlər də: [-3, -2, 7] -> [0, -2, 0] olmalıdır"
 assert _same(_call(tekleri_sifirla, [2, 4, 8]), [2, 4, 8]), "tək ədəd yoxdursa siyahı dəyişməməlidir"
 """, partial=False)

task("D16", "İki siyahının kəsişməsi",
 """
 İki siyahının **kəsişməsində** (hər ikisində mövcud olan) yerləşən **unikal** elementləri siyahı kimi qaytaran
 `kesisme(lst1, lst2)` funksiyasını yazın (elementlərin sırası vacib deyil).

 Nümunə: `kesisme([1, 2, 3, 4], [3, 4, 5, 6])` → `[3, 4]`
 """,
 _starter("kesisme(lst1, lst2)"),
 """
 def kesisme(lst1, lst2):
     netice = []
     for x in lst1:
         if x in lst2 and x not in netice:
             netice.append(x)
     return netice
 """,
 """
 return grade(
     (5, "kesisme([1, 2, 3, 4], [3, 4, 5, 6]) [3, 4] olmalıdır", lambda: _same_set(_call(kesisme, [1, 2, 3, 4], [3, 4, 5, 6]), [3, 4])),
     (3, "təkrarlar yalnız bir dəfə: kesisme([1, 1, 2, 2, 9], [2, 2, 1]) [1, 2] olmalıdır",
      lambda: _same_set(_call(kesisme, [1, 1, 2, 2, 9], [2, 2, 1]), [1, 2])),
     (2, "ortaq element yoxdursa boş siyahı: kesisme([1, 2], [3, 4]) -> []",
      lambda: _same(_call(kesisme, [1, 2], [3, 4]), [])),
 )
 """)

# =====================================================================
# Kateqoriya E: Mətn Sətirləri (Strings) və Funksiyalar
# =====================================================================
task("E3", "Cümlədəki sözlərin sayı",
 """
 Cümlədəki **sözlərin sayını** tapan `soz_sayi(cumle)` funksiyasını yazın (sözlər boşluqlarla ayrılır).

 Nümunə: `soz_sayi("Python proqramlaşdırma dili çox rahatdır")` → `5`  (Söz sayı: 5)
 """,
 _starter("soz_sayi(cumle)"),
 """
 def soz_sayi(cumle):
     return len(cumle.split())
 """,
 """
 return grade(
     (5, "soz_sayi('Python proqramlaşdırma dili çox rahatdır') 5 olmalıdır",
      lambda: _same(_call(soz_sayi, "Python proqramlaşdırma dili çox rahatdır"), 5)),
     (3, "artıq boşluqlar: soz_sayi('  salam   dünya ') 2 olmalıdır", lambda: _same(_call(soz_sayi, "  salam   dünya "), 2)),
     (2, "bir söz: soz_sayi('Bakı') 1 olmalıdır", lambda: _same(_call(soz_sayi, "Bakı"), 1)),
 )
 """)

task("E4", "Sait və samit hərflərin sayı",
 """
 Mətndəki **sait** və **samit** hərflərin sayını ayrı-ayrılıqda hesablayan `sait_samit(metn)` funksiyasını yazın.
 Saitlər: **a, ı, o, u, e, ə, i, ö, ü** (böyük hərflər də). Hərf olmayan simvollar (boşluq, rəqəm, işarə) sayılmır.
 Funksiya iki qiymət qaytarsın: `sait_sayi, samit_sayi`.

 Nümunə: `sait_samit("Salam Baku")` → `(4, 5)`  (Sait sayı: 4, Samit sayı: 5)
 """,
 _starter("sait_samit(metn)"),
 """
 def sait_samit(metn):
     saitler = "aıoueəiöüAIOUEƏİÖÜ"
     sait = samit = 0
     for ch in metn:
         if ch.isalpha():
             if ch in saitler:
                 sait += 1
             else:
                 samit += 1
     return sait, samit
 """,
 """
 cases = [("Salam Baku", (4, 5)), ("Ölkə 2026!", (2, 2)), ("Python", (1, 5)), ("Azərbaycan", (4, 6))]
 res = [_seq(_call(sait_samit, s), 2) for s, _ in cases]
 return grade(
     (5, "sait hərflərin sayı (ə, ö, ü, ı da saitdir)", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),
     (5, "samit hərflərin sayı (boşluq, rəqəm və işarələr sayılmır)", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),
 )
 """)

task("E5", "Polindrom söz",
 """
 Sözün **polindrom** (soldan sağa və sağdan sola eyni oxunan, məs. `'ana'`, `'kələk'`, `'radar'`) olub-olmadığını yoxlayan
 `polindrom_soz(soz)` funksiyasını yazın. Funksiya `True` / `False` qaytarsın (və ya `"Polindromdur"` / `"Polindrom deyil"` çap etsin).

 Nümunə: `polindrom_soz("radar")` → `True`
 """,
 _starter("polindrom_soz(soz)"),
 """
 def polindrom_soz(soz):
     return soz == soz[::-1]
 """,
 """
 assert _same(_call(polindrom_soz, "radar"), True), "'radar' polindromdur"
 assert _same(_call(polindrom_soz, "kələk"), True), "'kələk' polindromdur"
 assert _same(_call(polindrom_soz, "ana"), True), "'ana' polindromdur"
 assert _same(_call(polindrom_soz, "python"), False), "'python' polindrom deyil"
 assert _same(_call(polindrom_soz, "abca"), False), "'abca' polindrom deyil"
 """, partial=False)

task("E6", "Hərflərin registrini dəyişmək",
 """
 Mətndəki bütün kiçik hərfləri böyük, böyük hərfləri isə kiçik hərflərə çevirən `registr_deyis(metn)` funksiyasını yazın
 (**`swapcase()` metodundan istifadə etmədən**; digər simvollar dəyişmir).

 Nümunə: `registr_deyis("PyThOn")` → `"pYtHoN"`
 """,
 _starter("registr_deyis(metn)"),
 """
 def registr_deyis(metn):
     netice = ""
     for ch in metn:
         if ch.islower():
             netice += ch.upper()
         elif ch.isupper():
             netice += ch.lower()
         else:
             netice += ch
     return netice
 """,
 """
 return grade(
     (5, 'registr_deyis("PyThOn") "pYtHoN" olmalıdır', lambda: _same(_call(registr_deyis, "PyThOn"), "pYtHoN")),
     (3, 'boşluq və rəqəmlər qalır: registr_deyis("Hello World 2026") "hELLO wORLD 2026" olmalıdır',
      lambda: _same(_call(registr_deyis, "Hello World 2026"), "hELLO wORLD 2026")),
     (2, 'registr_deyis("abc") "ABC" olmalıdır', lambda: _same(_call(registr_deyis, "abc"), "ABC")),
 )
 """)

task("E7", "Simvolu başqa simvolla əvəz etmək",
 """
 Mətndə verilmiş bir simvolu başqa simvolla əvəz edən `simvol_evez_et(metn, kohne, yeni)` funksiyasını yazın.

 Nümunə: `simvol_evez_et("alma", "a", "o")` → `"olmo"`
 """,
 _starter("simvol_evez_et(metn, kohne, yeni)"),
 """
 def simvol_evez_et(metn, kohne, yeni):
     netice = ""
     for ch in metn:
         netice += yeni if ch == kohne else ch
     return netice
 """,
 """
 return grade(
     (5, 'simvol_evez_et("alma", "a", "o") "olmo" olmalıdır', lambda: _same(_call(simvol_evez_et, "alma", "a", "o"), "olmo")),
     (3, 'simvol_evez_et("salam dünya", " ", "_") "salam_dünya" olmalıdır',
      lambda: _same(_call(simvol_evez_et, "salam dünya", " ", "_"), "salam_dünya")),
     (2, 'simvol yoxdursa mətn dəyişmir: simvol_evez_et("kitab", "z", "x") "kitab"',
      lambda: _same(_call(simvol_evez_et, "kitab", "z", "x"), "kitab")),
 )
 """)

task("E8", "Mətni tərsinə çevirmək",
 """
 Mətni **tərsinə çevirən** `reverse_string(s)` funksiyasını yazın.

 Nümunə: `reverse_string("Python")` → `"nohtyP"`
 """,
 _starter("reverse_string(s)"),
 """
 def reverse_string(s):
     return s[::-1]
 """,
 """
 assert _same(_call(reverse_string, "Python"), "nohtyP"), 'reverse_string("Python") "nohtyP" olmalıdır'
 assert _same(_call(reverse_string, "Bakı 2026"), "6202 ıkaB"), 'reverse_string("Bakı 2026") "6202 ıkaB" olmalıdır'
 assert _same(_call(reverse_string, "a"), "a"), 'reverse_string("a") "a" olmalıdır'
 """, partial=False)

task("E9", "Sadə ədəd funksiyası is_prime(n)",
 """
 Ədədin sadə olub-olmadığını yoxlayan və **boolean** (`True` / `False`) dəyər qaytaran `is_prime(n)` funksiyasını yazın.

 Nümunə: `is_prime(13)` → `True`, `is_prime(10)` → `False`
 """,
 _starter("is_prime(n)"),
 """
 def is_prime(n):
     if n < 2:
         return False
     for d in range(2, int(n ** 0.5) + 1):
         if n % d == 0:
             return False
     return True
 """,
 """
 return grade(
     (4, "13, 2 və 89 üçün True", lambda: all(_same(_call(is_prime, p), True) for p in (13, 2, 89))),
     (4, "10, 21 və 121 (11 × 11) üçün False", lambda: all(_same(_call(is_prime, c), False) for c in (10, 21, 121))),
     (2, "1 və 0 sadə deyil (False)", lambda: _same(_call(is_prime, 1), False) and _same(_call(is_prime, 0), False)),
 )
 """)

task("E10", "Rekursiv faktorial",
 """
 Ədədin faktorialını hesablayan **rekursiv** funksiya `factorial_recursive(n)` yazın (funksiya özünü çağırır; 0! = 1).

 Nümunə: `factorial_recursive(5)` → `120`
 """,
 _starter("factorial_recursive(n)"),
 """
 def factorial_recursive(n):
     if n <= 1:
         return 1
     return n * factorial_recursive(n - 1)
 """,
 """
 assert _same(_call(factorial_recursive, 5), 120), "factorial_recursive(5) 120 olmalıdır"
 assert _same(_call(factorial_recursive, 1), 1), "factorial_recursive(1) 1 olmalıdır"
 assert _same(_call(factorial_recursive, 0), 1), "factorial_recursive(0) 1 olmalıdır"
 assert _same(_call(factorial_recursive, 10), 3628800), "factorial_recursive(10) 3628800 olmalıdır"
 """, partial=False)

task("E11", "Siyahının orta qiyməti",
 """
 Ədəd siyahısı qəbul edən və onun elementlərinin **orta qiymətini** qaytaran `calculate_average(lst)` funksiyasını yazın.

 Nümunə: `calculate_average([10, 20, 30, 40])` → `25.0`
 """,
 _starter("calculate_average(lst)"),
 """
 def calculate_average(lst):
     return sum(lst) / len(lst)
 """,
 """
 return grade(
     (5, "calculate_average([10, 20, 30, 40]) 25.0 olmalıdır", lambda: _same(_call(calculate_average, [10, 20, 30, 40]), 25.0)),
     (3, "kəsr nəticə: calculate_average([1, 2]) 1.5 olmalıdır", lambda: _same(_call(calculate_average, [1, 2]), 1.5)),
     (2, "mənfi ədədlər: calculate_average([-4, 4, 3]) 1.0 olmalıdır", lambda: _same(_call(calculate_average, [-4, 4, 3]), 1.0)),
 )
 """)

task("E12", "Avklid alqoritmi ilə ƏBOB: gcd(a, b)",
 """
 İki ədədin ƏBOB-unu **Avklid alqoritmi** ilə hesablayan `gcd(a, b)` funksiyasını yazın
 ((a, b) cütünü b 0 olana qədər (b, a % b) ilə əvəz edin).

 Nümunə: `gcd(48, 18)` → `6`
 """,
 _starter("gcd(a, b)"),
 """
 def gcd(a, b):
     while b != 0:
         a, b = b, a % b
     return a
 """,
 """
 assert _same(_call(gcd, 48, 18), 6), "gcd(48, 18) 6 olmalıdır"
 assert _same(_call(gcd, 17, 5), 1), "gcd(17, 5) 1 olmalıdır"
 assert _same(_call(gcd, 100, 75), 25), "gcd(100, 75) 25 olmalıdır"
 assert _same(_call(gcd, 7, 0), 7), "gcd(7, 0) 7 olmalıdır"
 """, partial=False)

task("E13", "Cümlədə ən uzun söz",
 """
 Cümlədəki **ən uzun sözü** tapıb qaytaran `en_uzun_soz(cumle)` funksiyasını yazın
 (eyni uzunluqda bir neçə söz varsa, birincisini qaytarın).

 Nümunə: `en_uzun_soz("Proqramlaşdırma kursu uğurla başladı")` → `"Proqramlaşdırma"`
 """,
 _starter("en_uzun_soz(cumle)"),
 """
 def en_uzun_soz(cumle):
     en_uzun = ""
     for soz in cumle.split():
         if len(soz) > len(en_uzun):
             en_uzun = soz
     return en_uzun
 """,
 """
 return grade(
     (5, 'en_uzun_soz("Proqramlaşdırma kursu uğurla başladı") "Proqramlaşdırma" olmalıdır',
      lambda: _same(_call(en_uzun_soz, "Proqramlaşdırma kursu uğurla başladı"), "Proqramlaşdırma")),
     (3, 'en_uzun_soz("Bakı gözəl şəhərdir") "şəhərdir" olmalıdır', lambda: _same(_call(en_uzun_soz, "Bakı gözəl şəhərdir"), "şəhərdir")),
     (2, 'eyni uzunluq -> birincisi: en_uzun_soz("ana ata bal") "ana" olmalıdır', lambda: _same(_call(en_uzun_soz, "ana ata bal"), "ana")),
 )
 """)

task("E14", "Simvolların tezlik lüğəti",
 """
 Mətndə hər simvolun neçə dəfə işləndiyini **tezlik lüğəti** (Dictionary) şəklində `{simvol: say}` qaytaran
 `simvol_tezliyi(metn)` funksiyasını yazın.

 Nümunə: `simvol_tezliyi("kitab")` → `{'k': 1, 'i': 1, 't': 1, 'a': 1, 'b': 1}`
 """,
 _starter("simvol_tezliyi(metn)"),
 """
 def simvol_tezliyi(metn):
     lugat = {}
     for ch in metn:
         lugat[ch] = lugat.get(ch, 0) + 1
     return lugat
 """,
 """
 return grade(
     (4, "simvol_tezliyi('kitab') {'k': 1, 'i': 1, 't': 1, 'a': 1, 'b': 1} olmalıdır",
      lambda: _same(_call(simvol_tezliyi, "kitab"), {'k': 1, 'i': 1, 't': 1, 'a': 1, 'b': 1})),
     (4, "təkrarlanan simvollar: simvol_tezliyi('alma') {'a': 2, 'l': 1, 'm': 1} olmalıdır",
      lambda: _same(_call(simvol_tezliyi, "alma"), {'a': 2, 'l': 1, 'm': 1})),
     (2, "simvol_tezliyi('ooo') {'o': 3} olmalıdır", lambda: _same(_call(simvol_tezliyi, "ooo"), {'o': 3})),
 )
 """)

task("E15", "Cüt ədədləri süzgəcdən keçirmək: get_evens(lst)",
 """
 Siyahıdakı **cüt ədədləri** süzgəcdən keçirib **yeni siyahı** qaytaran `get_evens(lst)` funksiyasını yazın.

 Nümunə: `get_evens([1, 2, 3, 4, 5, 6, 7, 8])` → `[2, 4, 6, 8]`
 """,
 _starter("get_evens(lst)"),
 """
 def get_evens(lst):
     return [x for x in lst if x % 2 == 0]
 """,
 """
 return grade(
     (5, "get_evens([1, 2, 3, 4, 5, 6, 7, 8]) [2, 4, 6, 8] olmalıdır",
      lambda: _same(_call(get_evens, [1, 2, 3, 4, 5, 6, 7, 8]), [2, 4, 6, 8])),
     (3, "mənfi ədədlər və sıfır: get_evens([-4, 0, 7, 10]) [-4, 0, 10] olmalıdır",
      lambda: _same(_call(get_evens, [-4, 0, 7, 10]), [-4, 0, 10])),
     (2, "cüt ədəd yoxdursa: get_evens([1, 3, 5]) [] olmalıdır", lambda: _same(_call(get_evens, [1, 3, 5]), [])),
 )
 """)

task("E16", "Rekursiv Fibonacci: fibonacci(n)",
 """
 N parametrini qəbul edən və **N-ci Fibonacci ədədini** qaytaran **rekursiv** funksiya `fibonacci(n)` yazın
 (fibonacci(0) = 0, fibonacci(1) = 1).

 Nümunə: `fibonacci(6)` → `8`  (Ardıcıllıq: 0, 1, 1, 2, 3, 5, 8)
 """,
 _starter("fibonacci(n)"),
 """
 def fibonacci(n):
     if n < 2:
         return n
     return fibonacci(n - 1) + fibonacci(n - 2)
 """,
 """
 return grade(
     (5, "fibonacci(6) 8 olmalıdır", lambda: _same(_call(fibonacci, 6), 8)),
     (3, "fibonacci(10) 55 olmalıdır", lambda: _same(_call(fibonacci, 10), 55)),
     (2, "başlanğıc qiymətlər: fibonacci(0) 0, fibonacci(1) 1 olmalıdır",
      lambda: _same(_call(fibonacci, 0), 0) and _same(_call(fibonacci, 1), 1)),
 )
 """)

assert len(CODING) == 60
assert [sum(1 for t in CODING.values() if t["cat"] == c) for c in CATEGORIES] == [8, 12, 13, 13, 14]
