"""Render the public map and directory from one inventory; no client JS required."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'dist/domains.json').read_text())
esc = html.escape
def display(url):
    return url.removeprefix('https://').rstrip('/')
def link(url, label):
    return f'<a href="{esc(url,quote=True)}">{esc(label)}</a>'

groups=data['groups']
surfaces=data['surfaces']
map_excluded_groups={'library','elsewhere'}
mapped=[
    s for s in surfaces
    if s.get('map') is True
    or (s.get('map') is not False and s['group'] not in map_excluded_groups)
]
map_clusters=[]
for key,title in groups:
    entries=[s for s in mapped if s['group']==key]
    if not entries:
        continue
    items=[]
    for s in entries:
        address=s.get('address') or display(s['url'])
        items.append(
            f'<li>{link(s["url"],s["title"])}'
            f'<span>{esc(address)}</span></li>'
        )
    map_clusters.append(
        f'<section class="map-cluster map-{esc(key)}" aria-labelledby="map-{esc(key)}-title">'
        f'<h3 id="map-{esc(key)}-title">{link("#"+key,title)} '
        f'<span class="map-count">{len(entries)}</span></h3>'
        f'<ul>{"".join(items)}</ul></section>'
    )
map_html=(
    f'<div class="map-summary"><h3>The whole public estate</h3>'
    f'<p>{len(mapped)} substantial sites, microsites, tools, exercises, programmes, '
    f'offers, and reference surfaces, grouped by what they are for. '
    f'Library subdivisions and external publishing profiles remain in the full directory below.</p></div>'
    f'<div class="estate-map">{"".join(map_clusters)}</div>'
)
parts=[f'<section id="web-surfaces" aria-labelledby="web-title"><p class="eyebrow">The connected work</p><h2 id="web-title">Websites, microsites, and useful entrances</h2><p class="lead">{len(surfaces)} destinations across consulting, learning, writing, tools, and reference, plus {len(data["aliases"])} campaign addresses and shortcuts.</p>',map_html,'<nav class="directory-nav" aria-label="Directory sections">']
parts.extend(link('#'+key,title) for key,title in groups)
parts.extend([link('#campaign-addresses','Campaign addresses'),'</nav>'])
for key,title in groups:
    entries=[s for s in surfaces if s['group']==key]
    parts.append(f'<section class="surface-group" id="{key}" aria-labelledby="{key}-title"><h3 id="{key}-title">{esc(title)} <span class="count">{len(entries)}</span></h3><ul class="directory surface-directory">')
    for s in entries:
        parts.append(f'<li><h4>{link(s["url"],s["title"])}</h4><p class="surface-url">{link(s["url"],display(s["url"]))}</p>')
        if key!='library': parts.append(f'<p>{esc(s["purpose"])}</p>')
        if s.get('note'):
            parts.append(f'<p class="domain-note">{link("https://"+s["address"]+"/",s["address"])}; {esc(s["note"])}</p>')
        parts.append('</li>')
    parts.append('</ul></section>')
parts.append('<section class="surface-group" id="campaign-addresses" aria-labelledby="campaign-title"><h3 id="campaign-title">Campaign addresses and shortcuts</h3><p>These names lead into the same body of work. Both the address and its intended destination are shown. A listed destination does not confirm that the redirect is working.</p><div class="alias-table-wrap"><table class="alias-table"><thead><tr><th scope="col">Address</th><th scope="col">Destination</th></tr></thead><tbody>')
for a in data['aliases']:
    parts.append('<tr><th scope="row">'+link('https://'+a['domain']+'/',a['domain'])+'</th><td>'+link(a['destination'],display(a['destination']))+'</td></tr>')
parts.append('</tbody></table></div><details class="reserved"><summary>Other registered names</summary><ul>')
for a in data['reserved']:
    parts.append('<li><b>'+esc(a['domain'])+'</b>; '+esc(a['purpose'])+'</li>')
updated_year,updated_month,updated_day=data['updated'].split('-')
month_names={'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08':'August','09':'September','10':'October','11':'November','12':'December'}
updated_label=f'{int(updated_day)} {month_names[updated_month]} {updated_year}'
parts.append(f'</ul></details></section><p class="inventory-date">Directory updated {updated_label}.</p></section>')
template=(ROOT/'templates/index.html').read_text()
template=template.replace('<header>Greebling</header>','<a class="skip-link" href="#web-surfaces">Skip to the web directory</a><header><a class="brand" href="/">Greebling</a><nav aria-label="Main navigation"><a href="#web-surfaces">All websites and microsites</a><a href="#reading-title">Greebling writing</a></nav></header>')
template=template.replace('Greebling writing and a map of Benjamin P Taylor’s connected public work.','Greebling writing and the directory of Benjamin P Taylor, RedQuadrant, and PSTA websites, microsites, tools, and publications.')
template=template.replace('Greebling | Essays and connections','Greebling | Writing, websites, and microsites')
(ROOT/'dist/index.html').write_text(template.replace('<!-- WEB_DIRECTORY -->','\n'.join(parts)))
print(f'Rendered {len(mapped)} map destinations, {len(surfaces)} directory entries, and {len(data["aliases"])} campaign addresses.')
