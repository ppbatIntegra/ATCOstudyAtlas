#!/usr/bin/env python3
"""Regenerate the ready-to-host docs folder. Python 3 standard library only."""
from pathlib import Path
from html import escape
import json, re, shutil

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src'; PUBLIC=ROOT/'docs'
SECTIONS=json.loads((SRC/'sections.json').read_text(encoding='utf-8'))
ICONS=json.loads((SRC/'icons.json').read_text(encoding='utf-8'))
TOPICS=json.loads((SRC/'topics.json').read_text(encoding='utf-8'))
PATHWAYS=['pipeline','shortage','solutions','future']
RESOURCES=['missions','expeditions','artefacts','discoveries','library','encyclopaedia']
REFERENCE_SLUGS=['definitions','regulation-policy','stakeholders','sources-evidence','cases','initiatives','technologies','data-methods']

def topic_url(id):return 'topic-'+id.replace('.','-')+'.html'
def reference_url(i):return 'reference-'+REFERENCE_SLUGS[i]+'.html'
def topic_title(id):return next(m['title'] for m in TOPICS['modules'] if m['id']==id)
def link(url,label):return '<a href="'+escape(url,quote=True)+'">'+escape(label)+'</a>'
def breadcrumbs(parts):
    return '<nav class="atlas-breadcrumb" aria-label="Breadcrumb">'+''.join(('<span aria-hidden="true">›</span>' if i else '')+(link(url,label) if url else '<span aria-current="page">'+escape(label)+'</span>') for i,(label,url) in enumerate(parts))+'</nav>'

def module_links(key):
    number=PATHWAYS.index(key)+1
    modules=[m for m in TOPICS['modules'] if m['id'].startswith(str(number)+'.')]
    rows=''.join('<a class="atlas-module" href="'+topic_url(m['id'])+'"><span class="atlas-number">'+escape(m['id'])+'</span><span><strong>'+escape(m['title'])+'</strong><small>'+('Worked example available' if m['id'] in TOPICS['worked'] else escape(m['outcome']))+'</small></span><span aria-hidden="true">→</span></a>' for m in modules)
    return '<section class="atlas-module-list" aria-label="Pathway modules"><h2>Explore this Pathway</h2><p class="atlas-preview-label">Proposed module structure · Five worked examples are developed across the Atlas.</p>'+rows+'</section>'

def reference_links():
    return '<section class="atlas-module-list"><h2>Shared reference entries</h2>'+''.join('<a class="atlas-module" href="'+reference_url(i)+'"><span>'+icon('book-open')+'</span><span><strong>'+escape(title)+'</strong><small>'+escape(description)+'</small></span><span aria-hidden="true">→</span></a>' for i,(title,description) in enumerate(TOPICS['refs']))+'</section>'

def icon(name):
    nodes=ICONS[name]
    body=''.join('<'+tag+' '+ ' '.join(f'{escape(str(k),quote=True)}="{escape(str(v),quote=True)}"' for k,v in attrs.items())+' />' for tag,attrs in nodes)
    return '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'+body+'</svg>'

def render_icons(markup):
    return re.sub(r'<i data-lucide="([a-z-]+)" aria-hidden="true"></i>',lambda m:icon(m[1]),markup)

def header():
    return '''<header class="atlas-header">
<a class="atlas-brand" href="index.html" aria-label="ATCO Knowledge Atlas home"><span class="atlas-brand-icon">'''+icon('compass')+'''</span><span><span class="atlas-brand-name">ATCO Knowledge Atlas</span><span class="atlas-brand-sub">A European study of the ATCO system</span></span></a>
<span class="atlas-header-note">Workforce · Training · Licensing</span>
</header>'''

