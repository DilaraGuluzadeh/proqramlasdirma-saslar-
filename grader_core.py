# -*- coding: utf-8 -*-
"""
Yoxlama mühərriki — həm brauzerdə (Pyodide, index.html), həm də müəllimin
kompüterində (yeniden_qiymetlendir.py) eyni kod işləyir.

HARNESS_SOURCE mətni tools/build_bank.py tərəfindən exam_data.js-ə yerləşdirilir.

Məqsəd: yazılış tərzini yox, NƏTİCƏNİ yoxlamaq.
  * Funksiya cavabı `return` edə və ya sadəcə `print` edə bilər — hər ikisi qəbul olunur.
  * Format sərbəstdir: 15, "15", "Rəqəmlərin cəmi: 15", (1, 1, 5), "1 saat, 1 dəqiqə, 5 saniyə" ...
  * list / tuple, 5 / 5.0, kiçik yuvarlaqlaşdırma fərqləri eyni sayılır.
  * Bəli/xeyr cavabları True/False və ya mətn ola bilər: "Sadə ədəddir", "Polindrom deyil", "Uzun ildir".
  * Tələbə funksiyanın adını dəyişsə, yazdığı tək funksiya götürülür.
  * Tab, Windows sətir sonları, "ağıllı" dırnaqlar və Jupyter sətirləri avtomatik təmizlənir.
  * Yalnız imtahan səhifəsini poza biləcək bir neçə modul bloklanır; qalan hər şey sərbəstdir.
"""

import types

