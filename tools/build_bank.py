# -*- coding: utf-8 -*-
"""
proqramlasdirmanin_esaslari_imtahan_suallari_v2.docx sual bankından 5 variantlı imtahan yaradır.

Hər variant: 10 tapşırıq = 4 nəzəri + 6 praktiki (kod), hər biri 10 bal, cəmi 100 bal.
  * Nəzəri suallar "Nəzəri Anlayış və Mövzu" hissəsindəndir (20 sual: A 8, B 4, C 3, D 3, E 2) — hər sual dəqiq bir
    variantda işlənir. Hər variantın 4 nəzəri sualı ən azı 3 fərqli kateqoriyadandır (bir kateqoriyadan ən çox 2 sual).
  * Kod tapşırıqları: hər variantda 5 kateqoriyanın (A–E) HAMISI var + 1 əlavə tapşırıq.
  * Heç bir sual iki variantda təkrarlanmır; bankda yan-yana olan (məs. C11 və C12) və ya məzmunca çox oxşar olan
    tapşırıqlar (məs. C6 "sadə ədəd" və E9 "is_prime") eyni variantda olmur.
  * Suallar variantlara bank sırası ilə paylanmır (A variantı hər kateqoriyanın ilk sualını almır) — kateqoriya daxilində qarışdırılır.
  * Hər variantda 10 tapşırığın sırası qarışdırılır: eyni kateqoriyadan iki tapşırıq ardıcıl gəlmir, nəzəri suallar yan-yana
    düşmür və heç iki variantın nəzəri/praktiki ardıcıllığı eyni deyil.
  * Bəzi kod tapşırıqları yalnız 0 / 10, digərləri isə hissə-hissə (0–10 arası) qiymətləndirilir.

İstifadə (layihənin kök qovluğundan):
    python tools/build_bank.py            # exam_data.js, variant_A..E.py, sual_banki_xeritesi.md yaradır
    python tools/build_bank.py --verify   # həmçinin yoxlayır: etalon həllər = 100/100, boş cavab = 0, qismən bal
"""
import hashlib
import os
import random
import re
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from grader_core import HARNESS_SOURCE, load_harness  # noqa: E402
from mdhtml import _inline, md_to_html, write_exam_data  # noqa: E402
from bank_theory import THEORY, THEORY_CATEGORIES, check_theory_answers  # noqa: E402
from bank_coding import CODING, CATEGORIES, SIMILAR  # noqa: E402

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

VARIANTS = ["A", "B", "C", "D", "E"]
PTS = 10
SEED = 20261021
UNIVERSITY = "BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)"
COURSE = "Proqramlaşdırmanın əsasları"
GROUP = "136a1"
YEAR = "1-ci kurs"
THEORY_BY_ID = {t[0]: t for t in THEORY}
SIMILAR_SET = {frozenset(p) for p in SIMILAR}


def sha(x):
    return hashlib.sha256(str(x).strip().lower().encode()).hexdigest()


def num_of(tid):
    return int(re.sub(r"\D", "", tid))


def far_apart(ids):
    """Eyni kateqoriyada bankda yan-yana olan və ya məzmunca oxşar suallar bir variantda olmasın."""
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if a[0] == b[0] and abs(num_of(a) - num_of(b)) <= 1:
                return False
            if frozenset((a, b)) in SIMILAR_SET:
                return False
    return True


def not_in_bank_order(seq):
    """A..E variantlarına verilən suallar bank sırası (və ya tərs sıra) ilə getməsin."""
    nums = [num_of(x) for x in seq]
    return nums != sorted(nums) and nums != sorted(nums, reverse=True)


# ----------------------------------------------------------------------
# Sualların variantlara bölünməsi
# ----------------------------------------------------------------------
def assign_theory(rnd):
    nv = len(VARIANTS)
    ids = [t[0] for t in THEORY]
    for _ in range(200000):
        rnd.shuffle(ids)
        res = [ids[v * 4:(v + 1) * 4] for v in range(nv)]
        ok = True
        for r in res:
            counts = [sum(1 for q in r if q[0] == c) for c in THEORY_CATEGORIES]
            if max(counts) > 2 or sum(1 for c in counts if c == 2) > 1 or not far_apart(r):
                ok = False
                break
        if not ok:
            continue
        # hər kateqoriyanın sualları variantlara bank sırası ilə düşməsin
        firsts = {}
        for v, r in enumerate(res):
            for q in r:
                firsts.setdefault(q[0], []).append(q)
        if all(len(s) < 3 or not_in_bank_order(s) for s in firsts.values()):
            return res
    raise RuntimeError("nəzəri bölgü tapılmadı")