def page(title,description,body):
    csp="default-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'; frame-src 'none'"
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="'''+csp+'''">
<meta name="color-scheme" content="light dark">
<meta name="description" content="'''+escape(description,quote=True)+'''">
<title>'''+escape(title)+'''</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/atlas.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<div id="atlas-front-page" aria-label="ATCO Knowledge Atlas">
'''+header()+'''
<main id="main">
'''+body+'''
</main>
<footer class="atlas-footer"><span>One knowledge base. Many ways to explore.</span><span>Concept preview</span></footer>
</div>
</body>
</html>
'''

def section_page(key,section):
    title=escape(section['title'])
    items=''.join('<li><span class="atlas-number">'+f'{i:02d}'+'</span><div><strong>'+escape(item[0])+'</strong><p>'+escape(item[1])+'</p></div></li>' for i,item in enumerate(section['items'],1))
    related_keys=([k for k in PATHWAYS if k!=key] if key in PATHWAYS else ['pipeline','artefacts','encyclopaedia'])
    related_keys=[k for k in related_keys if k!=key]
    related=''.join('<a href="'+k+'.html">'+escape(SECTIONS[k]['title'])+'</a>' for k in related_keys)
    note='<p class="atlas-detail-note">'+escape(section['note'])+'</p>' if section.get('note') else ''
    extra=module_links(key) if key in PATHWAYS else reference_links() if key=='encyclopaedia' else ''
    if key=='library':extra='<section class="atlas-related"><h2>Source records</h2><p>'+link(reference_url(3),'Inspect the study source versions and their status')+'</p></section>'
    if key=='artefacts':extra='<section class="atlas-related"><h2>Explore the demo artefacts</h2><div class="atlas-related-links">'+link('pipeline.html','The pipeline')+link(topic_url('2.7'),'The supply–demand model')+link('solutions.html','Challenges & Solutions')+link(topic_url('4.6'),'Competence domains')+'</div></section>'
    return '<section class="atlas-detail">'+breadcrumbs([('Atlas','index.html'),(section['title'],None)])+ '<a class="atlas-back" href="index.html">'+icon('arrow-left')+'Back to the Atlas</a><div class="atlas-title-line">'+icon(section['icon'])+'<span class="atlas-eyebrow">Explore the Atlas</span></div><h1>'+title+'</h1><p class="atlas-detail-intro">'+escape(section['intro'])+'</p><ul class="atlas-detail-list">'+items+'</ul>'+note+extra+'<p class="atlas-preview-label">Concept preview · Detailed coverage is not yet complete</p><nav class="atlas-related" aria-label="Related Atlas sections"><h2>Continue exploring</h2><div class="atlas-related-links">'+related+'</div></nav></section>'

def topic_page(m):
    id=m['id'];number=int(id.split('.')[0]);pathway=PATHWAYS[number-1];w=TOPICS['worked'].get(id)
    modules=[x for x in TOPICS['modules'] if x['id'].startswith(str(number)+'.')];position=modules.index(m)
    status=w['status'] if w else 'Proposed content outline'
    intro=w['intro'] if w else m['outcome']
    detail='<section class="atlas-topic-block"><h2>'+escape(w['heading'] if w else 'Planned coverage')+'</h2><ul>'+''.join('<li>'+escape(item)+'</li>' for item in (w['items'] if w else m['topics']))+'</ul></section>'
    limit=w['limit'] if w else 'This module shows the proposed scope. Its full explanation and claim-level source mapping remain to be drafted.'
    sources=[
        'F: sections 2.3 and 4.3, Annex F. I: chapter 2 and sections 1.2 and 6.1.',
        'F: sections 2.1–2.2, 4.1, 4.4 and Annex E. I: chapters 1, 3 and 4.',
        'F: sections 4.2–4.4, 5 and Annexes G–K. I: chapters 3 and 5.',
        'W: slides 5–16. C. F: sections 4.3.3–4.3.4 and 5. I: section 6.1.'
    ]
    source=w['source'] if w else sources[number-1]
    related_ids=w['links'] if w else [('2.6' if number==1 else '3.4' if number==2 else '1.6' if number==3 else '4.6')]
    related=''.join(link(topic_url(x),topic_title(x)) for x in related_ids if x!=id)
    navigation=link(topic_url(modules[position-1]['id']),'← Previous module') if position else link(pathway+'.html','Pathway overview')
    navigation+=link(topic_url(modules[position+1]['id']),'Next module →') if position<len(modules)-1 else link(pathway+'.html','Pathway overview')
    return '<article class="atlas-detail">'+breadcrumbs([('Atlas','index.html'),(SECTIONS[pathway]['title'],pathway+'.html'),(m['title'],None)])+'<div class="atlas-eyebrow">'+escape(id)+' · '+escape(status)+'</div><h1>'+escape(m['title'])+'</h1><p class="atlas-detail-intro">'+escape(intro)+'</p>'+detail+'<p class="atlas-evidence">'+escape(limit)+'</p><details class="atlas-source"><summary>Source basis and evidence status</summary><p>'+escape(source)+'</p>'+link(reference_url(3),'Inspect source records')+'</details><nav class="atlas-related" aria-label="Related topics"><h2>Continue across the Atlas</h2><div class="atlas-related-links">'+related+'</div></nav><nav class="atlas-bottom" aria-label="Pathway reading order">'+navigation+'</nav></article>'

def reference_page(i):
    title,items,note=TOPICS['refContent'][i]
    if i==3:
        content=''.join('<section class="atlas-topic-block"><div class="atlas-eyebrow">'+escape(key)+' · '+escape(s[1])+'</div><h2>'+escape(s[0])+'</h2><p>'+escape(s[2])+'</p></section>' for key,s in TOPICS['sources'].items())
    else:content='<section class="atlas-topic-block"><ul>'+''.join('<li>'+escape(t)+'</li>' for t in items)+'</ul></section>'
    example='4.8' if i in [6,5,1] else '1.6'
    return '<article class="atlas-detail">'+breadcrumbs([('Atlas','index.html'),('Encyclopaedia','encyclopaedia.html'),(title,None)])+'<div class="atlas-eyebrow">Shared reference layer</div><h1>'+escape(title)+'</h1>'+content+'<p class="atlas-evidence">'+escape(note)+'</p><nav class="atlas-related" aria-label="Reference in context"><h2>See it in context</h2><div class="atlas-related-links">'+link(topic_url(example),topic_title(example))+'</div></nav></article>'

def walkthrough():
    steps=TOPICS['steps']
    tabs=''.join(link('#step-'+str(i),str(i)+'. '+s['label']) for i,s in enumerate(steps,1))
    body=''.join('<section class="atlas-topic-block" id="step-'+str(i)+'"><div class="atlas-eyebrow">Step '+str(i)+' of 4 · '+escape(s['rel'])+'</div><h2>'+escape(s['q'])+'</h2><p>'+escape(s['body'])+'</p>'+link(topic_url(s['id']),'Open the topic page →')+'</section>' for i,s in enumerate(steps,1))
    return '<article class="atlas-detail">'+breadcrumbs([('Atlas','index.html'),('Connected walkthrough',None)])+'<div class="atlas-eyebrow">Connected walkthrough</div><h1>One issue. Four perspectives.</h1><p class="atlas-detail-intro">Unit training is the starting point. Each Pathway adds a different question to the same knowledge base.</p><nav class="atlas-related-links" aria-label="Walkthrough perspectives">'+tabs+'</nav>'+body+'</article>'

def main():
    (PUBLIC/'assets').mkdir(parents=True,exist_ok=True)
    shutil.copyfile(SRC/'atlas.css',PUBLIC/'assets/atlas.css')
    home=(SRC/'home.html').read_text(encoding='utf-8')
    def card(m):
        attrs,key=m[1],m[2]
        assert key in SECTIONS, key
        attrs=re.sub(r'\s*type="button"','',attrs)
        attrs=attrs.replace(' cursor-interaction','')
        return '<a'+attrs+' href="'+key+'.html">'
    home=re.sub(r'<button([^>]*?)\sdata-section="([a-z]+)">',card,home).replace('</button>','</a>')
    assert '<button' not in home
    home=render_icons(home)
    home=home.replace('</div>\n</div>','<section class="atlas-walkthrough"><h2>Follow one issue across the Atlas</h2><p>Unit training → workforce supply → possible measures → future competence</p>'+link('walkthrough.html','Explore the connected walkthrough →')+'</section></div>\n</div>')
    (PUBLIC/'index.html').write_text(page('ATCO Knowledge Atlas','Explore the ATCO Knowledge Atlas concept and its Pathways.',home),encoding='utf-8')
    for key,section in SECTIONS.items():
        (PUBLIC/(key+'.html')).write_text(page(section['title']+' | ATCO Knowledge Atlas',section['intro'],section_page(key,section)),encoding='utf-8')
    for m in TOPICS['modules']:
        (PUBLIC/topic_url(m['id'])).write_text(page(m['title']+' | ATCO Knowledge Atlas',m['outcome'],topic_page(m)),encoding='utf-8')
    for i,(title,_,__) in enumerate(TOPICS['refContent']):
        (PUBLIC/reference_url(i)).write_text(page(title+' | ATCO Knowledge Atlas',TOPICS['refs'][i][1],reference_page(i)),encoding='utf-8')
    (PUBLIC/'walkthrough.html').write_text(page('Connected walkthrough | ATCO Knowledge Atlas','Follow unit training across the four Atlas Pathways.',walkthrough()),encoding='utf-8')
    favicon=icon('compass').replace('stroke="currentColor"','stroke="#0062A7"').replace('width="22" height="22"','width="32" height="32"')
    (PUBLIC/'assets/favicon.svg').write_text(favicon,encoding='utf-8')
    (PUBLIC/'.nojekyll').touch()
    print('Built 57 static pages in docs/. No runtime JavaScript or external assets required.')

if __name__=='__main__':main()
