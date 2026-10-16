"""Build the architecture PDF with local matplotlib and a TeX installation."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', '/tmp/steam-architecture-matplotlib')
subprocess.run([sys.executable, str(ROOT/'render_figures.py')], cwd=ROOT, check=True)
build = ROOT/'build'
build.mkdir(exist_ok=True)
for run in range(3):
    result = subprocess.run([
        'pdflatex', '-interaction=nonstopmode', '-halt-on-error',
        '-output-directory=build', 'steam_patch_intelligence_architecture.tex'
    ], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (build/f'pass-{run+1}.txt').write_text(result.stdout)
    if result.returncode:
        print(result.stdout[-9000:])
        raise SystemExit(result.returncode)
pdf = build/'steam_patch_intelligence_architecture.pdf'
target = ROOT/pdf.name
target.write_bytes(pdf.read_bytes())
print(target)
print(f'{target.stat().st_size:,} bytes')
