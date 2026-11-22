"""Render the public map and directory from one inventory; no client JS required."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'dist/domains.json').read_text(encoding='utf-8'))
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
    '<details class="map-index"><summary>Compact index of websites and tools</summary>'
    f'<div class="estate-map">{"".join(map_clusters)}</div></details>'
)
parts=[f'<section id="web-surfaces" aria-labelledby="web-title"><h2 id="web-title">Website directory</h2><p>Browse {len(surfaces)} websites, programmes, articles, and tools from my work and from the organisations I work with. Choose a subject to see the links and descriptions.</p>',map_html,'<nav class="directory-nav" aria-label="Directory sections">']
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
parts.append('<section class="surface-group" id="campaign-addresses" aria-labelledby="campaign-title"><h3 id="campaign-title">Campaign addresses and shortcuts</h3><p>The second column links directly to the intended destination. Use it if the shorter address fails to open.</p><div class="alias-table-wrap"><table class="alias-table"><thead><tr><th scope="col">Address</th><th scope="col">Destination</th></tr></thead><tbody>')
for a in data['aliases']:
    parts.append('<tr><th scope="row">'+link('https://'+a['domain']+'/',a['domain'])+'</th><td>'+link(a['destination'],display(a['destination']))+'</td></tr>')
parts.append('</tbody></table></div><details class="reserved"><summary>Other registered names</summary><ul>')
for a in data['reserved']:
    parts.append('<li><b>'+esc(a['domain'])+'</b>; '+esc(a['purpose'])+'</li>')
updated_year,updated_month,updated_day=data['updated'].split('-')
month_names={'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08':'August','09':'September','10':'October','11':'November','12':'December'}
updated_label=f'{int(updated_day)} {month_names[updated_month]} {updated_year}'
parts.append(f'</ul></details></section><p class="inventory-date">Directory updated {updated_label}.</p></section>')
template=(ROOT/'templates/index.html').read_text(encoding='utf-8')
roles = data.get('stewardship', {}).get('coreRoles', [])
role_html = '<section class="surface-group" id="start-here"><h2>Where I write and work</h2><ul class="directory surface-directory">'
for role in roles:
    role_html += '<li><h3>' + link(role['url'],role['title']) + '</h3><p>' + esc(role['purpose']) + '</p></li>'
role_html += '</ul><p><a href="stewardship.json">Site owners and maintenance notes (JSON)</a></p></section>'
(ROOT/'dist/index.html').write_text(template.replace('<!-- ESTATE_ROLES -->', role_html).replace('<!-- WEB_DIRECTORY -->','\n'.join(parts)), encoding='utf-8')
print(f'Rendered {len(mapped)} map destinations, {len(surfaces)} directory entries, and {len(data["aliases"])} campaign addresses.')
