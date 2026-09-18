from pathlib import Path
import argparse, re, shutil
p=argparse.ArgumentParser();p.add_argument('--base-path',default='');args=p.parse_args()
base=args.base_path.rstrip('/')
source=Path('dist');target=Path('_site')
if target.exists():raise SystemExit('_site already exists; use a clean checkout')
shutil.copytree(source,target)
for path in target.rglob('*'):
    if path.is_file() and path.suffix.lower() in {'.html','.css','.js','.json','.webmanifest','.svg'}:
        text=path.read_text(encoding='utf-8')
        if base:
            text=re.sub(r"([\"'])/(?!/)([^\"'<>\r\n]*)\1",lambda m:m[1]+base+'/'+m[2]+m[1],text)
            text=re.sub(r'url\(/(?!/)', 'url('+base+'/',text)
        path.write_text(text,encoding='utf-8')
(target/'.nojekyll').touch()
print('Prepared',sum(p.is_file() for p in target.rglob('*')),'files for',base or '/')