HARNESS_SOURCE = r'''
import ast
import builtins
import contextlib
import copy
import hashlib
import io
import json
import math
import re
import sys
import time
import types

# Yalnız imtahan səhifəsinə mane ola biləcək modullar bloklanır; digər standart modullar sərbəstdir
_BLOCKED_MODULES = ("js", "pyodide", "pyodide_js", "_pyodide", "micropip", "subprocess", "socket")
_real_import = builtins.__import__


def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in _BLOCKED_MODULES:
        raise ImportError(f"'{name}' modulu imtahanda istifadə edilə bilməz")
    return _real_import(name, globals, locals, fromlist, level)


class InputNotNeeded(Exception):
    pass


def _no_input(prompt=""):
    raise InputNotNeeded("Bu imtahanda input() lazım deyil — qiymətlər funksiyaya parametr kimi ötürülür "
                         "(məs. reqemler_cemi(384)). input() əvəzinə funksiyanın parametrlərindən istifadə edin.")


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


OK_MSG = "✅ Tapşırıq {t}: DÜZGÜNDÜR (+{p} bal)"
PARTIAL_MSG = "🟡 Tapşırıq {t}: QİSMƏN DÜZGÜNDÜR (+{p} / {m} bal)"
FAIL_MSG = "❌ Tapşırıq {t}: XƏTA — qaytarılan / çap olunan nəticə gözlənilən nəticəyə uyğun deyil!"


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


def _exec_limited(code, ns, budget, out):
    """Kodu vaxt limiti ilə icra edir (sonsuz dövr brauzeri dondurmasın)."""
    deadline = time.monotonic() + budget

    def tracer(frame, event, arg):
        if time.monotonic() > deadline:
            raise TimeoutError(f"icra {budget:g} saniyədən çox çəkdi (sonsuz dövr ola bilər)")
        return tracer

    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        sys.settrace(tracer)
        try:
            exec(compile(code, "<code>", "exec"), ns)
        finally:
            sys.settrace(None)


_QUOTES = {"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", " ": " ", " ": " ",
           "​": "", "‌": "", "‍": "", "﻿": "", "–": "-", "−": "-"}


def normalize_code(code):
    """
    Kodu tolerant şəkildə qəbul edir:
    CRLF, sətir başındakı Tab (4 boşluq), görünməz/qeyri-standart simvollar (NBSP, sıfır enli boşluq), "ağıllı" dırnaqlar,
    ümumi artıq girinti (kod xanası içəridən kopyalananda) və Jupyter sehrli sətirləri (%magic, !əmr) düzəldilir.
    """
    import textwrap
    code = str(code).replace("\r\n", "\n").replace("\r", "\n")
    code = "".join(_QUOTES.get(c, c) for c in code)
    lines = []
    for ln in code.split("\n"):
        stripped = ln.lstrip(" \t")
        lead = ln[:len(ln) - len(stripped)].replace("\t", "    ")
        if stripped.startswith(("%", "!")) and not stripped.startswith("!="):
            continue                      # Jupyter: %matplotlib inline, !pip install ...
        lines.append((lead + stripped).rstrip())
    return textwrap.dedent("\n".join(lines)).strip("\n") + "\n"


def _describe(exc):
    if "'___'" in str(exc):
        return "`___` boşluqları hələ doldurulmayıb"
    if isinstance(exc, InputNotNeeded):
        return str(exc)
    if isinstance(exc, IndentationError):
        return f"Girinti xətası (sətir {exc.lineno}): {exc.msg}. Blokun (':' işarəsindən sonra) içindəki sətirlərə 4 boşluq girinti qoyun."
    if isinstance(exc, SyntaxError):
        return f"Sintaksis xətası (sətir {exc.lineno}): {exc.msg}"
    return f"{type(exc).__name__}: {exc}"


def _coerce(value):
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    if re.fullmatch(r"[+-]?\d+", s):
        return int(s)
    return s


def run_variant(steps, answers, upto=None, budget=10.0):
    """
    steps   : exam_data.js-dəki addımlar (tapşırıq ardıcıllığı ilə)
    answers : {"T1": "<kod>", "T2": "b", ...}
    upto    : yalnız bu tapşırığın testinə qədər icra et ("Kodu yoxla" düyməsi üçün)
    Nəticə  : {"results": {id: {ok, pts, max, msg, detail}}, "output": {id: stdout}}
    """
    answers = answers or {}
    ns = {
        "__name__": "__main__",
        "__builtins__": dict(vars(builtins), __import__=_guarded_import, input=_no_input),
        "math": math, "hashlib": hashlib, "_h": _h, "_eq": _eq, "grade": grade,
        "_call": _call, "_same": _same, "_yes": _yes, "_seq": _seq, "_lines": _lines, "_nums": _nums,
        "_flat": _flat, "_same_set": _same_set, "_has_word": _has_word,
    }
    errors, results, output = {}, {}, {}

    def check(task_id, points, test):
        t = task_id.split("_")[0]
        try:
            res = test()
            if isinstance(res, tuple) and len(res) == 3:
                got, tot, failed = res
                pts = int(points * got / tot + 0.5) if tot else 0
                if pts >= points:
                    results[t] = {"ok": True, "pts": points, "max": points, "partial": False,
                                  "msg": OK_MSG.format(t=t, p=points), "detail": ""}
                    return
                detail = "Ödənməyən hissələr: " + "; ".join(failed)
                if pts > 0:
                    results[t] = {"ok": False, "pts": pts, "max": points, "partial": True,
                                  "msg": PARTIAL_MSG.format(t=t, p=pts, m=points), "detail": detail}
                    return
                if t in errors:
                    detail = errors[t] if errors[t].startswith("`") else "kodunuz icra olunarkən xəta baş verdi → " + errors[t]
                results[t] = {"ok": False, "pts": 0, "max": points, "partial": False,
                              "msg": FAIL_MSG.format(t=t), "detail": detail}
                return
            results[t] = {"ok": True, "pts": points, "max": points, "partial": False,
                          "msg": OK_MSG.format(t=t, p=points), "detail": ""}
            return
        except AssertionError as e:
            detail = str(e) or "test şərti ödənmədi"
        except NameError as e:
            detail = f"tələb olunan funksiya / dəyişən təyin edilməyib ({e})"
        except BaseException as e:
            detail = _describe(e)
        if t in errors:
            detail = errors[t] if errors[t].startswith("`") else "kodunuz icra olunarkən xəta baş verdi → " + errors[t]
        results[t] = {"ok": False, "pts": 0, "max": points, "partial": False,
                      "msg": FAIL_MSG.format(t=t), "detail": detail}

    ns["check"] = check

    for st in steps:
        kind = st["k"]
        if kind == "var":
            ns[st["var"]] = _coerce(answers.get(st["task"]))
            continue
        label = st.get("task")
        code = st["code"]
        expected_fns = re.findall(r"^\s*def\s+([A-Za-z_]\w*)", st["code"], re.M) if kind == "code" else []
        if kind == "code":
            for name in expected_fns:          # əvvəlki tapşırığın eyniadlı funksiyası burada istifadə olunmasın
                ns.pop(name, None)
        if kind == "code" and label in answers and answers[label] is not None:
            code = normalize_code(answers[label])
        before = {k: id(v) for k, v in ns.items()}
        out = io.StringIO()
        try:
            _exec_limited(code, ns, budget, out)
        except BaseException as e:
            if label:
                errors[label] = _describe(e)
        if kind == "code" and expected_fns:
            # Tələbə funksiyanın adını dəyişibsə: yalnız bir yeni funksiya yazılıbsa, o götürülür
            new_fns = [v for k, v in ns.items()
                       if isinstance(v, types.FunctionType) and before.get(k) != id(v) and not k.startswith("_")]
            for name in expected_fns:
                if name not in ns and len(new_fns) == 1 and len(expected_fns) == 1:
                    ns[name] = new_fns[0]
        if label:
            output[label] = out.getvalue()[-2000:]
        elif kind == "test" and out.getvalue():
            # test zamanı tələbə funksiyasının çap etdikləri
            output[st["ids"][0]] = (output.get(st["ids"][0], "") + out.getvalue())[-2000:]
        if kind == "test" and upto and upto in st["ids"]:
            break

    if upto:
        results = {k: v for k, v in results.items() if k == upto}
        output = {k: v for k, v in output.items() if k == upto}
    return {"results": results, "output": output}


def run_json(payload):
    """Pyodide körpüsü: JSON mətn daxil olur, JSON mətn qayıdır."""
    p = json.loads(payload)
    return json.dumps(run_variant(p["steps"], p.get("answers"), p.get("upto"), p.get("budget", 10.0)),
                      ensure_ascii=False)
'''


def load_harness():
    """HARNESS_SOURCE-u adi Python modulu kimi yükləyir (CPython-da istifadə üçün)."""
    mod = types.ModuleType("exam_harness")
    exec(compile(HARNESS_SOURCE, "exam_harness", "exec"), mod.__dict__)
    return mod