def assign_coding(rnd):
    """Hər kateqoriyadan 6 tapşırıq: hər varianta 1 + bir varianta əlavə 1 (hər variant bir əlavə tapşırıq alır)."""
    nv = len(VARIANTS)
    cats = list(CATEGORIES)
    pools = {c: [t for t in CODING if t[0] == c] for c in cats}
    for _ in range(500000):
        extra = list(range(nv))
        rnd.shuffle(extra)
        res = [[] for _ in range(nv)]
        ok = True
        for ci, c in enumerate(cats):
            chosen = rnd.sample(pools[c], nv + 1)
            first, second = chosen[:nv], chosen[nv]
            if not not_in_bank_order(first):
                ok = False
                break
            for v in range(nv):
                res[v].append(first[v])
            res[extra[ci]].append(second)
        if not ok or not all(far_apart(r) for r in res):
            continue
        npart = [sum(CODING[t]["partial"] for t in r) for r in res]
        if not all(3 <= p <= 5 for p in npart):
            continue
        return res
    raise RuntimeError("kod bölgüsü tapılmadı")


def order_tasks(items, rnd, used_patterns):
    """items: [(növ, nömrə, kateqoriya_açarı)] -> qarışdırılmış sıra."""
    for _ in range(200000):
        seq = items[:]
        rnd.shuffle(seq)
        keys = [k for _, _, k in seq]
        cats = [q[0] for _, q, _ in seq]
        if any(keys[i] == keys[i + 1] or cats[i] == cats[i + 1] for i in range(len(seq) - 1)):
            continue
        if seq[0][0] == "theory" and seq[-1][0] == "theory":
            continue
        pattern = "".join("N" if k == "theory" else "K" for k, _, _ in seq)
        if pattern in used_patterns:
            continue
        used_patterns.add(pattern)
        return seq
    raise RuntimeError("sıra tapılmadı")


def make_plan():
    rnd = random.Random(SEED)
    theory = assign_theory(rnd)
    coding = assign_coding(rnd)
    plan, patterns = {}, set()
    for vi, v in enumerate(VARIANTS):
        items = [("theory", t, "N") for t in theory[vi]] + [("code", c, "K" + c[0]) for c in coding[vi]]
        plan[v] = order_tasks(items, random.Random(f"{SEED}-{v}"), patterns)
    return plan


# ----------------------------------------------------------------------
# Tapşırıqların qurulması
# ----------------------------------------------------------------------
def theory_task(tid, topic, v):
    qid, cat, short, question, correct, wrong = topic
    opts = [(True, correct)] + [(False, w) for w in wrong]
    random.Random(f"{v}-{qid}").shuffle(opts)
    letters = "abcd"
    options = {letters[i]: _inline(t) for i, (_, t) in enumerate(opts)}
    right = letters[[c for c, _ in opts].index(True)]
    title = f"Tapşırıq {tid}. {short} ({PTS} bal)"
    badge = (f"<p><i>Nəzəri sual · Nəzəri Anlayış və Mövzu — {cat}. {THEORY_CATEGORIES[cat]} · "
             f"düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>")
    html = f"<h4>{_inline(title)}</h4>\n{badge}\n" + md_to_html(question)
    task = {"id": tid, "title": title, "pts": PTS, "kind": "choice", "html": html, "options": options}
    steps = [
        {"k": "var", "task": tid, "var": f"cavab_{tid}"},
        {"k": "test", "ids": [tid], "code":
            f"def test_{tid.lower()}():\n"
            f"    assert _h(cavab_{tid}) == \"{sha(right)}\", \"seçilmiş cavab düzgün deyil\"\n"
            f"check(\"{tid}\", {PTS}, test_{tid.lower()})"},
    ]
    return task, steps, right, {"opts": options, "right": right, "q": question}


def grading_text(c):
    return ("qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)" if c["partial"]
            else "qiymətləndirmə: yalnız 0 və ya 10 bal (bütün yoxlamalar ödənməlidir)")


