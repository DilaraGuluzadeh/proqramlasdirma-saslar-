# -*- coding: utf-8 -*-
"""proqramlasdirmanin_esaslari_imtahan_suallari_v2.docx — 20 nəzəri sual -> çoxvariantlı test sualı.

Word faylında 20 nəzəri sual var (A: 8, B: 4, C: 3, D: 3, E: 2). 5 variant × 4 nəzəri sual = 20,
yəni hər nəzəri sual dəqiq bir variantda istifadə olunur.

Format: (nömrə, kateqoriya, qısa başlıq, sual (Markdown), düzgün cavab, [3 səhv cavab])
"""

THEORY_CATEGORIES = {
    "A": "Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar",
    "B": "Şərt Operatorları və Budaqlanan Alqoritmlər",
    "C": "Dövr Operatorları və İterasiya (For, While)",
    "D": "Birölçülü və İkiölçülü Massivlər / Siyahılar",
    "E": "Mətn Sətirləri (Strings) və Funksiyalar",
}

THEORY = [
 # ------------------------------------------------------------------ Kateqoriya A
 ("A1", "A", "Yüksək və aşağı səviyyəli dillər; kompilyator və interpretator",
  "Yüksək və aşağı səviyyəli dillər, kompilyator və interpretator haqqında hansı ifadə düzgündür və Python-u düzgün təsnif edir?",
  "Yüksək səviyyəli dillər insan dilinə yaxın və daşınandır, aşağı səviyyəli dillər (maşın kodu, assembler) avadanlığa yaxındır; "
  "kompilyator proqramı icradan əvvəl bütövlükdə tərcümə edir, interpretator isə əmr-əmr icra edir — Python yüksək səviyyəli, interpretasiya olunan dildir",
  ["Python aşağı səviyyəli dildir, çünki prosessorun registrləri ilə birbaşa işləyir və hər icradan əvvəl .exe faylına kompilyasiya olunur",
   "Yüksək səviyyəli dillər həmişə maşın kodundan sürətli işləyir, çünki heç bir tərcüməyə ehtiyac duymur",
   "Kompilyator proqramı sətir-sətir icra edir, interpretator isə əvvəlcə bütün proqramı maşın koduna çevirib .exe fayl yaradır"]),

 ("A2", "A", "Stack və Heap yaddaş sahələri",
  "Python-un yaddaş modelində **Stack** və **Heap** sahələrinin rolu haqqında hansı ifadə düzgündür?",
  "Stack funksiya çağırışlarının çərçivələrini və lokal adları (istinadları) saxlayır və funksiya bitəndə avtomatik boşalır; "
  "Heap obyektlərin özlərini (int, str, list …) saxlayır və onlara istinad qalmayanda istinad sayğacı / zibil toplayıcı (garbage collector) onları silir",
  ["Bütün obyektlər, o cümlədən siyahılar, Stack-də saxlanılır və hər mənimsətmədə yeni dəyişənə tam surəti çıxarılır",
   "Heap yalnız qlobal dəyişənlər, Stack isə yalnız sətirlər (str) üçün istifadə olunur",
   "Python-da Heap yaddaşını proqramçı free() funksiyası ilə əl ilə boşaltmalıdır, əks halda proqram dayanır"]),

 ("A3", "A", "Dinamik tipləşdirmə və girintilər",
  "Python-da **dinamik tipləşdirmə** və **girintilər (indentation)** haqqında hansı ifadə düzgündür?",
  "Tip dəyişənə deyil, obyektə aiddir, ona görə eyni ad əvvəl `int`, sonra `str` obyektinə istinad edə bilər; "
  "girinti sintaksisin hissəsidir — `if`, `for`, `def` … sonrakı blokları müəyyən edir, səhv girinti `IndentationError` yaradır",
  ["Hər dəyişən tipi ilə elan olunmalıdır, məsələn `int x = 5`, və bu tip sonradan heç vaxt dəyişə bilməz",
   "Girintilər yalnız oxunaqlılıq üçündür; Python blokları fiqurlu mötərizələrlə `{ }` müəyyən edir",
   "`x = 5` yazıldıqdan sonra `x = \"salam\"` əmri `TypeError` verir, çünki `x` artıq tam ədəd tipindədir"]),

 ("A4", "A", "Əsas məlumat tipləri, type() və tip çevrilməsi",
  "Bu kod ekrana nə çıxarır?\n\n```python\nx = \"7\"\ny = int(x) + 3\nprint(type(x), y, float(y))\n```",
  "`<class 'str'> 10 10.0`",
  ["`<class 'int'> 10 10.0`", "`<class 'str'> 73 73.0`", "`<class 'str'> 10 10`"]),

 ("A5", "A", "Riyazi operatorlar və icra prioriteti",
  "Aşağıdakı ifadənin qiyməti nəyə bərabərdir?\n\n```python\n2 + 3 * 4 ** 2 // 5 % 4\n```",
  "`3`",
  ["`0`", "`11`", "`9.6`"]),

 ("A6", "A", "Məntiqi və müqayisə operatorları",
  "`a = 5` və `b = 10` olduqda aşağıdakı ifadənin qiyməti nədir?\n\n```python\nnot (a > 3 and b < 10) or a == b\n```",
  "`True`",
  ["`False`", "`5`", "Xəta, çünki `not` mötərizədən əvvəl yazıla bilməz"]),

 ("A7", "A", "Truthy və falsy dəyərlər",
  "Hansı siyahıda **yalnız** şərt daxilində `False` kimi qiymətləndirilən (falsy) dəyərlər var?",
  "`0`, `0.0`, `''`, `[]`, `{}`, `None`, `False`",
  ["`0`, `'0'`, `[]`, `None`",
   "`False`, `' '` (boşluq simvolu), `()`, `0`",
   "`None`, `[0]`, `0.0`, `''`"]),

 ("A8", "A", "Şərt operatorunun üçlü forması (Ternary)",
  "`parity` dəyişəninə `\"cüt\"` və ya `\"tək\"` yazan **düzgün** üçlü (ternary) şərt ifadəsi hansıdır?",
  "`parity = \"cüt\" if n % 2 == 0 else \"tək\"`",
  ["`parity = n % 2 == 0 ? \"cüt\" : \"tək\"`",
   "`parity = if n % 2 == 0 \"cüt\" else \"tək\"`",
   "`parity = \"cüt\" if n % 2 == 0`"]),

 # ------------------------------------------------------------------ Kateqoriya B
 ("B1", "B", "if-if və if-elif icra fərqi",
  "Bu kod ekrana nə çıxarır?\n\n```python\nx = 15\nif x > 10:\n    print(\"A\")\nif x > 5:\n    print(\"B\")\nelif x > 0:\n    print(\"C\")\nelse:\n    print(\"D\")\n```",
  "`A` və `B` (iki sətirdə) — ayrı-ayrı `if`-lər müstəqil yoxlanılır, `if-elif-else` zəncirində isə yalnız ilk doğru blok icra olunur",
  ["Yalnız `A` — ilk doğru şərtdən sonra qalan bütün `if`-lər buraxılır",
   "`A`, `B` və `C` — `if-elif` zəncirində doğru olan bütün bloklar icra olunur",
   "Yalnız `B` — sonuncu doğru şərt əvvəlkiləri ləğv edir"]),

 ("B2", "B", "İç-içə if və girintilər",
  "Bu kod ekrana nə çıxarır?\n\n```python\nx = 7\nif x > 0:\n    if x % 2 == 0:\n        print(\"müsbət cüt\")\n    else:\n        print(\"müsbət tək\")\nelse:\n    print(\"müsbət deyil\")\n```",
  "`müsbət tək` — daxili `else` daxili `if` ilə eyni girintidədir, ona görə ona aiddir",
  ["`müsbət deyil` — bütün `else`-lər ən xarici `if`-ə aiddir",
   "`müsbət cüt` — iç-içə `if` buraxılır, ona görə onun `else` hissəsi heç vaxt icra olunmur",
   "Heç nə — iç-içə `if` üçün fiqurlu mötərizələr `{ }` lazımdır"]),

 ("B3", "B", "Qısa qapanma qiymətləndirməsi (Short-Circuit)",
  "`x = 0`. Python aşağıdakı şərti qiymətləndirəndə nə baş verir?\n\n```python\nif x != 0 and 10 / x > 1:\n    print(\"böyük\")\n```",
  "Şərt `False` olur və xəta yaranmır: `and` ilk yalan operandda dayanır, ona görə `10 / x` ümumiyyətlə hesablanmır",
  ["`ZeroDivisionError` yaranır, çünki Python `and`-in hər iki tərəfini həmişə hesablayır",
   "Şərt `True` olur, çünki `10 / 0` sonsuzluq kimi qəbul edilir",
   "Python əvvəlcə sağ operandı hesablayır, ona görə nəticə yalnız `10 / x > 1`-dən asılıdır"]),

 ("B4", "B", "pass operatoru",
  "Şərt bloklarında `pass` operatorunun təyinatı nədir?",
  "Heç nə etməyən yer tutucudur: `if` / `else` / `def` sonrakı blok boş ola bilməz, `pass` onu sintaksis xətası olmadan boş saxlamağa imkan verir",
  ["Dövrün cari təkrarının qalan hissəsini buraxır, `continue` kimi",
   "Funksiyadan çıxıb dəyər qaytarır, `return` kimi",
   "Bütün proqramı dərhal dayandırır"]),

 # ------------------------------------------------------------------ Kateqoriya C
 ("C1", "C", "for və while dövrləri, sonsuz dövr",
  "Python-da `for` və `while` dövrləri haqqında hansı ifadə düzgündür?",
  "`for` ardıcıllığın (iterable) elementlərini gəzir, `while` isə şərt `True` olduqca təkrarlanır; şərt heç vaxt `False` olmursa "
  "(məsələn, dövr dəyişəni dövrün içində dəyişdirilmir), `while` sonsuz dövrə çevrilir",
  ["Siyahı üzərində `for` dövrü siyahıda 1000-dən çox element olduqda sonsuz dövrə çevrilir",
   "`while` dövrü həmişə əvvəlcədən məlum olan sabit sayda təkrarlanmalıdır",
   "Python-da sonsuz dövr mümkün deyil, çünki interpretator hər dövrü 1000 təkrardan sonra dayandırır"]),

 ("C2", "C", "break, continue və dövrün else bloku",
  "Bu kod ekrana nə çıxarır?\n\n```python\nfor i in range(1, 6):\n    if i == 2:\n        continue\n    if i == 4:\n        break\n    print(i)\nelse:\n    print(\"bitdi\")\n```",
  "`1` və `3` — `continue` 2-ni buraxır, `break` 4-də dövrü dayandırır, `break` olduğu üçün `else` bloku icra olunmur",
  ["`1`, `3` və `bitdi` — dövrün `else` bloku həmişə icra olunur",
   "`1`, `3`, `5` və `bitdi` — `break` yalnız cari təkrarı dayandırır",
   "`1`, `2` və `3` — `continue` dövrü tamamilə dayandırır"]),

 ("C3", "C", "range(start, stop, step)",
  "Hansı çağırış dəqiq `10, 7, 4, 1` ədədlərini verir?",
  "`range(10, 0, -3)`",
  ["`range(10, 1, -3)`", "`range(1, 10, 3)`", "`range(10, -3)`"]),

 # ------------------------------------------------------------------ Kateqoriya D
 ("D1", "D", "İndeksləmə, mənfi indekslər və dilimləmə",
  "Bu kod ekrana nə çıxarır?\n\n```python\nlst = [10, 20, 30, 40, 50]\nprint(lst[-2], lst[1:4], lst[::2])\n```",
  "`40 [20, 30, 40] [10, 30, 50]`",
  ["`30 [20, 30, 40] [10, 30, 50]`",
   "`40 [20, 30, 40, 50] [10, 30, 50]`",
   "`40 [20, 30, 40] [20, 40]`"]),

 ("D2", "D", "Siyahı metodları (append, insert, remove, pop)",
  "Bu kod ekrana nə çıxarır?\n\n```python\na = [3, 1, 2]\na.append(5)\na.insert(0, 9)\na.remove(1)\nx = a.pop()\nprint(a, x)\n```",
  "`[9, 3, 2] 5`",
  ["`[9, 3, 2, 5] 5`", "`[9, 2, 5] 3`", "`[3, 2, 5] 9`"]),

 ("D3", "D", "İkiölçülü massivlər (matrislər)",
  "`m = [[1, 2, 3], [4, 5, 6]]` matrisi üçün hansı ifadə düzgündür?",
  "`m[1][2]` 6-ya bərabərdir; iç-içə dövrdə xarici dövr sətirləri (`for row in m`), daxili dövr həmin sətrin elementlərini (`for x in row`) gəzir",
  ["`m[2][1]` 6-ya bərabərdir; xarici dövr sütunları, daxili dövr sətirləri gəzir",
   "`m[1][2]` 5-ə bərabərdir, çünki indekslər 1-dən başlayır",
   "Matrisi yalnız bir dövrlə gəzmək olar; iç-içə dövr `TypeError` verir"]),

 # ------------------------------------------------------------------ Kateqoriya E
 ("E1", "E", "Sətirlərin dəyişməzliyi və sətir metodları",
  "Bu kod icra olunanda nə baş verir?\n\n```python\ns = \"salam\"\ns[0] = \"S\"\n```",
  "`TypeError` yaranır — sətirlər dəyişməzdir (immutable); yeni sətir yaratmaq lazımdır, məsələn `s = \"S\" + s[1:]` və ya `s = s.capitalize()`",
  ["`s` dəyişəni `\"Salam\"` olur, çünki sətirlər siyahılar kimi dəyişdirilə bilər",
   "`s` dəyişəni `\"S\"` olur, çünki bütün sətir yeni simvolla əvəz edilir",
   "Heç nə baş vermir — Python bu əmri səssizcə buraxır"]),

 ("E2", "E", "Funksiyalar, return və lokal / qlobal dəyişənlər",
  "Bu kod ekrana nə çıxarır?\n\n```python\nx = 10\ndef f():\n    x = 5\n    return x * 2\ny = f()\nprint(x, y)\n```",
  "`10 10` — funksiyanın içindəki `x` lokal dəyişəndir və qlobal `x`-i dəyişmir; `return` 5 * 2 = 10 qaytarır",
  ["`5 10` — funksiyadakı mənimsətmə qlobal `x`-i dəyişir",
   "`10 20` — funksiya qlobal `x`-dən istifadə edir",
   "Xəta — `global` açar sözü olmadan funksiyada `x` adlı dəyişən yaratmaq olmaz"]),
]


