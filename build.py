#!/usr/bin/env python3
"""Reads assets/CV.pdf and writes data.json. Run: python build.py"""
import re, json, glob, datetime
from pypdf import PdfReader

HEADS = ["Professional Summary", "Professional Skills", "Tool-Wise Experience",
         "Professional Experience", "Portfolio Projects", "Education", "Certifications"]
HDR = re.compile(r"^(.+?)\s*\|\s*(.+?)\s*\|\s*([A-Z][a-z]{2} \d{4}\s*[–-]\s*(?:Present|[A-Z][a-z]{2} \d{4}))$")
BUL = "•\uf0b7\u2022\uf0a7"

def sections(lines):
    sec, cur = {"header": []}, "header"
    for l in lines:
        h = next((x for x in HEADS if l.strip().lower() == x.lower()), None)
        if h: cur = h; sec[cur] = []
        else: sec[cur].append(l.strip())
    return sec

def clean(l): return l.lstrip(BUL + " -").strip()

def items(lines): return [clean(l) for l in lines if clean(l)]

def bullets(lines):
    out = []
    text = "\n".join(lines)
    for b in BUL: text = text.replace(b, "\n•")
    for l in text.split("\n"):
        l = l.strip()
        if not l: continue
        if l.startswith("•"): out.append(clean(l))
        elif out: out[-1] += " " + l
        else: out.append(l)
    return out

def split_commas(s): return [x.strip() for x in re.split(r",(?![^(]*\))", s) if x.strip()]

def parse_skills(lines):
    groups, cur = [], None
    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if "," not in l and len(l) < 50 and "," in nxt:
            cur = {"group": l, "text": ""}; groups.append(cur)
        elif cur: cur["text"] += " " + l
    out = []
    for g in groups:
        seen, its = set(), []
        for s in split_commas(g["text"]):
            if s.lower() not in seen: seen.add(s.lower()); its.append(s)
        out.append({"group": g["group"], "items": its})
    return out

def parse_experience(lines):
    jobs, cur, buf = [], None, []
    def flush():
        if cur is not None:
            cur["bullets"] = bullets(buf)
    for l in lines:
        m = HDR.match(l)
        if m:
            flush(); buf = []
            comp = m.group(2)
            place = ""
            if "," in comp: comp, place = [x.strip() for x in comp.rsplit(",", 1)]
            cur = {"role": m.group(1), "company": comp, "place": place, "period": m.group(3), "tools": []}
            jobs.append(cur)
        elif cur is not None and l.lower().startswith("tools:"):
            cur["tools"] = split_commas(l[6:])
        elif cur is not None:
            buf.append(l)
    flush()
    return jobs

def parse_kpis(summary, jobs):
    out, seen = [], set()
    y = re.search(r"(\d+(?:\.\d+)?\+?)\s*years", summary)
    if y: out.append({"value": y.group(1) + " yrs", "label": "Years of experience"})
    cands = [(s.strip(), "") for s in re.split(r"(?<=\.)\s+", summary)]
    for j in jobs:
        cands += [(b, j["company"]) for b in j["bullets"]]
    for text, tag in cands:
        m2 = re.search(r"from (\d+) (?:hours )?to (?:under|<)\s*(\d+) hours", text)
        vals = []
        if m2: vals.append("%sh → <%sh" % (m2.group(1), m2.group(2)))
        for m in re.finditer(r"(\d+(?:\.\d+)?\+?)\s*(%|hours)", text):
            if m2 and m.group(2) == "hours": continue
            vals.append(m.group(1) + ("%" if m.group(2) == "%" else " hrs"))
        for v in vals[:1]:
            key = v + text[:20]
            if key in seen: continue
            seen.add(key)
            out.append({"value": v, "label": text.rstrip("."), "tag": tag})
    return out[:8]

def main():
    pdfs = glob.glob("assets/CV.pdf") or glob.glob("assets/*.pdf")
    if not pdfs: raise SystemExit("Put your CV in assets/CV.pdf")
    rd = PdfReader(pdfs[0])
    lines = [l for p in rd.pages for l in (p.extract_text() or "").split("\n")]
    sec = sections(lines)
    head = [l for l in sec["header"] if l]
    contact = " ".join(head[2:])
    email = (re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", contact) or [None])[0]
    phone = (re.search(r"\+?\d[\d\s-]{8,}\d", contact) or [None])[0]
    loc = re.split(r"\|", contact)[0].strip() if "|" in contact else ""

    uris = []
    for p in rd.pages:
        an = []
        for a in p.get("/Annots") or []:
            a = a.get_object(); u = (a.get("/A") or {}).get("/URI")
            if u and not u.startswith(("mailto:", "tel:")):
                r = a.get("/Rect") or [0, 0, 0, 0]
                an.append((-float(r[3]), float(r[0]), u))
        uris += [u for _, _, u in sorted(an)]
    links = {}
    for u in uris[:3]:
        k = "linkedin" if "linkedin" in u else "github" if "github.com" in u else "portfolio"
        links[k] = u
    projs = items(sec.get("Portfolio Projects", []))
    plinks = uris[3:]
    projects = []
    for i, p in enumerate(projs):
        p = re.sub(r"\s*View Project\s*$", "", p).strip()
        projects.append({"name": p, "url": plinks[i] if i < len(plinks) else ""})

    summary = " ".join(sec.get("Professional Summary", []))
    jobs = parse_experience(sec.get("Professional Experience", []))
    edu = []
    for e in items(sec.get("Education", [])):
        a = [x.strip() for x in e.split("—", 1)]
        deg, rest = a[0], (a[1] if len(a) > 1 else "")
        inst, *extra = [x.strip() for x in rest.split("|")]
        edu.append({"degree": deg, "institution": inst, "extra": " · ".join(extra)})
    tools = []
    for t in items(sec.get("Tool-Wise Experience", [])):
        m = re.match(r"(.+?)\s*[–-]\s*([\d.]+\s*\w+)$", t)
        if m: tools.append({"tool": m.group(1), "years": m.group(2)})

    data = {
        "name": head[0] if head else "", "headline": head[1] if len(head) > 1 else "",
        "email": email, "phone": phone, "location": loc, "links": links,
        "summary": summary, "kpis": parse_kpis(summary, jobs),
        "skills": parse_skills(sec.get("Professional Skills", [])),
        "toolYears": tools, "experience": jobs, "projects": projects,
        "education": edu, "certs": items(sec.get("Certifications", [])),
        "generated": datetime.date.today().isoformat(),
    }
    json.dump(data, open("data.json", "w"), indent=1, ensure_ascii=False)
    print("OK:", len(jobs), "jobs,", len(data["skills"]), "skill groups,", len(projects), "projects,",
          len(data["kpis"]), "KPIs,", len(data["certs"]), "certs")

main()