def code_task(tid, c):
    title = f"Tapşırıq {tid}. {c['title']} ({PTS} bal)"
    badge = f"<p><i>Kod tapşırığı · {c['cat']}. {CATEGORIES[c['cat']]} · {grading_text(c)}</i></p>"
    html = f"<h4>{_inline(title)}</h4>\n{badge}\n" + md_to_html(c["desc"])
    task = {"id": tid, "title": title, "pts": PTS, "kind": "code", "html": html, "starter": c["starter"]}
    fn = f"test_{tid.lower()}"
    code = f"def {fn}():\n" + textwrap.indent(c["test"], "    ") + f"\ncheck(\"{tid}\", {PTS}, {fn})"
    steps = [{"k": "code", "task": tid, "code": c["starter"]}, {"k": "test", "ids": [tid], "code": code}]
    return task, steps


def build():
    data = {"version": 4, "harness": HARNESS_SOURCE, "variants": {}}
    keys, mapping, extra = {}, {}, {}
    plan = make_plan()
    for v in VARIANTS:
        tasks, items, steps, key, maps, pyinfo = [], [], [], {}, [], []
        for i, (kind, qid, _) in enumerate(plan[v], 1):
            tid = f"T{i}"
            if kind == "theory":
                t = THEORY_BY_ID[qid]
                task, st, right, info = theory_task(tid, t, v)
                key[tid] = right
                maps.append((tid, "Nəzəri", f"[{qid}]", f"Nəzəri — {t[1]}. {THEORY_CATEGORIES[t[1]]}", t[2], "0 / 10", right))
                pyinfo.append(("theory", tid, t[2], info, None))
            else:
                c = CODING[qid]
                task, st = code_task(tid, c)
                key[tid] = c["solution"]
                fname = re.match(r"def\s+(\w+)", c["starter"]).group(1)
                maps.append((tid, "Kod", f"[{qid}]", f"{c['cat']}. {CATEGORIES[c['cat']]}", c["title"],
                             "0–10 (qismən)" if c["partial"] else "0 / 10", f"`{fname}()`"))
                pyinfo.append(("code", tid, c["title"], None, c))
            tasks.append(task)
            steps += st
            items.append({"type": "task", "id": tid})
        assert len(tasks) == 10 and sum(t["pts"] for t in tasks) == 100
        data["variants"][v] = {"name": f"Variant {v}", "max_score": 100, "items": items, "tasks": tasks, "steps": steps}
        keys[v], mapping[v], extra[v] = key, maps, pyinfo
    return data, keys, mapping, extra, plan


# ----------------------------------------------------------------------
# variant_X.py (tələbənin müstəqil işlədə biləcəyi fayl)
# ----------------------------------------------------------------------
def _helpers_source():
    a = HARNESS_SOURCE.index("def _plain(v):")
    b = HARNESS_SOURCE.index("OK_MSG =")
    helpers = HARNESS_SOURCE[a:b].rstrip()
    g0 = HARNESS_SOURCE.index("def grade(*items):")
    g1 = HARNESS_SOURCE.index("def _exec_limited")
    return helpers + "\n\n\n" + HARNESS_SOURCE[g0:g1].rstrip()


PY_HEADER = '''# -*- coding: utf-8 -*-
"""
{university}
Fənn: {course} — {year}, qrup {group} — SDF 1 (Variant {v})
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
   Funksiya nəticəni qaytara (`return`) və ya ekrana çıxara (`print`) bilər — hər ikisi qəbul olunur.
3. Faylı işə salın:   python variant_{v}.py
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

results = {{}}
_errors = {{}}


def _h(x):
    return hashlib.sha256(str(x).strip().lower().encode()).hexdigest()


{helpers}


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
        _errors[self.task_id] = f"kodunuz icra olunarkən xəta baş verdi → {{exc_type.__name__}}: {{exc}}"
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
                print(f"✅ Tapşırıq {{tid}}: DÜZGÜNDÜR (+{{points}} bal)")
                return
            reason = "Ödənməyən hissələr: " + "; ".join(failed)
            if pts > 0:
                print(f"🟡 Tapşırıq {{tid}}: QİSMƏN DÜZGÜNDÜR (+{{pts}} / {{points}} bal)")
                print(f"   ↳ {{reason}}")
                return
        else:
            results[task_id] = points
            print(f"✅ Tapşırıq {{tid}}: DÜZGÜNDÜR (+{{points}} bal)")
            return
    except AssertionError as e:
        reason = str(e) or "test şərti ödənmədi"
    except NameError as e:
        reason = f"tələb olunan funksiya / dəyişən təyin edilməyib ({{e}})"
    except Exception as e:
        reason = f"{{type(e).__name__}}: {{e}}"
    results[task_id] = 0
    if tid in _errors:
        reason = _errors[tid]
    print(f"❌ Tapşırıq {{tid}}: XƏTA — qaytarılan / çap olunan nəticə gözlənilən nəticəyə uyğun deyil!")
    print(f"   ↳ Səbəb: {{reason}}")


ad_soyad = "..."      # Bura ad və soyadınızı yazın
qrup = "{group}"        # Qrup nömrəniz

'''

