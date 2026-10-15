#!/usr/bin/env python3
"""Check local links, fragments, asset locality and expected demo pages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import json

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'docs'

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.remote=[];self.scripts=0;self.inline_styles=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        if tag=='script':self.scripts+=1
        if 'style' in a:self.inline_styles+=1
        for k in ['href','src']:
            if k in a:self.links.append(a[k])

def main():
    sections=json.loads((ROOT/'src/sections.json').read_text(encoding='utf-8'))
    topics=json.loads((ROOT/'src/topics.json').read_text(encoding='utf-8'))
    references=['definitions','regulation-policy','stakeholders','sources-evidence','cases','initiatives','technologies','data-methods']
    expected={'index.html','walkthrough.html',*[key+'.html' for key in sections],*['topic-'+m['id'].replace('.','-')+'.html' for m in topics['modules']],*['reference-'+key+'.html' for key in references]}
    actual={p.name for p in PUBLIC.glob('*.html')}
    assert actual==expected,(actual,expected)
    parsed={}
    for name in sorted(expected):
        p=Links();p.feed((PUBLIC/name).read_text(encoding='utf-8'));parsed[name]=p
        assert p.scripts==0 and p.inline_styles==0,name
        assert 'main' in p.ids,name
    count=0
    for name,p in parsed.items():
        for link in p.links:
            u=urlsplit(link)
            assert not u.scheme and not u.netloc,'Remote URL: '+link
            assert not u.path.startswith('/'),'Root-relative URL: '+link
            target=(PUBLIC/name).parent/unquote(u.path) if u.path else PUBLIC/name
            assert target.resolve().is_relative_to(PUBLIC.resolve()),link
            assert target.is_file(),f'{name}: {link}'
            if u.fragment:
                assert target.name in parsed and unquote(u.fragment) in parsed[target.name].ids,link
            count+=1
    print(f'PASS: {len(expected)} HTML pages, {count} local links/assets, no remote requests or runtime scripts.')

if __name__=='__main__':main()
