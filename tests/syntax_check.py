"""Prueft alle Inline-<script>-Bloecke in app.html mit node --check."""
import re, subprocess, sys, tempfile, os

src = open(sys.argv[1] if len(sys.argv) > 1 else 'app.html', encoding='utf-8').read()
blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', src, re.DOTALL)
failed = 0
with tempfile.TemporaryDirectory() as d:
    for i, code in enumerate(blocks):
        path = os.path.join(d, f'block{i}.js')
        open(path, 'w', encoding='utf-8').write(code)
        r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
        if r.returncode:
            failed += 1
            print(f'Script-Block {i}: Syntaxfehler\n{r.stderr}')
print(f'{len(blocks)} Script-Bloecke geprueft, {failed} fehlerhaft')
sys.exit(1 if failed else 0)
