// AVTOMATİK YARADILIB: python tools/build_bank.py — əl ilə redaktə etməyin.
window.EXAM_DATA = {
 "version": 4,
 "harness": "\nimport ast\nimport builtins\nimport contextlib\nimport copy\nimport hashlib\nimport io\nimport json\nimport math\nimport re\nimport sys\nimport time\nimport types\n\n# Yalnız imtahan səhifəsinə mane ola biləcək modullar bloklanır; digər standart modullar sərbəstdir\n_BLOCKED_MODULES = (\"js\", \"pyodide\", \"pyodide_js\", \"_pyodide\", \"micropip\", \"subprocess\", \"socket\")\n_real_import = builtins.__import__\n\n\ndef _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):\n    if name.split(\".\")[0] in _BLOCKED_MODULES:\n        raise ImportError(f\"'{name}' modulu imtahanda istifadə edilə bilməz\")\n    return _real_import(name, globals, locals, fromlist, level)\n\n\nclass InputNotNeeded(Exception):\n    pass\n\n\ndef _no_input(prompt=\"\"):\n    raise InputNotNeeded(\"Bu imtahanda input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür \"\n                         \"(məs. reqemler_cemi(384)). input() əvəzinə funksiyanın parametrlərindən istifadə edin.\")\n\n\ndef _h(x):\n    return hashlib.sha256(str(x).strip().lower().encode()).hexdigest()\n\n\ndef _plain(v):\n    \"\"\"tuple / set kimi dəyərləri adi Python siyahısına çevirir (tolerant müqayisə üçün).\"\"\"\n    if hasattr(v, \"tolist\"):\n        v = v.tolist()\n    if isinstance(v, (set, frozenset)):\n        try:\n            v = sorted(v)\n        except TypeError:\n            v = list(v)\n    if isinstance(v, (list, tuple)):\n        return [_plain(x) for x in v]\n    if isinstance(v, dict):\n        return {k: _plain(x) for k, x in v.items()}\n    return v\n\n\ndef _close(a, b):\n    \"\"\"Ədəd müqayisəsi: 5 == 5.0; kəsr ədədlər kiçik yuvarlaqlaşdırma fərqi ilə bərabər sayılır (məs. 1.41 və 1.41421).\"\"\"\n    if isinstance(a, bool) or isinstance(b, bool):\n        return a == b\n    try:\n        if math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-9):\n            return True\n        if isinstance(b, float) and not float(b).is_integer():\n            return abs(a - b) <= 0.006\n        return False\n    except TypeError:\n        return False\n\n\ndef _eq(a, b):\n    \"\"\"Tolerant bərabərlik: list ≈ tuple, 1.0 ≈ 1, kiçik yuvarlaqlaşdırma fərqi qəbul olunur.\"\"\"\n    a, b = _plain(a), _plain(b)\n    if isinstance(a, list) and isinstance(b, list):\n        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))\n    if isinstance(a, dict) and isinstance(b, dict):\n        return a.keys() == b.keys() and all(_eq(a[k], b[k]) for k in a)\n    if isinstance(a, (int, float)) and isinstance(b, (int, float)):\n        return _close(a, b)\n    return a == b\n\n\n_NUM_RE = re.compile(r\"-?\\d+(?:\\.\\d+)?\")\n\n\ndef _nums(text):\n    \"\"\"Mətndəki bütün ədədlər, məs. 'ƏBOB: 6, ƏKOB: 36' -> [6, 36].\"\"\"\n    return [float(m) if \".\" in m else int(m) for m in _NUM_RE.findall(str(text))]\n\n\ndef _call(fn, *args):\n    \"\"\"\n    Tələbənin funksiyasını arqumentlərin surəti ilə çağırır.\n    Qaytarılan dəyər götürülür; funksiya heç nə qaytarmırsa, ekrana çıxardığı mətn götürülür;\n    yalnız siyahı arqumentini yerində dəyişibsə (məs. çeşidləmə), həmin siyahı götürülür.\n    \"\"\"\n    args = copy.deepcopy(args)\n    before = copy.deepcopy(args)\n    buf = io.StringIO()\n    with contextlib.redirect_stdout(buf):\n        result = fn(*args)\n    printed = buf.getvalue()\n    if printed:\n        sys.stdout.write(printed)\n    if result is None:\n        if printed.strip():\n            return printed.strip()\n        for now, was in zip(args, before):\n            if isinstance(now, list) and now != was:\n                return now\n    return result\n\n\n# Bəli / xeyr sözləri (azərbaycanca və ingiliscə). İnkar: deyil, yox, mürəkkəb, -mır/-mir/-mur/-mür (gətirmir, bölünmür) ...\n_NO = re.compile(r\"\\b(not|no|non|isn'?t|aren'?t|doesn'?t|does not|cannot|can'?t|invalid|composite|common|false|\"\n                 r\"deyil|deyildir|yox|xeyr|mürəkkəb|adi|yanlış|səhv)\\b|\\w+m[ıiuü]r\\b\")\n_YES = re.compile(r\"\\b(yes|true|prime|leap|valid|palindrome|forms?|triangle|divisible|\"\n                  r\"bəli|hə|doğru|düzgün|sadə|uyğun|palindrom|polindrom|üçbucaq|uzun|bölünür|gətirir)|\"\n                  r\"(dır|dir|dur|dür)\\b\")\n\n\ndef _yes(v):\n    \"\"\"Bəli-xeyr cavabından True / False: True, 1, 'Sadə ədəddir', 'Polindrom deyil', 'Uzun ildir' ...\"\"\"\n    if isinstance(v, bool):\n        return v\n    if isinstance(v, int) and v in (0, 1):\n        return bool(v)\n    if isinstance(v, str):\n        t = v.casefold()\n        if _NO.search(t):\n            return False\n        if _YES.search(t):\n            return True\n    return None\n\n\ndef _clean_text(s):\n    return \" \".join(str(s).strip().strip(\"'\\\"\").split())\n\n\ndef _same(got, exp):\n    \"\"\"Tələbənin cavabı (qaytarılan və ya çap olunan) gözlənilən dəyərə bərabərdirmi? Formata tolerantdır.\"\"\"\n    if isinstance(exp, bool):\n        return _yes(got) is exp\n    if got is None:\n        return False\n    if isinstance(exp, str):\n        g, e = _clean_text(got), _clean_text(exp)\n        if g == e:\n            return True\n        # cavabdan əvvəl izah ola bilər: \"Ən uzun söz: 'Proqramlaşdırma'\"\n        g = g.rstrip(\".!\").strip(\"'\\\"\")\n        return g == e or (g.endswith(e) and g[-len(e) - 1] in \" :='\\\"-\")\n    if isinstance(got, str):\n        text = got.strip()\n        try:\n            if _eq(ast.literal_eval(text), exp):\n                return True\n        except Exception:\n            pass\n        if isinstance(exp, dict):\n            m = re.search(r\"\\{.*\\}\", text, re.S)\n            if m:\n                try:\n                    return _eq(ast.literal_eval(m.group(0)), exp)\n                except Exception:\n                    return False\n            return False\n        if isinstance(exp, (list, tuple)) and exp and all(isinstance(x, (int, float)) for x in exp):\n            m = re.search(r\"\\[.*\\]|\\(.*\\)\", text, re.S)\n            if m:\n                try:\n                    if _eq(ast.literal_eval(m.group(0)), exp):\n                        return True\n                except Exception:\n                    pass\n            after_label = [float(x) if \".\" in x else int(x) for x in re.findall(r\"[:=]\\s*(-?\\d+(?:\\.\\d+)?)\", text)]\n            if after_label and _eq(after_label, list(exp)):\n                return True       # \"Sətir 1 cəmi: 6, Sətir 2 cəmi: 15\" -> [6, 15]\n            ns = _nums(text)\n            return len(ns) >= len(exp) and _eq(ns[len(ns) - len(exp):], list(exp))\n        if isinstance(exp, (list, tuple)) and not exp:\n            return text in (\"[]\", \"()\", \"\")\n        if isinstance(exp, (int, float)):\n            ns = _nums(text)\n            after_label = [float(x) if \".\" in x else int(x) for x in re.findall(r\"[:=]\\s*(-?\\d+(?:\\.\\d+)?)\", text)]\n            return any(_close(x, exp) for x in ns[-1:] + after_label)\n        return False\n    if isinstance(exp, (int, float)) and isinstance(got, (list, tuple)) and len(got) == 1:\n        got = got[0]\n    return _eq(got, exp)\n\n\ndef _seq(got, n):\n    \"\"\"Cavab n dəyərdən ibarət siyahı kimi (tuple/list-dən və ya çap olunan mətnin son n ədədindən).\"\"\"\n    if isinstance(got, str):\n        ns = _nums(got)\n        return ns[len(ns) - n:] if len(ns) >= n else None\n    v = _plain(got)\n    return v if isinstance(v, list) and len(v) == n else None\n\n\ndef _lines(got):\n    \"\"\"Mətn naxışı sətirlər siyahısı kimi (sondakı boşluqlar və boş sətirlər nəzərə alınmır).\"\"\"\n    if got is None:\n        return []\n    if isinstance(got, (list, tuple)):\n        rows = [str(x) for x in got]\n    else:\n        rows = str(got).split(\"\\n\")\n    return [r.rstrip() for r in rows if r.strip()]\n\n\n\ndef _flat(got):\n    \"\"\"Cavabdakı bütün ədədlər düz siyahı kimi (iç-içə siyahılar açılır, mətndən ədədlər götürülür).\"\"\"\n    if got is None:\n        return []\n    if isinstance(got, str):\n        return _nums(got)\n    v = _plain(got)\n    if isinstance(v, list):\n        out = []\n        for x in v:\n            out += _flat(x) if isinstance(x, (list, tuple, str)) else [x]\n        return out\n    return [v]\n\n\ndef _same_set(got, exp):\n    \"\"\"Sıradan asılı olmayan müqayisə (məs. iki siyahının kəsişməsi): elementlər eyni olmalıdır.\"\"\"\n    if got is None:\n        return False\n    return sorted(_flat(got)) == sorted(exp)\n\n\ndef _has_word(got, *words):\n    \"\"\"Cavab mətnində sözlərdən biri varmı (kiçik/böyük hərf fərqi nəzərə alınmır).\"\"\"\n    if got is None:\n        return False\n    t = str(got).casefold()\n    return any(re.search(r\"(?<!\\w)\" + re.escape(w.casefold()), t) for w in words)\n\n\nOK_MSG = \"✅ Tapşırıq {t}: DÜZGÜNDÜR (+{p} bal)\"\nPARTIAL_MSG = \"🟡 Tapşırıq {t}: QİSMƏN DÜZGÜNDÜR (+{p} / {m} bal)\"\nFAIL_MSG = \"❌ Tapşırıq {t}: XƏTA — qaytarılan / çap olunan nəticə gözlənilən nəticəyə uyğun deyil!\"\n\n\ndef grade(*items):\n    \"\"\"\n    Qismən bal üçün: items = (çəki, \"yoxlanılan hissə\", çağırıla bilən) ...\n    Hər hissə ayrıca yoxlanılır; ödənən hissələrin çəkisi toplanır.\n    Qaytarır: (qazanılan_çəki, ümumi_çəki, [ödənməyən hissələrin təsviri]).\n    \"\"\"\n    got = tot = 0\n    failed = []\n    for w, label, fn in items:\n        tot += w\n        try:\n            r = fn()\n            if r is None or (isinstance(r, bool) and not r):\n                raise AssertionError\n            got += w\n        except AssertionError:\n            failed.append(label)\n        except Exception as e:\n            failed.append(f\"{label} ({type(e).__name__}: {e})\")\n    return (got, tot, failed)\n\n\ndef _exec_limited(code, ns, budget, out):\n    \"\"\"Kodu vaxt limiti ilə icra edir (sonsuz dövr brauzeri dondurmasın).\"\"\"\n    deadline = time.monotonic() + budget\n\n    def tracer(frame, event, arg):\n        if time.monotonic() > deadline:\n            raise TimeoutError(f\"icra {budget:g} saniyədən çox çəkdi (sonsuz dövr ola bilər)\")\n        return tracer\n\n    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):\n        sys.settrace(tracer)\n        try:\n            exec(compile(code, \"<code>\", \"exec\"), ns)\n        finally:\n            sys.settrace(None)\n\n\n_QUOTES = {\"“\": '\"', \"”\": '\"', \"„\": '\"', \"‘\": \"'\", \"’\": \"'\", \" \": \" \", \" \": \" \",\n           \"​\": \"\", \"‌\": \"\", \"‍\": \"\", \"﻿\": \"\", \"–\": \"-\", \"−\": \"-\"}\n\n\ndef normalize_code(code):\n    \"\"\"\n    Kodu tolerant şəkildə qəbul edir:\n    CRLF, sətir başındakı Tab (4 boşluq), görünməz/qeyri-standart simvollar (NBSP, sıfır enli boşluq), \"ağıllı\" dırnaqlar,\n    ümumi artıq girinti (kod xanası içəridən kopyalananda) və Jupyter sehrli sətirləri (%magic, !əmr) düzəldilir.\n    \"\"\"\n    import textwrap\n    code = str(code).replace(\"\\r\\n\", \"\\n\").replace(\"\\r\", \"\\n\")\n    code = \"\".join(_QUOTES.get(c, c) for c in code)\n    lines = []\n    for ln in code.split(\"\\n\"):\n        stripped = ln.lstrip(\" \\t\")\n        lead = ln[:len(ln) - len(stripped)].replace(\"\\t\", \"    \")\n        if stripped.startswith((\"%\", \"!\")) and not stripped.startswith(\"!=\"):\n            continue                      # Jupyter: %matplotlib inline, !pip install ...\n        lines.append((lead + stripped).rstrip())\n    return textwrap.dedent(\"\\n\".join(lines)).strip(\"\\n\") + \"\\n\"\n\n\ndef _describe(exc):\n    if \"'___'\" in str(exc):\n        return \"`___` boşluqları hələ doldurulmayıb\"\n    if isinstance(exc, InputNotNeeded):\n        return str(exc)\n    if isinstance(exc, IndentationError):\n        return f\"Girinti xətası (sətir {exc.lineno}): {exc.msg}. Blokun (':' işarəsindən sonra) içindəki sətirlərə 4 boşluq girinti qoyun.\"\n    if isinstance(exc, SyntaxError):\n        return f\"Sintaksis xətası (sətir {exc.lineno}): {exc.msg}\"\n    return f\"{type(exc).__name__}: {exc}\"\n\n\ndef _coerce(value):\n    if value is None:\n        return None\n    s = str(value).strip()\n    if s == \"\":\n        return None\n    if re.fullmatch(r\"[+-]?\\d+\", s):\n        return int(s)\n    return s\n\n\ndef run_variant(steps, answers, upto=None, budget=10.0):\n    \"\"\"\n    steps   : exam_data.js-dəki addımlar (tapşırıq ardıcıllığı ilə)\n    answers : {\"T1\": \"<kod>\", \"T2\": \"b\", ...}\n    upto    : yalnız bu tapşırığın testinə qədər icra et (\"Kodu yoxla\" düyməsi üçün)\n    Nəticə  : {\"results\": {id: {ok, pts, max, msg, detail}}, \"output\": {id: stdout}}\n    \"\"\"\n    answers = answers or {}\n    ns = {\n        \"__name__\": \"__main__\",\n        \"__builtins__\": dict(vars(builtins), __import__=_guarded_import, input=_no_input),\n        \"math\": math, \"hashlib\": hashlib, \"_h\": _h, \"_eq\": _eq, \"grade\": grade,\n        \"_call\": _call, \"_same\": _same, \"_yes\": _yes, \"_seq\": _seq, \"_lines\": _lines, \"_nums\": _nums,\n        \"_flat\": _flat, \"_same_set\": _same_set, \"_has_word\": _has_word,\n    }\n    errors, results, output = {}, {}, {}\n\n    def check(task_id, points, test):\n        t = task_id.split(\"_\")[0]\n        try:\n            res = test()\n            if isinstance(res, tuple) and len(res) == 3:\n                got, tot, failed = res\n                pts = int(points * got / tot + 0.5) if tot else 0\n                if pts >= points:\n                    results[t] = {\"ok\": True, \"pts\": points, \"max\": points, \"partial\": False,\n                                  \"msg\": OK_MSG.format(t=t, p=points), \"detail\": \"\"}\n                    return\n                detail = \"Ödənməyən hissələr: \" + \"; \".join(failed)\n                if pts > 0:\n                    results[t] = {\"ok\": False, \"pts\": pts, \"max\": points, \"partial\": True,\n                                  \"msg\": PARTIAL_MSG.format(t=t, p=pts, m=points), \"detail\": detail}\n                    return\n                if t in errors:\n                    detail = errors[t] if errors[t].startswith(\"`\") else \"kodunuz icra olunarkən xəta baş verdi → \" + errors[t]\n                results[t] = {\"ok\": False, \"pts\": 0, \"max\": points, \"partial\": False,\n                              \"msg\": FAIL_MSG.format(t=t), \"detail\": detail}\n                return\n            results[t] = {\"ok\": True, \"pts\": points, \"max\": points, \"partial\": False,\n                          \"msg\": OK_MSG.format(t=t, p=points), \"detail\": \"\"}\n            return\n        except AssertionError as e:\n            detail = str(e) or \"test şərti ödənmədi\"\n        except NameError as e:\n            detail = f\"tələb olunan funksiya / dəyişən təyin edilməyib ({e})\"\n        except BaseException as e:\n            detail = _describe(e)\n        if t in errors:\n            detail = errors[t] if errors[t].startswith(\"`\") else \"kodunuz icra olunarkən xəta baş verdi → \" + errors[t]\n        results[t] = {\"ok\": False, \"pts\": 0, \"max\": points, \"partial\": False,\n                      \"msg\": FAIL_MSG.format(t=t), \"detail\": detail}\n\n    ns[\"check\"] = check\n\n    for st in steps:\n        kind = st[\"k\"]\n        if kind == \"var\":\n            ns[st[\"var\"]] = _coerce(answers.get(st[\"task\"]))\n            continue\n        label = st.get(\"task\")\n        code = st[\"code\"]\n        expected_fns = re.findall(r\"^\\s*def\\s+([A-Za-z_]\\w*)\", st[\"code\"], re.M) if kind == \"code\" else []\n        if kind == \"code\":\n            for name in expected_fns:          # əvvəlki tapşırığın eyniadlı funksiyası burada istifadə olunmasın\n                ns.pop(name, None)\n        if kind == \"code\" and label in answers and answers[label] is not None:\n            code = normalize_code(answers[label])\n        before = {k: id(v) for k, v in ns.items()}\n        out = io.StringIO()\n        try:\n            _exec_limited(code, ns, budget, out)\n        except BaseException as e:\n            if label:\n                errors[label] = _describe(e)\n        if kind == \"code\" and expected_fns:\n            # Tələbə funksiyanın adını dəyişibsə: yalnız bir yeni funksiya yazılıbsa, o götürülür\n            new_fns = [v for k, v in ns.items()\n                       if isinstance(v, types.FunctionType) and before.get(k) != id(v) and not k.startswith(\"_\")]\n            for name in expected_fns:\n                if name not in ns and len(new_fns) == 1 and len(expected_fns) == 1:\n                    ns[name] = new_fns[0]\n        if label:\n            output[label] = out.getvalue()[-2000:]\n        elif kind == \"test\" and out.getvalue():\n            # test zamanı tələbə funksiyasının çap etdikləri\n            output[st[\"ids\"][0]] = (output.get(st[\"ids\"][0], \"\") + out.getvalue())[-2000:]\n        if kind == \"test\" and upto and upto in st[\"ids\"]:\n            break\n\n    if upto:\n        results = {k: v for k, v in results.items() if k == upto}\n        output = {k: v for k, v in output.items() if k == upto}\n    return {\"results\": results, \"output\": output}\n\n\ndef run_json(payload):\n    \"\"\"Pyodide körpüsü: JSON mətn daxil olur, JSON mətn qayıdır.\"\"\"\n    p = json.loads(payload)\n    return json.dumps(run_variant(p[\"steps\"], p.get(\"answers\"), p.get(\"upto\"), p.get(\"budget\", 10.0)),\n                      ensure_ascii=False)\n",
 "variants": {
  "A": {
   "name": "Variant A",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. pass operatoru (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T1. pass operatoru (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — B. Şərt Operatorları və Budaqlanan Alqoritmlər · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Şərt bloklarında <code>pass</code> operatorunun təyinatı nədir?</p>",
     "options": {
      "a": "Dövrün cari təkrarının qalan hissəsini buraxır, <code>continue</code> kimi",
      "b": "Bütün proqramı dərhal dayandırır",
      "c": "Heç nə etməyən yer tutucudur: <code>if</code> / <code>else</code> / <code>def</code> sonrakı blok boş ola bilməz, <code>pass</code> onu sintaksis xətası olmadan boş saxlamağa imkan verir",
      "d": "Funksiyadan çıxıb dəyər qaytarır, <code>return</code> kimi"
     }
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Selsidən Farenheytə çevirmə (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Selsidən Farenheytə çevirmə (10 bal)</h4>\n<p><i>Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>Temperaturu Selsidən (Celsius) Farenheytə (Fahrenheit) çevirən <code>selsi_farenheyt(c)</code> funksiyasını yazın: <b>F = C · 1.8 + 32</b>.</p>\n<p>Nümunə: <code>selsi_farenheyt(25)</code> → <code>77.0</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def selsi_farenheyt(c):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. İkiölçülü massivlər (matrislər) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T3. İkiölçülü massivlər (matrislər) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — D. Birölçülü və İkiölçülü Massivlər / Siyahılar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p><code>m = [[1, 2, 3], [4, 5, 6]]</code> matrisi üçün hansı ifadə düzgündür?</p>",
     "options": {
      "a": "Matrisi yalnız bir dövrlə gəzmək olar; iç-içə dövr <code>TypeError</code> verir",
      "b": "<code>m[2][1]</code> 6-ya bərabərdir; xarici dövr sütunları, daxili dövr sətirləri gəzir",
      "c": "<code>m[1][2]</code> 5-ə bərabərdir, çünki indekslər 1-dən başlayır",
      "d": "<code>m[1][2]</code> 6-ya bərabərdir; iç-içə dövrdə xarici dövr sətirləri (<code>for row in m</code>), daxili dövr həmin sətrin elementlərini (<code>for x in row</code>) gəzir"
     }
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Düzbucaqlının sahəsi və perimetri (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. Düzbucaqlının sahəsi və perimetri (10 bal)</h4>\n<p><i>Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Düzbucaqlının eni və uzunluğuna görə onun <b>sahəsini</b> və <b>perimetrini</b> hesablayan <code>duzbucaqli(en, uzunluq)</code> funksiyasını yazın.<br>Funksiya iki qiymət qaytarsın: <code>sahe, perimetr</code>.</p>\n<p>Nümunə: <code>duzbucaqli(5, 10)</code> → <code>(50, 30)</code>  (Sahə: 50, Perimetr: 30)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def duzbucaqli(en, uzunluq):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. X ədədinin təkrar sayı və ilk indeksi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T5. X ədədinin təkrar sayı və ilk indeksi (10 bal)</h4>\n<p><i>Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Siyahıda verilmiş X ədədinin <b>neçə dəfə təkrarlandığını</b> və <b>ilk rast gəlindiyi indeksi</b> tapan <code>tekrar_ve_indeks(lst, x)</code><br>funksiyasını yazın. Funksiya iki qiymət qaytarsın: <code>say, ilk_indeks</code>.</p>\n<p>Nümunə: <code>tekrar_ve_indeks([5, 3, 5, 2, 5, 8], 5)</code> → <code>(3, 0)</code>  (Təkrar sayı: 3, İlk indeks: 0)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def tekrar_ve_indeks(lst, x):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Stack və Heap yaddaş sahələri (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T6. Stack və Heap yaddaş sahələri (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Python-un yaddaş modelində <b>Stack</b> və <b>Heap</b> sahələrinin rolu haqqında hansı ifadə düzgündür?</p>",
     "options": {
      "a": "Python-da Heap yaddaşını proqramçı free() funksiyası ilə əl ilə boşaltmalıdır, əks halda proqram dayanır",
      "b": "Heap yalnız qlobal dəyişənlər, Stack isə yalnız sətirlər (str) üçün istifadə olunur",
      "c": "Stack funksiya çağırışlarının çərçivələrini və lokal adları (istinadları) saxlayır və funksiya bitəndə avtomatik boşalır; Heap obyektlərin özlərini (int, str, list …) saxlayır və onlara istinad qalmayanda istinad sayğacı / zibil toplayıcı (garbage collector) onları silir",
      "d": "Bütün obyektlər, o cümlədən siyahılar, Stack-də saxlanılır və hər mənimsətmədə yeni dəyişənə tam surəti çıxarılır"
     }
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. ƏBOB və ƏKOB (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T7. ƏBOB və ƏKOB (10 bal)</h4>\n<p><i>Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While) · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>İki natural ədədin <b>ƏBOB</b>-unu (ən böyük ortaq bölən) və <b>ƏKOB</b>-unu (ən kiçik ortaq bölünən) hesablayan<br><code>ebob_ekob(a, b)</code> funksiyasını yazın. Funksiya iki qiymət qaytarsın: <code>ebob, ekob</code>.</p>\n<p>Nümunə: <code>ebob_ekob(12, 18)</code> → <code>(6, 36)</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def ebob_ekob(a, b):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. İndeksləmə, mənfi indekslər və dilimləmə (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T8. İndeksləmə, mənfi indekslər və dilimləmə (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — D. Birölçülü və İkiölçülü Massivlər / Siyahılar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>lst = [10, 20, 30, 40, 50]\nprint(lst[-2], lst[1:4], lst[::2])</code></pre>",
     "options": {
      "a": "<code>40 [20, 30, 40] [20, 40]</code>",
      "b": "<code>40 [20, 30, 40] [10, 30, 50]</code>",
      "c": "<code>30 [20, 30, 40] [10, 30, 50]</code>",
      "d": "<code>40 [20, 30, 40, 50] [10, 30, 50]</code>"
     }
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Həm 3-ə, həm də 5-ə bölünmə (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. Həm 3-ə, həm də 5-ə bölünmə (10 bal)</h4>\n<p><i>Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>Ədədin <b>həm 3-ə, həm də 5-ə</b> qalıqsız bölünüb-bölünmədiyini şərt operatoru ilə yoxlayan <code>uc_ve_bese_bolunur(n)</code><br>funksiyasını yazın. Funksiya <code>True</code> / <code>False</code> qaytarsın (və ya <code>\"Ədəd həm 3-ə, həm də 5-ə bölünür\"</code> / <code>\"Bölünmür\"</code> çap etsin).</p>\n<p>Nümunə: <code>uc_ve_bese_bolunur(15)</code> → <code>True</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def uc_ve_bese_bolunur(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. Rekursiv faktorial (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T10. Rekursiv faktorial (10 bal)</h4>\n<p><i>Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>Ədədin faktorialını hesablayan <b>rekursiv</b> funksiya <code>factorial_recursive(n)</code> yazın (funksiya özünü çağırır; 0! = 1).</p>\n<p>Nümunə: <code>factorial_recursive(5)</code> → <code>120</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def factorial_recursive(n):\n    # kodunuzu bura yazın\n    pass"
    }
   ],
   "steps": [
    {
     "k": "var",
     "task": "T1",
     "var": "cavab_T1"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    assert _h(cavab_T1) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def selsi_farenheyt(c):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    assert _same(_call(selsi_farenheyt, 25), 77.0), \"selsi_farenheyt(25) 77.0 olmalıdır\"\n    assert _same(_call(selsi_farenheyt, 0), 32.0), \"selsi_farenheyt(0) 32.0 olmalıdır\"\n    assert _same(_call(selsi_farenheyt, -40), -40.0), \"selsi_farenheyt(-40) -40.0 olmalıdır\"\n    assert _same(_call(selsi_farenheyt, 36.6), 97.88), \"selsi_farenheyt(36.6) 97.88 olmalıdır\"\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "var",
     "task": "T3",
     "var": "cavab_T3"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    assert _h(cavab_T3) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def duzbucaqli(en, uzunluq):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    cases = [((5, 10), (50, 30)), ((3, 3), (9, 12)), ((2.5, 4), (10.0, 13.0))]\n    res = [_seq(_call(duzbucaqli, *a), 2) for a, _ in cases]\n    return grade(\n        (5, \"sahə (en × uzunluq)\", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),\n        (5, \"perimetr (2 × (en + uzunluq))\", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),\n    )\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "code",
     "task": "T5",
     "code": "def tekrar_ve_indeks(lst, x):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    cases = [(([5, 3, 5, 2, 5, 8], 5), (3, 0)), (([1, 2, 3, 2, 2], 2), (3, 1)), (([4, 6, 9], 9), (1, 2))]\n    res = [_seq(_call(tekrar_ve_indeks, *a), 2) for a, _ in cases]\n    return grade(\n        (5, \"təkrar sayı\", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),\n        (5, \"ilk indeks\", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),\n    )\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "var",
     "task": "T6",
     "var": "cavab_T6"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    assert _h(cavab_T6) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "code",
     "task": "T7",
     "code": "def ebob_ekob(a, b):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    cases = [((12, 18), (6, 36)), ((7, 13), (1, 91)), ((20, 5), (5, 20)), ((21, 6), (3, 42))]\n    res = [_seq(_call(ebob_ekob, *a), 2) for a, _ in cases]\n    return grade(\n        (5, \"ƏBOB\", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),\n        (5, \"ƏKOB\", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),\n    )\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "var",
     "task": "T8",
     "var": "cavab_T8"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _h(cavab_T8) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def uc_ve_bese_bolunur(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    assert _same(_call(uc_ve_bese_bolunur, 15), True), \"15 həm 3-ə, həm də 5-ə bölünür\"\n    assert _same(_call(uc_ve_bese_bolunur, 45), True), \"45 həm 3-ə, həm də 5-ə bölünür\"\n    assert _same(_call(uc_ve_bese_bolunur, 9), False), \"9 yalnız 3-ə bölünür\"\n    assert _same(_call(uc_ve_bese_bolunur, 10), False), \"10 yalnız 5-ə bölünür\"\n    assert _same(_call(uc_ve_bese_bolunur, 7), False), \"7 heç birinə bölünmür\"\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "code",
     "task": "T10",
     "code": "def factorial_recursive(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _same(_call(factorial_recursive, 5), 120), \"factorial_recursive(5) 120 olmalıdır\"\n    assert _same(_call(factorial_recursive, 1), 1), \"factorial_recursive(1) 1 olmalıdır\"\n    assert _same(_call(factorial_recursive, 0), 1), \"factorial_recursive(0) 1 olmalıdır\"\n    assert _same(_call(factorial_recursive, 10), 3628800), \"factorial_recursive(10) 3628800 olmalıdır\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "B": {
   "name": "Variant B",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. İki nöqtə arasındakı məsafə (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T1. İki nöqtə arasındakı məsafə (10 bal)</h4>\n<p><i>Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>Müstəvidə (x1, y1) və (x2, y2) nöqtələri arasındakı məsafəni hesablayan <code>mesafe(x1, y1, x2, y2)</code> funksiyasını yazın:</p>\n<p>d = √((x2 − x1)² + (y2 − y1)²)</p>\n<p>Nümunə: <code>mesafe(0, 0, 3, 4)</code> → <code>5.0</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def mesafe(x1, y1, x2, y2):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Sait və samit hərflərin sayı (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Sait və samit hərflərin sayı (10 bal)</h4>\n<p><i>Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Mətndəki <b>sait</b> və <b>samit</b> hərflərin sayını ayrı-ayrılıqda hesablayan <code>sait_samit(metn)</code> funksiyasını yazın.<br>Saitlər: <b>a, ı, o, u, e, ə, i, ö, ü</b> (böyük hərflər də). Hərf olmayan simvollar (boşluq, rəqəm, işarə) sayılmır.<br>Funksiya iki qiymət qaytarsın: <code>sait_sayi, samit_sayi</code>.</p>\n<p>Nümunə: <code>sait_samit(\"Salam Baku\")</code> → <code>(4, 5)</code>  (Sait sayı: 4, Samit sayı: 5)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def sait_samit(metn):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. if-if və if-elif icra fərqi (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T3. if-if və if-elif icra fərqi (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — B. Şərt Operatorları və Budaqlanan Alqoritmlər · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>x = 15\nif x &gt; 10:\n    print(\"A\")\nif x &gt; 5:\n    print(\"B\")\nelif x &gt; 0:\n    print(\"C\")\nelse:\n    print(\"D\")</code></pre>",
     "options": {
      "a": "Yalnız <code>B</code> — sonuncu doğru şərt əvvəlkiləri ləğv edir",
      "b": "Yalnız <code>A</code> — ilk doğru şərtdən sonra qalan bütün <code>if</code>-lər buraxılır",
      "c": "<code>A</code>, <code>B</code> və <code>C</code> — <code>if-elif</code> zəncirində doğru olan bütün bloklar icra olunur",
      "d": "<code>A</code> və <code>B</code> (iki sətirdə) — ayrı-ayrı <code>if</code>-lər müstəqil yoxlanılır, <code>if-elif-else</code> zəncirində isə yalnız ilk doğru blok icra olunur"
     }
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. 0 daxil edilənə qədər cəm və ədədi orta (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. 0 daxil edilənə qədər cəm və ədədi orta (10 bal)</h4>\n<p><i>Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While) · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Ədədlər siyahı şəklində verilir; istifadəçi <b>0 daxil edənə qədər</b> olan ədədlərin <b>cəmini</b> və <b>ədədi ortasını</b> hesablayan<br><code>cem_orta(ededler)</code> funksiyasını yazın (0 və ondan sonrakı ədədlər nəzərə alınmır). Funksiya iki qiymət qaytarsın: <code>cem, orta</code>.</p>\n<p>Nümunə: <code>cem_orta([5, 10, 15, 0])</code> → <code>(30, 10.0)</code>  (Cəm: 30, Ədədi orta: 10.0)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def cem_orta(ededler):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Əsas məlumat tipləri, type() və tip çevrilməsi (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T5. Əsas məlumat tipləri, type() və tip çevrilməsi (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>x = \"7\"\ny = int(x) + 3\nprint(type(x), y, float(y))</code></pre>",
     "options": {
      "a": "<code>&lt;class 'str'&gt; 73 73.0</code>",
      "b": "<code>&lt;class 'int'&gt; 10 10.0</code>",
      "c": "<code>&lt;class 'str'&gt; 10 10.0</code>",
      "d": "<code>&lt;class 'str'&gt; 10 10</code>"
     }
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Nöqtənin koordinat rübü (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T6. Nöqtənin koordinat rübü (10 bal)</h4>\n<p><i>Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>(x, y) nöqtəsinin hansı <b>koordinat rübündə</b> (I, II, III, IV rüb) və ya <b>oxlar üzərində</b> olduğunu təyin edən<br><code>rub(x, y)</code> funksiyasını yazın. Mümkün cavablar: <code>\"I rüb\"</code>, <code>\"II rüb\"</code>, <code>\"III rüb\"</code>, <code>\"IV rüb\"</code>, <code>\"OX oxu\"</code>, <code>\"OY oxu\"</code>,<br><code>\"Koordinat başlanğıcı\"</code>. (<code>\"II\"</code>, <code>2</code> və ya <code>\"2-ci rüb\"</code> kimi cavablar da qəbul olunur.)</p>\n<p>Nümunə: <code>rub(-3, 5)</code> → <code>\"II rüb\"</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def rub(x, y):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. for və while dövrləri, sonsuz dövr (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T7. for və while dövrləri, sonsuz dövr (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — C. Dövr Operatorları və İterasiya (For, While) · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Python-da <code>for</code> və <code>while</code> dövrləri haqqında hansı ifadə düzgündür?</p>",
     "options": {
      "a": "Python-da sonsuz dövr mümkün deyil, çünki interpretator hər dövrü 1000 təkrardan sonra dayandırır",
      "b": "Siyahı üzərində <code>for</code> dövrü siyahıda 1000-dən çox element olduqda sonsuz dövrə çevrilir",
      "c": "<code>for</code> ardıcıllığın (iterable) elementlərini gəzir, <code>while</code> isə şərt <code>True</code> olduqca təkrarlanır; şərt heç vaxt <code>False</code> olmursa (məsələn, dövr dəyişəni dövrün içində dəyişdirilmir), <code>while</code> sonsuz dövrə çevrilir",
      "d": "<code>while</code> dövrü həmişə əvvəlcədən məlum olan sabit sayda təkrarlanmalıdır"
     }
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Matrisin transponirə edilməsi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T8. Matrisin transponirə edilməsi (10 bal)</h4>\n<p><i>Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>N × M ölçülü matrisin <b>transponirə edilmiş</b> (M × N) matrisini quran <code>transpoze(matris)</code> funksiyasını yazın<br>(sətirlər sütunlara çevrilir).</p>\n<p>Nümunə: <code>transpoze([[1, 2], [3, 4], [5, 6]])</code> → <code>[[1, 3, 5], [2, 4, 6]]</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def transpoze(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Hərflərin registrini dəyişmək (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. Hərflərin registrini dəyişmək (10 bal)</h4>\n<p><i>Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Mətndəki bütün kiçik hərfləri böyük, böyük hərfləri isə kiçik hərflərə çevirən <code>registr_deyis(metn)</code> funksiyasını yazın<br>(<b><code>swapcase()</code> metodundan istifadə etmədən</b>; digər simvollar dəyişmir).</p>\n<p>Nümunə: <code>registr_deyis(\"PyThOn\")</code> → <code>\"pYtHoN\"</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def registr_deyis(metn):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. Məntiqi və müqayisə operatorları (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T10. Məntiqi və müqayisə operatorları (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p><code>a = 5</code> və <code>b = 10</code> olduqda aşağıdakı ifadənin qiyməti nədir?</p>\n<pre class=\"md-code\"><code>not (a &gt; 3 and b &lt; 10) or a == b</code></pre>",
     "options": {
      "a": "<code>5</code>",
      "b": "<code>True</code>",
      "c": "<code>False</code>",
      "d": "Xəta, çünki <code>not</code> mötərizədən əvvəl yazıla bilməz"
     }
    }
   ],
   "steps": [
    {
     "k": "code",
     "task": "T1",
     "code": "def mesafe(x1, y1, x2, y2):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    assert _same(_call(mesafe, 0, 0, 3, 4), 5.0), \"mesafe(0, 0, 3, 4) 5.0 olmalıdır\"\n    assert _same(_call(mesafe, -1, 2, 5, -6), 10.0), \"mesafe(-1, 2, 5, -6) 10.0 olmalıdır\"\n    assert _same(_call(mesafe, 0, 0, 1, 1), 1.41421356), \"mesafe(0, 0, 1, 1) təxminən 1.414 olmalıdır\"\n    assert _same(_call(mesafe, 2, 3, 2, 3), 0), \"eyni nöqtələr arasındakı məsafə 0 olmalıdır\"\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def sait_samit(metn):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    cases = [(\"Salam Baku\", (4, 5)), (\"Ölkə 2026!\", (2, 2)), (\"Python\", (1, 5)), (\"Azərbaycan\", (4, 6))]\n    res = [_seq(_call(sait_samit, s), 2) for s, _ in cases]\n    return grade(\n        (5, \"sait hərflərin sayı (ə, ö, ü, ı da saitdir)\", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),\n        (5, \"samit hərflərin sayı (boşluq, rəqəm və işarələr sayılmır)\", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),\n    )\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "var",
     "task": "T3",
     "var": "cavab_T3"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    assert _h(cavab_T3) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def cem_orta(ededler):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    cases = [([5, 10, 15, 0], (30, 10.0)), ([4, 0], (4, 4.0)), ([2, 3, 0, 100, 200], (5, 2.5)), ([-6, 12, 3, 0], (9, 3.0))]\n    res = [_seq(_call(cem_orta, lst), 2) for lst, _ in cases]\n    return grade(\n        (5, \"cəm (0-a qədər)\", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),\n        (5, \"ədədi orta (0-a qədər)\", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),\n    )\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "var",
     "task": "T5",
     "var": "cavab_T5"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    assert _h(cavab_T5) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "code",
     "task": "T6",
     "code": "def rub(x, y):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    import re\n    def where(x, y):\n        t = str(_call(rub, x, y)).casefold().replace(\"-\", \" \").replace(\"_\", \" \")\n        if any(w in t for w in (\"başlanğıc\", \"baslangic\", \"mərkəz\", \"merkez\", \"origin\", \"(0, 0)\")):\n            return \"O\"\n        if \"ox\" in t or \"oy\" in t or \"axis\" in t or \"oxu\" in t or \"ox \" in t:\n            if re.search(r\"\\box\\b|\\bx\\b|abs\", t):\n                return \"X\"\n            if re.search(r\"\\boy\\b|\\by\\b|ord\", t):\n                return \"Y\"\n        t = t.replace(\"rüb\", \" \").replace(\"rub\", \" \").replace(\"quadrant\", \" \")\n        for word, q in ((\"iv\", 4), (\"iii\", 3), (\"ii\", 2), (\"i\", 1)):\n            if re.search(r\"\\b\" + word + r\"\\b\", t):\n                return q\n        ns = _nums(t)\n        return ns[0] if ns else None\n    return grade(\n        (2, \"rub(4, 7) I rüb olmalıdır\", lambda: where(4, 7) == 1),\n        (2, \"rub(-3, 5) II rüb olmalıdır\", lambda: where(-3, 5) == 2),\n        (2, \"rub(-2, -9) III rüb olmalıdır\", lambda: where(-2, -9) == 3),\n        (2, \"rub(6, -1) IV rüb olmalıdır\", lambda: where(6, -1) == 4),\n        (2, \"oxlar və başlanğıc: (5, 0) OX oxu, (0, -3) OY oxu, (0, 0) Koordinat başlanğıcı\",\n         lambda: where(5, 0) == \"X\" and where(0, -3) == \"Y\" and where(0, 0) == \"O\"),\n    )\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "var",
     "task": "T7",
     "var": "cavab_T7"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    assert _h(cavab_T7) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "code",
     "task": "T8",
     "code": "def transpoze(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    return grade(\n        (5, \"transpoze([[1, 2], [3, 4], [5, 6]]) [[1, 3, 5], [2, 4, 6]] olmalıdır\",\n         lambda: _same(_call(transpoze, [[1, 2], [3, 4], [5, 6]]), [[1, 3, 5], [2, 4, 6]])),\n        (3, \"kvadrat matris: [[1, 2], [3, 4]] -> [[1, 3], [2, 4]]\", lambda: _same(_call(transpoze, [[1, 2], [3, 4]]), [[1, 3], [2, 4]])),\n        (2, \"bir sətir: [[7, 8, 9]] -> [[7], [8], [9]]\", lambda: _same(_call(transpoze, [[7, 8, 9]]), [[7], [8], [9]])),\n    )\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def registr_deyis(metn):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    return grade(\n        (5, 'registr_deyis(\"PyThOn\") \"pYtHoN\" olmalıdır', lambda: _same(_call(registr_deyis, \"PyThOn\"), \"pYtHoN\")),\n        (3, 'boşluq və rəqəmlər qalır: registr_deyis(\"Hello World 2026\") \"hELLO wORLD 2026\" olmalıdır',\n         lambda: _same(_call(registr_deyis, \"Hello World 2026\"), \"hELLO wORLD 2026\")),\n        (2, 'registr_deyis(\"abc\") \"ABC\" olmalıdır', lambda: _same(_call(registr_deyis, \"abc\"), \"ABC\")),\n    )\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "var",
     "task": "T10",
     "var": "cavab_T10"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _h(cavab_T10) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "C": {
   "name": "Variant C",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. range(start, stop, step) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T1. range(start, stop, step) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — C. Dövr Operatorları və İterasiya (For, While) · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Hansı çağırış dəqiq <code>10, 7, 4, 1</code> ədədlərini verir?</p>",
     "options": {
      "a": "<code>range(10, 0, -3)</code>",
      "b": "<code>range(1, 10, 3)</code>",
      "c": "<code>range(10, -3)</code>",
      "d": "<code>range(10, 1, -3)</code>"
     }
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Müsbət, mənfi və ya sıfır (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Müsbət, mənfi və ya sıfır (10 bal)</h4>\n<p><i>Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Ədədin <b>müsbət</b>, <b>mənfi</b> və ya <b>sıfıra bərabər</b> olduğunu yoxlayan <code>isare(n)</code> funksiyasını yazın.<br>Funksiya <code>\"Müsbət\"</code>, <code>\"Mənfi\"</code> və ya <code>\"Sıfır\"</code> qaytarsın (və ya məs. <code>\"Mənfi ədəd\"</code> çap etsin).</p>\n<p>Nümunə: <code>isare(-15)</code> → <code>\"Mənfi\"</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def isare(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. Siyahının orta qiyməti (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T3. Siyahının orta qiyməti (10 bal)</h4>\n<p><i>Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Ədəd siyahısı qəbul edən və onun elementlərinin <b>orta qiymətini</b> qaytaran <code>calculate_average(lst)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>calculate_average([10, 20, 30, 40])</code> → <code>25.0</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def calculate_average(lst):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. İç-içə if və girintilər (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T4. İç-içə if və girintilər (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — B. Şərt Operatorları və Budaqlanan Alqoritmlər · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>x = 7\nif x &gt; 0:\n    if x % 2 == 0:\n        print(\"müsbət cüt\")\n    else:\n        print(\"müsbət tək\")\nelse:\n    print(\"müsbət deyil\")</code></pre>",
     "options": {
      "a": "<code>müsbət deyil</code> — bütün <code>else</code>-lər ən xarici <code>if</code>-ə aiddir",
      "b": "<code>müsbət cüt</code> — iç-içə <code>if</code> buraxılır, ona görə onun <code>else</code> hissəsi heç vaxt icra olunmur",
      "c": "<code>müsbət tək</code> — daxili <code>else</code> daxili <code>if</code> ilə eyni girintidədir, ona görə ona aiddir",
      "d": "Heç nə — iç-içə <code>if</code> üçün fiqurlu mötərizələr <code>{ }</code> lazımdır"
     }
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. 3 rəqəmli ədədin rəqəmlərinin cəmi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T5. 3 rəqəmli ədədin rəqəmlərinin cəmi (10 bal)</h4>\n<p><i>Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>3 rəqəmli müsbət tam ədədin <b>rəqəmlərinin cəmini</b> hesablayan <code>reqemler_cemi(n)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>reqemler_cemi(384)</code> → <code>15</code>  (3 + 8 + 4)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def reqemler_cemi(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Ədədin bölənləri və onların sayı (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T6. Ədədin bölənləri və onların sayı (10 bal)</h4>\n<p><i>Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While) · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Tam ədədin <b>bütün bölənlərini</b> və <b>bölənlərinin sayını</b> tapan <code>bolenler(n)</code> funksiyasını yazın.<br>Funksiya iki qiymət qaytarsın: <code>bolenler_siyahisi, say</code>.</p>\n<p>Nümunə: <code>bolenler(12)</code> → <code>([1, 2, 3, 4, 6, 12], 6)</code>  (Bölənlər: 1, 2, 3, 4, 6, 12 (Sayı: 6))</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def bolenler(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. Yüksək və aşağı səviyyəli dillər; kompilyator və interpretator (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T7. Yüksək və aşağı səviyyəli dillər; kompilyator və interpretator (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Yüksək və aşağı səviyyəli dillər, kompilyator və interpretator haqqında hansı ifadə düzgündür və Python-u düzgün təsnif edir?</p>",
     "options": {
      "a": "Yüksək səviyyəli dillər insan dilinə yaxın və daşınandır, aşağı səviyyəli dillər (maşın kodu, assembler) avadanlığa yaxındır; kompilyator proqramı icradan əvvəl bütövlükdə tərcümə edir, interpretator isə əmr-əmr icra edir — Python yüksək səviyyəli, interpretasiya olunan dildir",
      "b": "Python aşağı səviyyəli dildir, çünki prosessorun registrləri ilə birbaşa işləyir və hər icradan əvvəl .exe faylına kompilyasiya olunur",
      "c": "Kompilyator proqramı sətir-sətir icra edir, interpretator isə əvvəlcə bütün proqramı maşın koduna çevirib .exe fayl yaradır",
      "d": "Yüksək səviyyəli dillər həmişə maşın kodundan sürətli işləyir, çünki heç bir tərcüməyə ehtiyac duymur"
     }
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Baş diaqonalın cəmi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T8. Baş diaqonalın cəmi (10 bal)</h4>\n<p><i>Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>N × N ölçülü kvadrat matrisin <b>baş diaqonalında</b> yerləşən elementlərin cəmini hesablayan <code>bas_diaqonal_cemi(matris)</code><br>funksiyasını yazın.</p>\n<p>Nümunə: <code>bas_diaqonal_cemi([[1, 2], [3, 4]])</code> → <code>5</code>  (1 + 4)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def bas_diaqonal_cemi(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Sətirlərin dəyişməzliyi və sətir metodları (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T9. Sətirlərin dəyişməzliyi və sətir metodları (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — E. Mətn Sətirləri (Strings) və Funksiyalar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod icra olunanda nə baş verir?</p>\n<pre class=\"md-code\"><code>s = \"salam\"\ns[0] = \"S\"</code></pre>",
     "options": {
      "a": "<code>TypeError</code> yaranır — sətirlər dəyişməzdir (immutable); yeni sətir yaratmaq lazımdır, məsələn <code>s = \"S\" + s[1:]</code> və ya <code>s = s.capitalize()</code>",
      "b": "<code>s</code> dəyişəni <code>\"S\"</code> olur, çünki bütün sətir yeni simvolla əvəz edilir",
      "c": "<code>s</code> dəyişəni <code>\"Salam\"</code> olur, çünki sətirlər siyahılar kimi dəyişdirilə bilər",
      "d": "Heç nə baş vermir — Python bu əmri səssizcə buraxır"
     }
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. 3 rəqəmli polindrom ədəd (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T10. 3 rəqəmli polindrom ədəd (10 bal)</h4>\n<p><i>Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>3 rəqəmli ədədin <b>polindrom</b> (soldan sağa və sağdan sola eyni oxunan) olub-olmadığını yoxlayan <code>polindrom_eded(n)</code><br>funksiyasını yazın. Funksiya <code>True</code> / <code>False</code> qaytarsın (və ya <code>\"Polindromdur\"</code> / <code>\"Polindrom deyil\"</code> çap etsin).</p>\n<p>Nümunə: <code>polindrom_eded(121)</code> → <code>True</code>, <code>polindrom_eded(123)</code> → <code>False</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def polindrom_eded(n):\n    # kodunuzu bura yazın\n    pass"
    }
   ],
   "steps": [
    {
     "k": "var",
     "task": "T1",
     "var": "cavab_T1"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    assert _h(cavab_T1) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def isare(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    def kind(n):\n        r = _call(isare, n)\n        if _has_word(r, \"müsbət\", \"musbet\", \"positive\"):\n            return \"+\"\n        if _has_word(r, \"mənfi\", \"menfi\", \"negative\"):\n            return \"-\"\n        if _has_word(r, \"sıfır\", \"sifir\", \"zero\") or _same(r, 0):\n            return \"0\"\n        return None\n    return grade(\n        (4, \"isare(-15) Mənfi olmalıdır\", lambda: kind(-15) == \"-\"),\n        (3, \"isare(8) Müsbət olmalıdır\", lambda: kind(8) == \"+\"),\n        (3, \"isare(0) Sıfır olmalıdır\", lambda: kind(0) == \"0\"),\n    )\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "code",
     "task": "T3",
     "code": "def calculate_average(lst):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    return grade(\n        (5, \"calculate_average([10, 20, 30, 40]) 25.0 olmalıdır\", lambda: _same(_call(calculate_average, [10, 20, 30, 40]), 25.0)),\n        (3, \"kəsr nəticə: calculate_average([1, 2]) 1.5 olmalıdır\", lambda: _same(_call(calculate_average, [1, 2]), 1.5)),\n        (2, \"mənfi ədədlər: calculate_average([-4, 4, 3]) 1.0 olmalıdır\", lambda: _same(_call(calculate_average, [-4, 4, 3]), 1.0)),\n    )\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "var",
     "task": "T4",
     "var": "cavab_T4"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    assert _h(cavab_T4) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "code",
     "task": "T5",
     "code": "def reqemler_cemi(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    return grade(\n        (4, \"reqemler_cemi(384) 15 olmalıdır\", lambda: _same(_call(reqemler_cemi, 384), 15)),\n        (2, \"reqemler_cemi(999) 27 olmalıdır\", lambda: _same(_call(reqemler_cemi, 999), 27)),\n        (2, \"reqemler_cemi(105) 6 olmalıdır (ortada 0 rəqəmi)\", lambda: _same(_call(reqemler_cemi, 105), 6)),\n        (2, \"reqemler_cemi(100) 1 olmalıdır\", lambda: _same(_call(reqemler_cemi, 100), 1)),\n    )\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "code",
     "task": "T6",
     "code": "def bolenler(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    cases = {12: [1, 2, 3, 4, 6, 12], 7: [1, 7], 36: [1, 2, 3, 4, 6, 9, 12, 18, 36]}\n    got = {n: _flat(_call(bolenler, n)) for n in cases}\n    return grade(\n        (6, \"bölənlərin siyahısı\", lambda: all(got[n][:len(d)] == d for n, d in cases.items())),\n        (4, \"bölənlərin sayı\", lambda: all(len(got[n]) == len(d) + 1 and got[n][-1] == len(d) for n, d in cases.items())),\n    )\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "var",
     "task": "T7",
     "var": "cavab_T7"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    assert _h(cavab_T7) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "code",
     "task": "T8",
     "code": "def bas_diaqonal_cemi(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _same(_call(bas_diaqonal_cemi, [[1, 2], [3, 4]]), 5), \"[[1, 2], [3, 4]] üçün cavab 5 olmalıdır\"\n    assert _same(_call(bas_diaqonal_cemi, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]), 15), \"3 × 3 matris üçün cavab 15 olmalıdır (1 + 5 + 9)\"\n    assert _same(_call(bas_diaqonal_cemi, [[-2]]), -2), \"[[-2]] üçün cavab -2 olmalıdır\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "var",
     "task": "T9",
     "var": "cavab_T9"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    assert _h(cavab_T9) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "code",
     "task": "T10",
     "code": "def polindrom_eded(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _same(_call(polindrom_eded, 121), True), \"121 polindromdur\"\n    assert _same(_call(polindrom_eded, 123), False), \"123 polindrom deyil\"\n    assert _same(_call(polindrom_eded, 707), True), \"707 polindromdur\"\n    assert _same(_call(polindrom_eded, 100), False), \"100 polindrom deyil\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "D": {
   "name": "Variant D",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. break, continue və dövrün else bloku (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T1. break, continue və dövrün else bloku (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — C. Dövr Operatorları və İterasiya (For, While) · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>for i in range(1, 6):\n    if i == 2:\n        continue\n    if i == 4:\n        break\n    print(i)\nelse:\n    print(\"bitdi\")</code></pre>",
     "options": {
      "a": "<code>1</code> və <code>3</code> — <code>continue</code> 2-ni buraxır, <code>break</code> 4-də dövrü dayandırır, <code>break</code> olduğu üçün <code>else</code> bloku icra olunmur",
      "b": "<code>1</code>, <code>3</code>, <code>5</code> və <code>bitdi</code> — <code>break</code> yalnız cari təkrarı dayandırır",
      "c": "<code>1</code>, <code>2</code> və <code>3</code> — <code>continue</code> dövrü tamamilə dayandırır",
      "d": "<code>1</code>, <code>3</code> və <code>bitdi</code> — dövrün <code>else</code> bloku həmişə icra olunur"
     }
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Köməkçi diaqonalın maksimumu (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Köməkçi diaqonalın maksimumu (10 bal)</h4>\n<p><i>Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>N × N ölçülü kvadrat matrisin <b>köməkçi diaqonalında</b> (sağ yuxarı küncdən sol aşağı küncə) yerləşən elementlərin<br><b>maksimumunu</b> tapan <code>komekci_diaqonal_max(matris)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>komekci_diaqonal_max([[1, 9], [3, 4]])</code> → <code>9</code>  (9 və 3-dən ən böyüyü)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def komekci_diaqonal_max(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. Dinamik tipləşdirmə və girintilər (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T3. Dinamik tipləşdirmə və girintilər (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Python-da <b>dinamik tipləşdirmə</b> və <b>girintilər (indentation)</b> haqqında hansı ifadə düzgündür?</p>",
     "options": {
      "a": "Hər dəyişən tipi ilə elan olunmalıdır, məsələn <code>int x = 5</code>, və bu tip sonradan heç vaxt dəyişə bilməz",
      "b": "Tip dəyişənə deyil, obyektə aiddir, ona görə eyni ad əvvəl <code>int</code>, sonra <code>str</code> obyektinə istinad edə bilər; girinti sintaksisin hissəsidir — <code>if</code>, <code>for</code>, <code>def</code> … sonrakı blokları müəyyən edir, səhv girinti <code>IndentationError</code> yaradır",
      "c": "<code>x = 5</code> yazıldıqdan sonra <code>x = \"salam\"</code> əmri <code>TypeError</code> verir, çünki <code>x</code> artıq tam ədəd tipindədir",
      "d": "Girintilər yalnız oxunaqlılıq üçündür; Python blokları fiqurlu mötərizələrlə <code>{ }</code> müəyyən edir"
     }
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Polindrom söz (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. Polindrom söz (10 bal)</h4>\n<p><i>Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>Sözün <b>polindrom</b> (soldan sağa və sağdan sola eyni oxunan, məs. <code>'ana'</code>, <code>'kələk'</code>, <code>'radar'</code>) olub-olmadığını yoxlayan<br><code>polindrom_soz(soz)</code> funksiyasını yazın. Funksiya <code>True</code> / <code>False</code> qaytarsın (və ya <code>\"Polindromdur\"</code> / <code>\"Polindrom deyil\"</code> çap etsin).</p>\n<p>Nümunə: <code>polindrom_soz(\"radar\")</code> → <code>True</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def polindrom_soz(soz):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Truthy və falsy dəyərlər (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T5. Truthy və falsy dəyərlər (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Hansı siyahıda <b>yalnız</b> şərt daxilində <code>False</code> kimi qiymətləndirilən (falsy) dəyərlər var?</p>",
     "options": {
      "a": "<code>0</code>, <code>0.0</code>, <code>''</code>, <code>[]</code>, <code>{}</code>, <code>None</code>, <code>False</code>",
      "b": "<code>None</code>, <code>[0]</code>, <code>0.0</code>, <code>''</code>",
      "c": "<code>0</code>, <code>'0'</code>, <code>[]</code>, <code>None</code>",
      "d": "<code>False</code>, <code>' '</code> (boşluq simvolu), <code>()</code>, <code>0</code>"
     }
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. 1-dən N-ə qədər ədədlərin cəmi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T6. 1-dən N-ə qədər ədədlərin cəmi (10 bal)</h4>\n<p><i>Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While) · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>1-dən N-ə qədər (N daxil) olan tam ədədlərin <b>cəmini</b> dövr vasitəsilə hesablayan <code>cem_1_n(n)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>cem_1_n(10)</code> → <code>55</code>  (Cəm = 55)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def cem_1_n(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. Siyahı metodları (append, insert, remove, pop) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T7. Siyahı metodları (append, insert, remove, pop) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — D. Birölçülü və İkiölçülü Massivlər / Siyahılar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>a = [3, 1, 2]\na.append(5)\na.insert(0, 9)\na.remove(1)\nx = a.pop()\nprint(a, x)</code></pre>",
     "options": {
      "a": "<code>[9, 2, 5] 3</code>",
      "b": "<code>[3, 2, 5] 9</code>",
      "c": "<code>[9, 3, 2, 5] 5</code>",
      "d": "<code>[9, 3, 2] 5</code>"
     }
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. İki dəyişənin qiymətlərinin yerini dəyişmək (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T8. İki dəyişənin qiymətlərinin yerini dəyişmək (10 bal)</h4>\n<p><i>Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>İki dəyişənin (<code>a</code> və <code>b</code>) qiymətlərini <b>üçüncü köməkçi dəyişəndən istifadə etmədən</b> (Pythonic swap) dəyişən<br><code>yer_deyis(a, b)</code> funksiyasını yazın. Funksiya yeni qiymətləri <code>a, b</code> ardıcıllığı ilə qaytarsın.</p>\n<p>Nümunə: <code>yer_deyis(5, 9)</code> → <code>(9, 5)</code>  (a = 9, b = 5)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def yer_deyis(a, b):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Bala görə qiymət hərfi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. Bala görə qiymət hərfi (10 bal)</h4>\n<p><i>Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Tələbənin imtahan balına (0–100) görə <b>qiymət hərfini</b> qaytaran <code>qiymet_herfi(bal)</code> funksiyasını yazın:<br>91–100: A, 81–90: B, 71–80: C, 61–70: D, 51–60: E, 0–50: F.</p>\n<p>Nümunə: <code>qiymet_herfi(85)</code> → <code>\"B\"</code>  (Qiymət: B)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def qiymet_herfi(bal):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. Rəqəmlərin sayı və cəmi (while ilə) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T10. Rəqəmlərin sayı və cəmi (while ilə) (10 bal)</h4>\n<p><i>Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While) · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Tam ədədin <b>rəqəmlərinin sayını</b> və <b>rəqəmlərinin cəmini</b> <code>while</code> dövrü ilə hesablayan <code>reqem_say_cem(n)</code> funksiyasını yazın.<br>Funksiya iki qiymət qaytarsın: <code>say, cem</code>.</p>\n<p>Nümunə: <code>reqem_say_cem(4052)</code> → <code>(4, 11)</code>  (Rəqəm sayı: 4, Rəqəm cəmi: 11)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def reqem_say_cem(n):\n    # kodunuzu bura yazın\n    pass"
    }
   ],
   "steps": [
    {
     "k": "var",
     "task": "T1",
     "var": "cavab_T1"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    assert _h(cavab_T1) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def komekci_diaqonal_max(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    return grade(\n        (4, \"komekci_diaqonal_max([[1, 9], [3, 4]]) 9 olmalıdır\", lambda: _same(_call(komekci_diaqonal_max, [[1, 9], [3, 4]]), 9)),\n        (4, \"3 × 3: [[1, 2, 3], [4, 5, 6], [70, 8, 9]] -> 70 (köməkçi diaqonal: 3, 5, 70)\",\n         lambda: _same(_call(komekci_diaqonal_max, [[1, 2, 3], [4, 5, 6], [70, 8, 9]]), 70)),\n        (2, \"baş diaqonal yox, köməkçi diaqonal: [[100, 1], [2, 100]] -> 2\",\n         lambda: _same(_call(komekci_diaqonal_max, [[100, 1], [2, 100]]), 2)),\n    )\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "var",
     "task": "T3",
     "var": "cavab_T3"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    assert _h(cavab_T3) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def polindrom_soz(soz):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    assert _same(_call(polindrom_soz, \"radar\"), True), \"'radar' polindromdur\"\n    assert _same(_call(polindrom_soz, \"kələk\"), True), \"'kələk' polindromdur\"\n    assert _same(_call(polindrom_soz, \"ana\"), True), \"'ana' polindromdur\"\n    assert _same(_call(polindrom_soz, \"python\"), False), \"'python' polindrom deyil\"\n    assert _same(_call(polindrom_soz, \"abca\"), False), \"'abca' polindrom deyil\"\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "var",
     "task": "T5",
     "var": "cavab_T5"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    assert _h(cavab_T5) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "code",
     "task": "T6",
     "code": "def cem_1_n(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    assert _same(_call(cem_1_n, 10), 55), \"cem_1_n(10) 55 olmalıdır\"\n    assert _same(_call(cem_1_n, 1), 1), \"cem_1_n(1) 1 olmalıdır\"\n    assert _same(_call(cem_1_n, 100), 5050), \"cem_1_n(100) 5050 olmalıdır (N özü də daxildir)\"\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "var",
     "task": "T7",
     "var": "cavab_T7"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    assert _h(cavab_T7) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "code",
     "task": "T8",
     "code": "def yer_deyis(a, b):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _same(_call(yer_deyis, 5, 9), (9, 5)), \"yer_deyis(5, 9) (9, 5) olmalıdır\"\n    assert _same(_call(yer_deyis, -1, 7), (7, -1)), \"yer_deyis(-1, 7) (7, -1) olmalıdır\"\n    assert _same(_call(yer_deyis, 4, 4), (4, 4)), \"yer_deyis(4, 4) (4, 4) olmalıdır\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def qiymet_herfi(bal):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    return grade(\n        (3, \"qiymet_herfi(85) B, qiymet_herfi(95) A olmalıdır\",\n         lambda: _same(_call(qiymet_herfi, 85), \"B\") and _same(_call(qiymet_herfi, 95), \"A\")),\n        (3, \"qiymet_herfi(75) C, (65) D, (55) E olmalıdır\",\n         lambda: _same(_call(qiymet_herfi, 75), \"C\") and _same(_call(qiymet_herfi, 65), \"D\") and _same(_call(qiymet_herfi, 55), \"E\")),\n        (2, \"qiymet_herfi(30) F olmalıdır\", lambda: _same(_call(qiymet_herfi, 30), \"F\")),\n        (2, \"sərhəd qiymətləri: 91 → A, 90 → B, 51 → E, 50 → F\",\n         lambda: all(_same(_call(qiymet_herfi, b), h) for b, h in ((91, \"A\"), (90, \"B\"), (51, \"E\"), (50, \"F\")))),\n    )\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "code",
     "task": "T10",
     "code": "def reqem_say_cem(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    cases = [(4052, (4, 11)), (7, (1, 7)), (99999, (5, 45)), (1000, (4, 1))]\n    res = [_seq(_call(reqem_say_cem, n), 2) for n, _ in cases]\n    return grade(\n        (5, \"rəqəmlərin sayı\", lambda: all(r and _same(r[0], e[0]) for r, (_, e) in zip(res, cases))),\n        (5, \"rəqəmlərin cəmi\", lambda: all(r and _same(r[1], e[1]) for r, (_, e) in zip(res, cases))),\n    )\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "E": {
   "name": "Variant E",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. Saniyəni saat, dəqiqə və saniyəyə çevirmək (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T1. Saniyəni saat, dəqiqə və saniyəyə çevirmək (10 bal)</h4>\n<p><i>Kod tapşırığı · A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Verilmiş saniyə miqdarını <b>saat, dəqiqə və saniyəyə</b> çevirən <code>saniye_cevir(saniye)</code> funksiyasını yazın.<br>Funksiya üç qiymət qaytarsın: <code>saat, deqiqe, saniye</code>.</p>\n<p>Nümunə: <code>saniye_cevir(3665)</code> → <code>(1, 1, 5)</code>  (1 saat, 1 dəqiqə, 5 saniyə)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def saniye_cevir(saniye):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Cüt ədədləri süzgəcdən keçirmək: get_evens(lst) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Cüt ədədləri süzgəcdən keçirmək: get_evens(lst) (10 bal)</h4>\n<p><i>Kod tapşırığı · E. Mətn Sətirləri (Strings) və Funksiyalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Siyahıdakı <b>cüt ədədləri</b> süzgəcdən keçirib <b>yeni siyahı</b> qaytaran <code>get_evens(lst)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>get_evens([1, 2, 3, 4, 5, 6, 7, 8])</code> → <code>[2, 4, 6, 8]</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def get_evens(lst):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. Riyazi operatorlar və icra prioriteti (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T3. Riyazi operatorlar və icra prioriteti (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Aşağıdakı ifadənin qiyməti nəyə bərabərdir?</p>\n<pre class=\"md-code\"><code>2 + 3 * 4 ** 2 // 5 % 4</code></pre>",
     "options": {
      "a": "<code>3</code>",
      "b": "<code>11</code>",
      "c": "<code>0</code>",
      "d": "<code>9.6</code>"
     }
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Matrisin hər sətrinin cəmi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. Matrisin hər sətrinin cəmi (10 bal)</h4>\n<p><i>Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>N × M ölçülü matrisin (siyahılar siyahısı) <b>hər sətrinin elementlərinin cəmini</b> ayrıca hesablayıb siyahı kimi qaytaran<br><code>setir_cemleri(matris)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>setir_cemleri([[1, 2, 3], [4, 5, 6]])</code> → <code>[6, 15]</code>  (Sətir 1 cəmi: 6, Sətir 2 cəmi: 15)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def setir_cemleri(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Qısa qapanma qiymətləndirməsi (Short-Circuit) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T5. Qısa qapanma qiymətləndirməsi (Short-Circuit) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — B. Şərt Operatorları və Budaqlanan Alqoritmlər · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p><code>x = 0</code>. Python aşağıdakı şərti qiymətləndirəndə nə baş verir?</p>\n<pre class=\"md-code\"><code>if x != 0 and 10 / x &gt; 1:\n    print(\"böyük\")</code></pre>",
     "options": {
      "a": "Şərt <code>False</code> olur və xəta yaranmır: <code>and</code> ilk yalan operandda dayanır, ona görə <code>10 / x</code> ümumiyyətlə hesablanmır",
      "b": "<code>ZeroDivisionError</code> yaranır, çünki Python <code>and</code>-in hər iki tərəfini həmişə hesablayır",
      "c": "Şərt <code>True</code> olur, çünki <code>10 / 0</code> sonsuzluq kimi qəbul edilir",
      "d": "Python əvvəlcə sağ operandı hesablayır, ona görə nəticə yalnız <code>10 / x &gt; 1</code>-dən asılıdır"
     }
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. 7-yə bölündükdə qalığı 3 olan ədədlərin cəmi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T6. 7-yə bölündükdə qalığı 3 olan ədədlərin cəmi (10 bal)</h4>\n<p><i>Kod tapşırığı · C. Dövr Operatorları və İterasiya (For, While) · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>1-dən N-ə qədər (N daxil) olan ədədlər arasında <b>7-yə bölündükdə qalıqda 3</b> alınan ədədlərin cəmini hesablayan<br><code>qaliq_cemi(n)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>qaliq_cemi(100)</code> → <code>679</code>  (3 + 10 + 17 + … + 94)</p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def qaliq_cemi(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. Tək ədədləri 0 ilə əvəz etmək (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T7. Tək ədədləri 0 ilə əvəz etmək (10 bal)</h4>\n<p><i>Kod tapşırığı · D. Birölçülü və İkiölçülü Massivlər / Siyahılar · qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)</i></p>\n<p>Siyahıdakı bütün <b>tək ədədləri 0 ilə əvəz edən</b> <code>tekleri_sifirla(lst)</code> funksiyasını yazın.</p>\n<p>Nümunə: <code>tekleri_sifirla([1, 2, 3, 4, 5, 6])</code> → <code>[0, 2, 0, 4, 0, 6]</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def tekleri_sifirla(lst):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Funksiyalar, return və lokal / qlobal dəyişənlər (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T8. Funksiyalar, return və lokal / qlobal dəyişənlər (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — E. Mətn Sətirləri (Strings) və Funksiyalar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bu kod ekrana nə çıxarır?</p>\n<pre class=\"md-code\"><code>x = 10\ndef f():\n    x = 5\n    return x * 2\ny = f()\nprint(x, y)</code></pre>",
     "options": {
      "a": "<code>10 20</code> — funksiya qlobal <code>x</code>-dən istifadə edir",
      "b": "Xəta — <code>global</code> açar sözü olmadan funksiyada <code>x</code> adlı dəyişən yaratmaq olmaz",
      "c": "<code>10 10</code> — funksiyanın içindəki <code>x</code> lokal dəyişəndir və qlobal <code>x</code>-i dəyişmir; <code>return</code> 5 * 2 = 10 qaytarır",
      "d": "<code>5 10</code> — funksiyadakı mənimsətmə qlobal <code>x</code>-i dəyişir"
     }
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Üçbucaq əmələ gəlirmi? (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. Üçbucaq əmələ gəlirmi? (10 bal)</h4>\n<p><i>Kod tapşırığı · B. Şərt Operatorları və Budaqlanan Alqoritmlər · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Üç tərəfin uzunluğuna (a, b, c) görə <b>üçbucaq əmələ gəlib-gəlmədiyini</b> yoxlayan <code>ucbucaqdir(a, b, c)</code> funksiyasını yazın.<br>Üçbucaq bərabərsizliyi: a + b &gt; c, a + c &gt; b, b + c &gt; a.<br>Funksiya <code>True</code> / <code>False</code> qaytarsın (və ya <code>\"Üçbucaq əmələ gətirir\"</code> / <code>\"Üçbucaq əmələ gətirmir\"</code> çap etsin).</p>\n<p>Nümunə: <code>ucbucaqdir(3, 4, 5)</code> → <code>True</code></p>\n<p><i>Nəticəni funksiyadan qaytarın (<code>return</code>); ekrana çıxarmaq (<code>print</code>) da qəbul olunur. <code>input()</code> lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür.</i></p>",
     "starter": "def ucbucaqdir(a, b, c):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. Şərt operatorunun üçlü forması (Ternary) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T10. Şərt operatorunun üçlü forması (Ternary) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p><code>parity</code> dəyişəninə <code>\"cüt\"</code> və ya <code>\"tək\"</code> yazan <b>düzgün</b> üçlü (ternary) şərt ifadəsi hansıdır?</p>",
     "options": {
      "a": "<code>parity = \"cüt\" if n % 2 == 0</code>",
      "b": "<code>parity = if n % 2 == 0 \"cüt\" else \"tək\"</code>",
      "c": "<code>parity = n % 2 == 0 ? \"cüt\" : \"tək\"</code>",
      "d": "<code>parity = \"cüt\" if n % 2 == 0 else \"tək\"</code>"
     }
    }
   ],
   "steps": [
    {
     "k": "code",
     "task": "T1",
     "code": "def saniye_cevir(saniye):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    return grade(\n        (4, \"saniye_cevir(3665) (1, 1, 5) olmalıdır\", lambda: _same(_call(saniye_cevir, 3665), (1, 1, 5))),\n        (2, \"saniye_cevir(59) (0, 0, 59) olmalıdır\", lambda: _same(_call(saniye_cevir, 59), (0, 0, 59))),\n        (2, \"saniye_cevir(7200) (2, 0, 0) olmalıdır\", lambda: _same(_call(saniye_cevir, 7200), (2, 0, 0))),\n        (2, \"saniye_cevir(86399) (23, 59, 59) olmalıdır\", lambda: _same(_call(saniye_cevir, 86399), (23, 59, 59))),\n    )\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def get_evens(lst):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    return grade(\n        (5, \"get_evens([1, 2, 3, 4, 5, 6, 7, 8]) [2, 4, 6, 8] olmalıdır\",\n         lambda: _same(_call(get_evens, [1, 2, 3, 4, 5, 6, 7, 8]), [2, 4, 6, 8])),\n        (3, \"mənfi ədədlər və sıfır: get_evens([-4, 0, 7, 10]) [-4, 0, 10] olmalıdır\",\n         lambda: _same(_call(get_evens, [-4, 0, 7, 10]), [-4, 0, 10])),\n        (2, \"cüt ədəd yoxdursa: get_evens([1, 3, 5]) [] olmalıdır\", lambda: _same(_call(get_evens, [1, 3, 5]), [])),\n    )\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "var",
     "task": "T3",
     "var": "cavab_T3"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    assert _h(cavab_T3) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def setir_cemleri(matris):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    return grade(\n        (5, \"setir_cemleri([[1, 2, 3], [4, 5, 6]]) [6, 15] olmalıdır\", lambda: _same(_call(setir_cemleri, [[1, 2, 3], [4, 5, 6]]), [6, 15])),\n        (3, \"3 sətirli matris: [[1, 1], [2, 2], [-3, 10]] -> [2, 4, 7]\",\n         lambda: _same(_call(setir_cemleri, [[1, 1], [2, 2], [-3, 10]]), [2, 4, 7])),\n        (2, \"bir sətirli matris: [[5, 5, 5, 5]] -> [20]\", lambda: _same(_call(setir_cemleri, [[5, 5, 5, 5]]), [20])),\n    )\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "var",
     "task": "T5",
     "var": "cavab_T5"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    assert _h(cavab_T5) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "code",
     "task": "T6",
     "code": "def qaliq_cemi(n):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    return grade(\n        (5, \"qaliq_cemi(100) 679 olmalıdır\", lambda: _same(_call(qaliq_cemi, 100), 679)),\n        (3, \"qaliq_cemi(20) 30 olmalıdır (3 + 10 + 17)\", lambda: _same(_call(qaliq_cemi, 20), 30)),\n        (2, \"N özü də daxildir: qaliq_cemi(10) 13 olmalıdır (3 + 10)\", lambda: _same(_call(qaliq_cemi, 10), 13)),\n    )\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "code",
     "task": "T7",
     "code": "def tekleri_sifirla(lst):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    assert _same(_call(tekleri_sifirla, [1, 2, 3, 4, 5, 6]), [0, 2, 0, 4, 0, 6]), \"[1, 2, 3, 4, 5, 6] -> [0, 2, 0, 4, 0, 6] olmalıdır\"\n    assert _same(_call(tekleri_sifirla, [-3, -2, 7]), [0, -2, 0]), \"mənfi tək ədədlər də: [-3, -2, 7] -> [0, -2, 0] olmalıdır\"\n    assert _same(_call(tekleri_sifirla, [2, 4, 8]), [2, 4, 8]), \"tək ədəd yoxdursa siyahı dəyişməməlidir\"\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "var",
     "task": "T8",
     "var": "cavab_T8"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _h(cavab_T8) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def ucbucaqdir(a, b, c):\n    # kodunuzu bura yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    return grade(\n        (3, \"ucbucaqdir(3, 4, 5) True olmalıdır\", lambda: _same(_call(ucbucaqdir, 3, 4, 5), True)),\n        (2, \"ucbucaqdir(7, 10, 5) True olmalıdır\", lambda: _same(_call(ucbucaqdir, 7, 10, 5), True)),\n        (2, \"ucbucaqdir(1, 2, 3) False olmalıdır (a + b = c kifayət deyil)\", lambda: _same(_call(ucbucaqdir, 1, 2, 3), False)),\n        (3, \"ucbucaqdir(10, 1, 2) və ucbucaqdir(1, 10, 2) False olmalıdır (hər tərəf yoxlanmalıdır)\",\n         lambda: _same(_call(ucbucaqdir, 10, 1, 2), False) and _same(_call(ucbucaqdir, 1, 10, 2), False)),\n    )\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "var",
     "task": "T10",
     "var": "cavab_T10"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _h(cavab_T10) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"seçilmiş cavab düzgün deyil\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  }
 }
};
