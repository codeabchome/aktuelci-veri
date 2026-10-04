# Aktüelci veri aynası: aktuelci.pages.dev'deki veriyi bu reponun GitHub Pages'ine kopyalar.
# (Bazı internet sağlayıcıları *.pages.dev'i engelliyor; uygulama açamazsa buradan okur.)
import json, os, pathlib, shutil, time, urllib.request

KOK = "https://aktuelci.pages.dev/"
SITE, ONCEKI = pathlib.Path("site"), pathlib.Path("onceki")

def al(yol):
    if yol.endswith(".json"): yol += f"?t={int(time.time())}"   # CDN önbelleğini atla
    req = urllib.request.Request(KOK + yol, headers={"User-Agent": "aktuelci-ayna"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

katalog = al("katalog.json")
marketler = al("marketler.json")
degisti = any(not (ONCEKI / ad).exists() or (ONCEKI / ad).read_bytes() != veri
              for ad, veri in (("katalog.json", katalog), ("marketler.json", marketler)))
with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
    f.write(f"degisti={'true' if degisti else 'false'}\n")
if not degisti:
    print("veri ayni, yayin yok"); raise SystemExit(0)

dosyalar = {"gizlilik.html"}
for b in json.loads(katalog)["brosurler"]:
    for u in [b.get("kk"), b.get("kapak"), *(b.get("sayfalar") or [])]:
        if u and not u.startswith("http"): dosyalar.add(u)
yeni = 0
for y in sorted(dosyalar):
    hedef = SITE / y; hedef.parent.mkdir(parents=True, exist_ok=True)
    o = ONCEKI / y
    if y.startswith(("s/", "k/")) and o.exists():
        shutil.copy2(o, hedef)          # görseller değişmez, tekrar indirme
    else:
        hedef.write_bytes(al(y)); yeni += 1
(SITE / "katalog.json").write_bytes(katalog)
(SITE / "marketler.json").write_bytes(marketler)
(SITE / ".nojekyll").touch()
print(f"{len(dosyalar)} dosya, {yeni} yeni indirildi")
