# Aktüelci veri aynası: aktuelci.pages.dev'deki veriyi bu reponun GitHub Pages'ine kopyalar.
# (Bazı internet sağlayıcıları *.pages.dev'i engelliyor; uygulama açamazsa buradan okur.)
import json, os, pathlib, shutil, urllib.request

KOK = "https://aktuelci.pages.dev/"
SITE, ONCEKI = pathlib.Path("site"), pathlib.Path("onceki")

def al(yol):
    req = urllib.request.Request(KOK + yol, headers={"User-Agent": "aktuelci-ayna"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

katalog = al("katalog.json")
eski = ONCEKI / "katalog.json"
degisti = not eski.exists() or eski.read_bytes() != katalog
with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
    f.write(f"degisti={'true' if degisti else 'false'}\n")
if not degisti:
    print("katalog ayni, yayin yok"); raise SystemExit(0)

dosyalar = {"marketler.json", "gizlilik.html"}
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
(SITE / ".nojekyll").touch()
print(f"{len(dosyalar)} dosya, {yeni} yeni indirildi")
