"""Render the public map and directory from one inventory; no client JS required."""
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'dist/domains.json').read_text())
esc = html.escape
def display(url):
    return url.removeprefix('https://').rstrip('/')
def link(url, label):
    return f'<a href="{esc(url,quote=True)}">{esc(label)}</a>'

groups=data['groups']
surfaces=data['surfaces']
mapped=[s for s in surfaces if s.get('map')]
height=((len(mapped)+2)//3)*138+28
svg=[f'<div class="map"><svg viewBox="0 0 1080 {height}" role="img" aria-labelledby="map-title map-desc"><title id="map-title">Connected websites, tools, and reference</title><desc id="map-desc">{len(mapped)} principal destinations. Every destination, specialist page, and campaign address is listed with its URL in the directory below.</desc>']
for i,s in enumerate(mapped):
    x=22+(i%3)*356; y=22+(i//3)*138
    if i%3<2 and i+1<len(mapped): svg.append(f'<path d="M{x+328} {y+52}h28" stroke="#b7b9c8" stroke-width="2"/>')
    if i+3<len(mapped): svg.append(f'<path d="M{x+164} {y+104}v34" stroke="#b7b9c8" stroke-width="2"/>')
    title=s['title']
    words=title.split(); lines=['']
    for w in words:
        if len(lines[-1])+len(w)>28: lines.append(w)
        else: lines[-1]+=(' ' if lines[-1] else '')+w
    text=''.join(f'<tspan x="{x+16}" dy="{0 if n==0 else 25}">{esc(line)}</tspan>' for n,line in enumerate(lines))
    label=s.get('address') or display(s['url'])
    if len(label)>39: label=urlsplit(s['url']).hostname
    svg.append(f'<a href="{esc(s["url"],quote=True)}" aria-label="{esc(title,quote=True)}"><rect x="{x}" y="{y}" width="328" height="104" rx="3" fill="white" stroke="#413383" stroke-width="2"/><text x="{x+16}" y="{y+31}" font-size="19" font-weight="bold" fill="#201a3e">{text}</text><text x="{x+16}" y="{y+85}" font-size="14" fill="#413383">{esc(label)}</text></a>')
svg.append('</svg></div>')
parts=[f'<section id="web-surfaces" aria-labelledby="web-title"><p class="eyebrow">The connected work</p><h2 id="web-title">Websites, microsites, and useful entrances</h2><p class="lead">{len(surfaces)} destinations across consulting, learning, writing, tools, and reference, plus {len(data["aliases"])} campaign addresses and shortcuts.</p>',''.join(svg),'<nav class="directory-nav" aria-label="Directory sections">']
parts.extend(link('#'+key,title) for key,title in groups)
parts.extend([link('#campaign-addresses','Campaign addresses'),'</nav>'])
for key,title in groups:
    entries=[s for s in surfaces if s['group']==key]
    parts.append(f'<section class="surface-group" id="{key}" aria-labelledby="{key}-title"><h3 id="{key}-title">{esc(title)} <span class="count">{len(entries)}</span></h3><ul class="directory surface-directory">')
    for s in entries:
        parts.append(f'<li><h4>{link(s["url"],s["title"])}</h4><p class="surface-url">{link(s["url"],display(s["url"]))}</p>')
        if key!='library': parts.append(f'<p>{esc(s["purpose"])}</p>')
        if s.get('note'):
            parts.append(f'<p class="domain-note">{link("https://"+s["address"]+"/",s["address"])} — {esc(s["note"])}</p>')
        parts.append('</li>')
    parts.append('</ul></section>')
parts.append('<section class="surface-group" id="campaign-addresses" aria-labelledby="campaign-title"><h3 id="campaign-title">Campaign addresses and shortcuts</h3><p>These names lead into the same body of work. Both the address and its intended destination are shown. A listed destination does not confirm that the redirect is working.</p><div class="alias-table-wrap"><table class="alias-table"><thead><tr><th scope="col">Address</th><th scope="col">Destination</th></tr></thead><tbody>')
for a in data['aliases']:
    parts.append('<tr><th scope="row">'+link('https://'+a['domain']+'/',a['domain'])+'</th><td>'+link(a['destination'],display(a['destination']))+'</td></tr>')
parts.append('</tbody></table></div><details class="reserved"><summary>Other registered names</summary><ul>')
for a in data['reserved']:
    parts.append('<li><b>'+esc(a['domain'])+'</b> — '+esc(a['purpose'])+'</li>')
parts.append('</ul></details></section><p class="inventory-date">Directory updated 6 September 2026.</p></section>')
template=(ROOT/'templates/index.html').read_text()
template=template.replace('<header>Greebling</header>','<a class="skip-link" href="#web-surfaces">Skip to the web directory</a><header><a class="brand" href="/">Greebling</a><nav aria-label="Main navigation"><a href="#web-surfaces">All websites and microsites</a><a href="#reading-title">Greebling writing</a></nav></header>')
template=template.replace('Greebling writing and a map of Benjamin P Taylor’s connected public work.','Greebling writing and the directory of Benjamin P Taylor, RedQuadrant, and PSTA websites, microsites, tools, and publications.')
template=template.replace('Greebling | Essays and connections','Greebling | Writing, websites, and microsites')
(ROOT/'dist/index.html').write_text(template.replace('<!-- WEB_DIRECTORY -->','\n'.join(parts)))
print(f'Rendered {len(mapped)} map destinations, {len(surfaces)} directory entries, and {len(data["aliases"])} campaign addresses.')