def check_theory_answers():
    """Kodlu sualların düzgün cavablarının yoxlanması (build_bank.py --verify işlədir)."""
    import contextlib
    import io
    x = "7"; y = int(x) + 3
    assert (str(type(x)), y, float(y)) == ("<class 'str'>", 10, 10.0)
    assert 2 + 3 * 4 ** 2 // 5 % 4 == 3
    a, b = 5, 10
    assert (not (a > 3 and b < 10) or a == b) is True
    assert not any([0, 0.0, '', [], {}, None, False])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        x = 15
        if x > 10:
            print("A")
        if x > 5:
            print("B")
        elif x > 0:
            print("C")
        for i in range(1, 6):
            if i == 2:
                continue
            if i == 4:
                break
            print(i)
        else:
            print("bitdi")
    assert out.getvalue().split() == ["A", "B", "1", "3"]
    assert list(range(10, 0, -3)) == [10, 7, 4, 1] and list(range(10, 1, -3)) != [10, 7, 4, 1]
    lst = [10, 20, 30, 40, 50]
    assert (lst[-2], lst[1:4], lst[::2]) == (40, [20, 30, 40], [10, 30, 50])
    a = [3, 1, 2]; a.append(5); a.insert(0, 9); a.remove(1); x = a.pop()
    assert (a, x) == ([9, 3, 2], 5)
    m = [[1, 2, 3], [4, 5, 6]]
    assert m[1][2] == 6
    try:
        s = "salam"; s[0] = "S"
        raise AssertionError
    except TypeError:
        pass
    assert len(THEORY) == 20 and len({t[0] for t in THEORY}) == 20
    return True
