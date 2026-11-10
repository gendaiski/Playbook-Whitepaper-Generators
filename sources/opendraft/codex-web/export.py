import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
from utils.export_professional import export_pdf,export_docx,export_latex
source,out=map(Path,sys.argv[1:]);results={}
for ext,fn in [('pdf',export_pdf),('docx',export_docx),('tex',export_latex)]:
 results[ext]=fn(source,out/('document.'+ext))
print(results)
if not all(results.values()):raise SystemExit(1)
