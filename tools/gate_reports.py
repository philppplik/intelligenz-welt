#!/usr/bin/env python3
"""Move generated IW report PDFs out of the public site (and the public repo) into private
Vercel Blob storage. Run after the full site build, before persist/deploy. Fails closed:
if any upload fails, nothing is deleted and the exit code is non-zero, so the workflow
cannot publish public PDFs by accident.
Upload goes through the Lead-Wall backend (HMAC-signed, no Blob token in GitHub).
Env: IW_UPLOAD_SECRET, optional LW_API.
Usage: gate_reports.py [OUT_DIR] [REPO_ROOT]  (defaults: site/out .)"""
import os, re, sys, glob, hmac, hashlib, base64
import urllib.request

API = os.environ.get('LW_API', 'https://daily-hob-newsletter.vercel.app/lw')

def auth(secret, date):
    d = hmac.new(secret.encode(), ('upload:iwreport:' + date).encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(d).decode().rstrip('=')

def upload(f, date, secret):
    req = urllib.request.Request(API + '/api/iwupload?date=' + date, data=open(f, 'rb').read(), method='POST',
        headers={'x-lw-auth': auth(secret, date), 'content-type': 'application/pdf'})
    return urllib.request.urlopen(req, timeout=90).status

def main(out_dir='site/out', repo_root='.'):
    secret = os.environ.get('IW_UPLOAD_SECRET')
    if not secret: sys.exit('gate_reports: IW_UPLOAD_SECRET missing, refusing to publish PDFs')
    out_files = glob.glob(os.path.join(out_dir, 'berichte', '*.pdf'))
    arc_files = glob.glob(os.path.join(repo_root, 'report-archive', '*.pdf'))
    files = out_files + arc_files
    dated = {}
    for f in files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(f))
        if m: dated[m.group(1)] = f  # one file per date is enough, content is identical
    for d, f in sorted(dated.items()):
        try: st = upload(f, d, secret)
        except Exception as e: sys.exit('gate_reports: upload failed %s %s' % (d, e))
        if st != 200: sys.exit('gate_reports: upload failed %s %s' % (d, st))
        print('uploaded', d)
    # Manifest keeps the archive history visible after the PDFs leave the public repo.
    if dated:
        manifest = os.path.join(repo_root, 'report-archive', 'dates.txt')
        os.makedirs(os.path.dirname(manifest), exist_ok=True)
        existing = set()
        if os.path.exists(manifest):
            existing = {l.strip() for l in open(manifest, encoding='utf-8') if l.strip()}
        with open(manifest, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(sorted(existing | set(dated), reverse=True)) + '\n')
    for f in files: os.remove(f)
    html = os.path.join(out_dir, 'berichte', 'tagesausgabe.html')  # public print view would defeat the gate
    if os.path.exists(html): os.remove(html)
    print('removed %d public PDFs' % len(files))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'site/out', sys.argv[2] if len(sys.argv) > 2 else '.')
