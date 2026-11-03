from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = [
    ('<a class="brand" href="#/" aria-label="saludrcartes, ir al inicio">',
     '<a class="brand" href="#/" aria-label="saludrcartes">'),
    ('<button class="search-trigger" type="button" id="search-trigger" aria-label="Buscar en el registro clínico" aria-haspopup="dialog">',
     '<button class="search-trigger" type="button" id="search-trigger" aria-label="Buscar en el registro clínico, atajo Ctrl K" aria-haspopup="dialog">'),
    ('<a class="emergency-cta" href="#/categoria/emergencia" aria-label="Ir a contactos de emergencia">',
     '<a class="emergency-cta" href="#/categoria/emergencia" aria-label="Emergencia, contactos de urgencia">'),
    ('<button class="user-trigger" type="button" id="user-trigger" aria-label="Menú de cuenta"',
     '<button class="user-trigger" type="button" id="user-trigger" aria-label="Menú de cuenta: RC"'),
    ('<span class="avatar" id="user-initials">RC</span>',
     '<span class="avatar" id="user-initials" aria-hidden="true">RC</span>'),
]

for old, new in replacements:
    if old not in s:
        print('MISSING:', old[:70])
        continue
    s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('patched index.html')