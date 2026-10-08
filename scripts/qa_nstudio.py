#!/usr/bin/env python3
"""QA pre-entrega N-STUDIO. Uso: python3 qa_nstudio.py <carpeta> --modo demo|final
Solo librería estándar. Ignora los comentarios HTML. Sale con código 1 si hay errores críticos."""
import sys, re, json, os, argparse

ap = argparse.ArgumentParser()
ap.add_argument("carpeta")
ap.add_argument("--modo", choices=["demo", "final"], required=True)
a = ap.parse_args()

crit, warn, ok = [], [], []
def C(m): crit.append(m)
def W(m): warn.append(m)

def img_size(path):
    try:
        with open(path, "rb") as f:
            d = f.read(65536)
        if d[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(d[16:20], "big"), int.from_bytes(d[20:24], "big")
        if d[:4] == b"RIFF" and d[8:12] == b"WEBP":
            if d[12:16] == b"VP8X":
                return 1 + int.from_bytes(d[24:27], "little"), 1 + int.from_bytes(d[27:30], "little")
            if d[12:16] == b"VP8 ":
                return int.from_bytes(d[26:28], "little") & 0x3FFF, int.from_bytes(d[28:30], "little") & 0x3FFF
        if d[:2] == b"\xff\xd8":
            i = 2
            while i < len(d) - 9:
                if d[i] != 0xFF: i += 1; continue
                m = d[i + 1]
                if m in (0xC0, 0xC1, 0xC2):
                    return int.from_bytes(d[i + 7:i + 9], "big"), int.from_bytes(d[i + 5:i + 7], "big")
                i += 2 + int.from_bytes(d[i + 2:i + 4], "big")
    except Exception:
        pass
    return None

root = a.carpeta
htmls, total = [], 0
for dp, _, fs in os.walk(root):
    for f in fs:
        p = os.path.join(dp, f); s = os.path.getsize(p); total += s
        ext = f.lower().rsplit(".", 1)[-1]
        rel = os.path.relpath(p, root)
        if ext == "html": htmls.append(p)
        if re.search(r"(viejo|old|backup|copia|\(\d\))", f, re.I): C(f"Copia o duplicado en el sitio: {rel} (se publicaría; bórrala o renómbrala)")
        if ext in ("mp4", "mov", "webm") and s > 8e6: C(f"Video pesado ({s/1e6:.1f} MB): {rel} → YouTube con fachada o comprimir < 8 MB")
        if ext in ("jpg", "jpeg", "png", "webp") and s > 300e3: W(f"Imagen > 300 KB ({s/1e3:.0f} KB): {rel}")

if not htmls: C("No hay archivos .html en la carpeta"); htmls = []
for name in ("robots.txt", "sitemap.xml"):
    if not os.path.exists(os.path.join(root, name)): C(f"Falta {name}")
if a.modo == "final" and not os.path.exists(os.path.join(root, ".htaccess")):
    C("Falta .htaccess (HTTPS + www→sin www + caché + seguridad)")

PLACEHOLDER = re.compile(r"TU[-_ ]ID|TU-[A-Z]|\[(FOTO|DATO|TEXTO|IMAGEN|PENDIENTE)[^\]]*\]|lorem ipsum|XXXXX|59100000000|example\.com|REEMPLAZAR|TODO:", re.I)

for p in htmls:
    rel = os.path.relpath(p, root)
    h = re.sub(r"<!--.*?-->", "", open(p, encoding="utf-8", errors="ignore").read(), flags=re.S)
    for m in set(x.group(0) for x in PLACEHOLDER.finditer(h)):
        C(f"{rel}: marcador sin rellenar «{m}»")
    for s in re.findall(r'data-website-id="([^"]*)"', h):
        if not re.fullmatch(r"[0-9a-f-]{36}", s): C(f"{rel}: ID de analítica inválido «{s}» (rellenar o borrar el script)")
    if re.search(r'\sstyle="|\son[a-z]+="|<style[\s>]', h): C(f"{rel}: style=\"\", <style> u onclick= en el HTML: la CSP los bloquea")
    for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", h, re.S):
        if body.strip() and "ld+json" not in attrs: C(f"{rel}: <script> inline: la CSP lo bloquea (mover a assets/app.js)")
    noidx = bool(re.search(r'<meta[^>]+name="robots"[^>]+noindex', h, re.I))
    if a.modo == "demo" and not noidx: C(f"{rel}: demo SIN noindex")
    if a.modo == "final" and noidx: C(f"{rel}: web final CON noindex (Google no la indexará)")
    if a.modo == "final" and re.search(r"netlify\.app", h): C(f"{rel}: quedan URLs de netlify.app en la versión final")
    for ref in re.findall(r'(?:href|src)="((?!https?:|//|contenido/)[^"?]+\.(?:css|js))"', h):
        W(f"{rel}: «{ref}» sin versión → usar {ref}?v=AAAAMMDD (la caché del navegador dura días)")
    lang = re.search(r'<html[^>]*lang="([^"]*)"', h)
    if not lang: C(f"{rel}: falta lang en <html>")
    elif lang.group(1) != "es-BO": W(f"{rel}: lang=\"{lang.group(1)}\" → usar es-BO (o el del país del cliente)")
    if len(re.findall(r"<h1[\s>]", h)) != 1: C(f"{rel}: debe haber exactamente un <h1>")
    for tag in ("<title>", 'name="description"', 'rel="canonical"', 'property="og:image"'):
        if tag not in h: C(f"{rel}: falta {tag}")
    if rel == "index.html":
        card = re.search(r'name="twitter:card" content="([^"]*)"', h)
        if not card or card.group(1) != "summary_large_image": W(f"{rel}: twitter:card debe ser summary_large_image")
        og = re.search(r'property="og:image" content="([^"]*)"', h)
        if og:
            local = os.path.join(root, re.sub(r"^https?://[^/]+/", "", og.group(1)))
            sz = img_size(local) if os.path.exists(local) else None
            if not sz:
                mw = re.search(r'og:image:width" content="(\d+)"', h); mh = re.search(r'og:image:height" content="(\d+)"', h)
                if mw and mh: sz = (int(mw.group(1)), int(mh.group(1)))
            if sz and (sz[0] < 1200 or sz[1] < 630 or sz[0] < sz[1]): C(f"og:image es {sz[0]}×{sz[1]} → usar imagen horizontal 1200×630")
            elif not sz: W(f"No pude medir la og:image ({og.group(1)}); verifica que sea 1200×630")
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        if not lds: C(f"{rel}: falta JSON-LD de LocalBusiness")
        for ld in lds:
            try:
                d = json.loads(ld)
                for k in ("geo", "sameAs", "telephone", "address", "openingHours"):
                    if k not in d and not (k == "openingHours" and "openingHoursSpecification" in d):
                        W(f"JSON-LD sin «{k}»")
                if "aggregateRating" in d: C("JSON-LD con aggregateRating propio: Google lo prohíbe para el propio negocio")
            except Exception as e:
                C(f"JSON-LD inválido: {e}")
    for aTag in re.findall(r"<a[^>]*>", h):
        if re.search(r"wa\.me|api\.whatsapp", aTag) and "_blank" not in aTag:
            W(f"{rel}: enlaces de WhatsApp sin target=\"_blank\" rel=\"noopener\""); break
    for m in re.finditer(r"wa\.me/(\d+)", h):
        if not re.fullmatch(r"591[67]\d{7}|54\d{10,11}|34\d{9}", m.group(1)):
            W(f"{rel}: número de WhatsApp con formato raro: {m.group(1)}"); break
    for v in re.findall(r"<video[^>]*>", h):
        if 'preload="none"' not in v: W(f"{rel}: <video> sin preload=\"none\"")
        if "poster=" not in v: W(f"{rel}: <video> sin poster")
    txt = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S))
    for m in re.finditer(r"\d[,.]\d\s*(?:sobre|/)\s*5|\+?\d{2,}\s*(?:años|pacientes|clientes|cirugías|reseñas)|n[º°]\s*1|el mejor", txt, re.I):
        W(f"{rel}: afirmación a verificar con fuente y fecha: «{m.group(0).strip()}»")

print(f"\nQA N-STUDIO · modo {a.modo} · {len(htmls)} HTML · {total/1e6:.1f} MB en total\n")
for m in crit: print("🔴", m)
for m in dict.fromkeys(warn): print("🟡", m)
if not crit and not warn: print("✅ Todo correcto")
print(f"\n{len(crit)} críticos · {len(set(warn))} avisos")
sys.exit(1 if crit else 0)