PY_FOOTER = '''
# ======================================================================
# YEKUN NƏTİCƏ
# ======================================================================
MAX_POINTS = {max_points}

total = 0
print()
print(f"{{'Tapşırıq':<12}}{{'Nəticə':<10}}{{'Bal':>6}}")
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
    print(f"{{k:<12}}{{status:<10}}{{earned:>3}}/{{p}}")

max_total = sum(MAX_POINTS.values())
print("-" * 30)
print(f"YEKUN İMTAHAN BALI: {{total}} / {{max_total}}  ({{total / max_total * 100:.0f}}%)")
'''


def _comment(text):
    bar = "# " + "=" * 70
    return "\n".join([bar] + [("# " + l).rstrip() for l in text.rstrip().split("\n")] + [bar])


def _plain_md(md):
    return md.replace("**", "").replace("`", "").replace("*", "")


def build_py(v, tasks_info, answers=None):
    """answers verilsə, həll blokları etalon cavablarla doldurulur (yoxlama üçün)."""
    parts = [PY_HEADER.format(v=v, helpers=_helpers_source(), university=UNIVERSITY, course=COURSE, year=YEAR, group=GROUP)]
    max_points = {}
    for kind, tid, title, info, c in tasks_info:
        max_points[tid] = PTS
        if kind == "theory":
            q = _plain_md(info["q"]).replace("\n\n", "\n").replace("```python\n", "").replace("```", "")
            text = f"Tapşırıq {tid}. {title} ({PTS} bal) — Nəzəri sual (yalnız 0 və ya 10 bal)\n\n" + q
            for k in "abcd":
                opt = re.sub(r"</?code>|</?b>|</?i>", "", info["opts"][k]).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                text += f"\n  {k}) " + opt
            parts.append(_comment(text) + "\n")
            val = answers[tid] if answers else ""
            parts.append(f'cavab_{tid} = "{val}"      # düzgün variantın hərfi: "a", "b", "c" və ya "d"\n\n')
            parts.append(f'def test_{tid.lower()}():\n    assert _h(cavab_{tid}) == "{sha(info["right"])}", "seçilmiş cavab düzgün deyil"\n'
                         f'check("{tid}", {PTS}, test_{tid.lower()})\n\n')
        else:
            text = (f"Tapşırıq {tid}. {title} ({PTS} bal) — Kod tapşırığı · {c['cat']}. {CATEGORIES[c['cat']]}\n"
                    f"{grading_text(c)}\n\n" + _plain_md(c["desc"]).replace("```\n", "").replace("```", ""))
            parts.append(_comment(text) + "\n")
            code = answers[tid] if answers else c["starter"]
            parts.append(f'with hell("{tid}"):\n' + "\n".join(("    " + l) if l.strip() else "" for l in code.split("\n")) + "\n\n")
            fn = f"test_{tid.lower()}"
            parts.append(f"def {fn}():\n" + textwrap.indent(c["test"], "    ") + f"\ncheck(\"{tid}\", {PTS}, {fn})\n\n")
    parts.append(PY_FOOTER.format(max_points=repr(max_points)))
    return "\n".join(parts).rstrip() + "\n"


