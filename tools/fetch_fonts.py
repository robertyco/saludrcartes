import re
import urllib.request
from pathlib import Path

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
FONT_DIR = Path("assets/fonts")
FONT_DIR.mkdir(parents=True, exist_ok=True)

families = {
    "fraunces": "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..700&display=swap",
}

for family, url in families.items():
    request = urllib.request.Request(url, headers=UA)
    css = urllib.request.urlopen(request, timeout=30).read().decode("utf-8")
    blocks = re.findall(r"/\* ([a-z-]+) \*/\s*@font-face \{(.*?)\}", css, re.S)
    for subset, block in blocks:
        if subset not in ("latin", "latin-ext"):
            continue
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        src = re.search(r"src:\s*url\((https://[^)]+)\)", block).group(1)
        out = FONT_DIR / f"{family}-{subset}-{style}.woff2"
        urllib.request.urlretrieve(src, out)
        print(out, out.stat().st_size)
