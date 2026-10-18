import json,re,html,urllib.request,datetime,email.utils,xml.etree.ElementTree as ET,hashlib
UA={'User-Agent':'Mozilla/5.0 (compatible; SiteBuild/1.0)'}
def get(u,t=15):
    try:
        return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read()
    except Exception as e:
        print('FAIL',u,e); return None
def strip(s):
    return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s or ''))).strip()
def feed(u,src,limit=12):
    b=get(u); out=[]
    if not b: return out
    try: root=ET.fromstring(b)
    except Exception as e: print('XML',u,e); return out
    ns={'a':'http://www.w3.org/2005/Atom'}
    items=root.findall('.//item')
    if items:
        for it in items[:limit]:
            d=it.findtext('pubDate') or ''
            try: ts=email.utils.parsedate_to_datetime(d).timestamp()
            except: ts=0
            out.append(dict(title=strip(it.findtext('title')),url=(it.findtext('link') or '').strip(),sum=strip(it.findtext('description'))[:220],ts=ts,src=src))
    else:
        for it in root.findall('a:entry',ns)[:limit]:
            l=it.find('a:link',ns); d=it.findtext('a:updated',namespaces=ns) or it.findtext('a:published',namespaces=ns) or ''
            try: ts=datetime.datetime.fromisoformat(d.replace('Z','+00:00')).timestamp()
            except: ts=0
            out.append(dict(title=strip(it.findtext('a:title',namespaces=ns)),url=l.get('href') if l is not None else '',sum=strip(it.findtext('a:summary',namespaces=ns))[:220],ts=ts,src=src))
    return [o for o in out if o['title'] and o['url']]
def fmtd(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M') if ts else ''
def esc(s): return html.escape(s or '',quote=True)
def merge_archive(path,new):
    try: arch=json.load(open(path))
    except: arch=[]
    seen={a['url'] for a in arch}
    for n in new:
        if n['url'] not in seen: arch.append(n); seen.add(n['url'])
    arch.sort(key=lambda x:-x['ts'])
    return arch[:2000]