# ----------------------------------------------------------------------
# Xəritə (müəllim üçün)
# ----------------------------------------------------------------------
def write_mapping(mapping, plan, path):
    used = {q for v in plan.values() for _, q, _ in v}
    spare = [t for t in sorted(CODING, key=lambda x: (x[0], num_of(x))) if t not in used]
    lines = ["# Sual bankı → variant xəritəsi (müəllim üçündür)\n",
             f"Mənbə: `proqramlasdirmanin_esaslari_imtahan_suallari_v2.docx` — {COURSE}, {YEAR}, qrup {GROUP}. "
             "Bankda 20 nəzəri və 60 kod yazma sualı var.\n",
             "Hər variantda 10 tapşırıq: **4 nəzəri + 6 praktiki**, hər biri 10 bal, cəmi 100 bal.\n",
             "* **Nəzəri suallar** (Nəzəri Anlayış və Mövzu): 20 sualın hər biri dəqiq bir variantda işlənir; hər variantın 4 nəzəri sualı "
             "ən azı 3 fərqli kateqoriyadandır (bir kateqoriyadan ən çox 2 sual).",
             "* **Kod tapşırıqları**: hər variantda 5 kateqoriyanın (A–E) hamısı + 1 əlavə tapşırıq var.",
             "* Heç bir sual iki variantda təkrarlanmır. Bankda yan-yana olan və ya məzmunca oxşar tapşırıqlar "
             "(məs. C6 və E9, C5 və E10, C7 və E16, C10 və E12) eyni variantda deyil.",
             "* Suallar variantlara bank sırası ilə paylanmayıb; hər variantda tapşırıqların sırası qarışdırılıb "
             "(eyni kateqoriyadan iki tapşırıq ardıcıl gəlmir).\n",
             "Qiymətləndirmə: `0 / 10` — yalnız 0 və ya 10 bal; `0–10 (qismən)` — hər düzgün hissə üçün ayrıca bal. "
             "Yoxlama nəticəyə əsaslanır: funksiya cavabı qaytara və ya çap edə bilər, istənilən düzgün alqoritm qəbul olunur. "
             "*“swapcase olmadan”*, *“rekursiv”*, *“Bubble Sort ilə”*, *“üçüncü dəyişənsiz”*, *“while ilə”* kimi göstərişlər "
             "avtomatik yoxlanılmır — lazım olsa, kodu müəllim panelində özünüz baxın.\n",
             "Qeyd: Word faylındakı E4 nümunəsində *'Salam Baku'* üçün samit sayı 4 yazılıb, düzgün cavab isə 5-dir "
             "(S, l, m, B, k) — tapşırıqda düzgün qiymət (4, 5) istifadə olunub. Eyni şəkildə C16-da 1–100 aralığı üçün "
             "cavab 735 yox, 679-dur (3 + 10 + … + 94, 14 ədəd) — tapşırıqda 679 istifadə olunub.\n"]
    for v, rows in mapping.items():
        npart = sum(1 for r in rows if r[5].startswith("0–10"))
        lines.append(f"\n## Variant {v}  (kod: {npart} qismən, {6 - npart} tapşırıq 0/10; nəzəri: 4 × 0/10)\n\n"
                     "| Tapşırıq | Növ | Bank nömrəsi | Kateqoriya | Mövzu | Qiymətləndirmə | Cavab / funksiya |\n|---|---|---|---|---|---|---|")
        lines += [f"| {t} | {k} | {b} | {c} | {n} | {m} | {a} |" for t, k, b, c, n, m, a in rows]
    lines.append("\n## Ehtiyat kod tapşırıqları (heç bir variantda istifadə olunmayıb)\n")
    lines.append("Təkrar (ehtiyat) imtahan üçün: " + ", ".join(f"[{t}] {CODING[t]['title']}" for t in spare) + ".")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------
# Yoxlama
# ----------------------------------------------------------------------
def verify(data, keys, extra, plan):
    from probes import PROBES
    h = load_harness()
    ok = check_theory_answers()
    print("\n=== YOXLAMA ===")
    used = [q for v in plan.values() for _, q, _ in v]
    ok &= len(used) == len(set(used)) == 50
    for v, seq in plan.items():
        th = [q for k, q, _ in seq if k == "theory"]
        cd = [q for k, q, _ in seq if k == "code"]
        rule = (len(th) == 4 and len({q[0] for q in th}) >= 3 and {q[0] for q in cd} == set(CATEGORIES)
                and len(cd) == 6 and far_apart(cd) and far_apart(th))
        ok &= rule
        print(f"Variant {v}: nəzəri {th} | kod {cd} {'✅' if rule else '❌'}")
    for v, var in data["variants"].items():
        steps, key = var["steps"], keys[v]
        r = h.run_variant(steps, key)["results"]
        total = sum(x["pts"] for x in r.values())
        bad = {k: x["detail"] for k, x in r.items() if not x["ok"]}
        starters = {t["id"]: t["starter"] for t in var["tasks"] if t["kind"] == "code"}
        r0 = h.run_variant(steps, starters)["results"]
        zero = sum(x["pts"] for x in r0.values())
        wrong = {t["id"]: next(l for l in "abcd" if l != key[t["id"]]) for t in var["tasks"] if t["kind"] == "choice"}
        rw = h.run_variant(steps, wrong)["results"]
        wrong_pts = sum(x["pts"] for k, x in rw.items() if k in wrong)
        with tempfile.TemporaryDirectory() as td:
            def run_py(code):
                fp = os.path.join(td, f"variant_{v}.py")
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(code)
                compile(code, fp, "exec")
                rr = subprocess.run([sys.executable, fp], capture_output=True, text=True, encoding="utf-8", timeout=180)
                m = re.search(r"YEKUN İMTAHAN BALI: (\d+) / (\d+)", rr.stdout)
                return (int(m.group(1)) if m else None), rr
            py_full, rf = run_py(build_py(v, extra[v], key))
            py_blank, rb = run_py(build_py(v, extra[v]))
        line_ok = total == 100 and not bad and zero == 0 and wrong_pts == 0 and py_full == 100 and py_blank == 0
        ok &= line_ok
        print(f"Variant {v}: etalon={total}/100 | boş starter={zero} | səhv test cavabları={wrong_pts} | "
              f".py etalon={py_full} | .py boş={py_blank} {'✅' if line_ok else '❌'}")
        if bad:
            print("   səhv tapşırıqlar:", bad)
        if py_full != 100:
            print(rf.stdout[-1500:], rf.stderr[-1500:])
        if py_blank != 0:
            print(rb.stdout[-1500:], rb.stderr[-1500:])
    print("\n--- 60 kod tapşırığı tək-tək (etalon = 10, boş = 0, sınaq həlləri) ---")
    for qid, c in sorted(CODING.items(), key=lambda kv: (kv[0][0], num_of(kv[0]))):
        step = [{"k": "code", "task": "T1", "code": c["starter"]},
                {"k": "test", "ids": ["T1"], "code": "def test_t1():\n" + textwrap.indent(c["test"], "    ") + f"\ncheck(\"T1\", {PTS}, test_t1)"}]
        full = h.run_variant(step, {"T1": c["solution"]})["results"]["T1"]
        blank = h.run_variant(step, {})["results"]["T1"]
        good = full["pts"] == 10 and blank["pts"] == 0
        ok &= good
        line = f"  {'✅' if good else '❌'} {qid:<4} {c['title']:<52} etalon={full['pts']:>2} boş={blank['pts']}"
        if not good:
            line += f"  ({full['detail']})"
        if qid in PROBES:
            code, expected = PROBES[qid]
            got = h.run_variant(step, {"T1": code})["results"]["T1"]
            flag = "✅" if got["pts"] == expected else "❌"
            ok &= got["pts"] == expected
            line += f" | sınaq → {got['pts']} (gözlənilən {expected}) {flag}"
            if got["pts"] != expected:
                line += f"  [{got['detail'][:140]}]"
        print(line)
    print("NƏTİCƏ:", "HAMISI DÜZGÜNDÜR ✅" if ok else "PROBLEM VAR ❌")
    return ok


def main():
    data, keys, mapping, extra, plan = build()
    write_exam_data(data, os.path.join(ROOT, "exam_data.js"))
    write_mapping(mapping, plan, os.path.join(ROOT, "sual_banki_xeritesi.md"))
    for v in VARIANTS:
        code = build_py(v, extra[v])
        compile(code, f"variant_{v}.py", "exec")
        with open(os.path.join(ROOT, f"variant_{v}.py"), "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
    print("Yaradıldı: exam_data.js, variant_A.py ... variant_E.py, sual_banki_xeritesi.md")
    if "--verify" in sys.argv and not verify(data, keys, extra, plan):
        sys.exit(1)


if __name__ == "__main__":
    main()
