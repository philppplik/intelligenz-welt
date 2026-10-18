#!/usr/bin/env python3
"""IW hero: crop to 16:9, export 1600x900 JPEG (+800 thumb) with a subtle brand watermark strip:
bottom-left IW logo (blended), bottom-center 'intelligenz-welt.de', bottom-right label (default 'KI').
Usage: label_image_wm.py <src.png> <slug-name> [--label KI] [--logo path.svg|png] [--outdir images]
Needs Pillow; SVG logos are rasterised with ImageMagick 'convert' (or pass a PNG)."""
import sys, os, argparse, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('name')
ap.add_argument('--label', default='KI'); ap.add_argument('--logo', default=None)
ap.add_argument('--outdir', default=None); ap.add_argument('--site', default='intelligenz-welt.de')
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
logo_path = a.logo or os.path.join(HERE, '..', 'content', 'branding', 'iw-logo.svg')
outdir = a.outdir or os.path.join(HERE, '..', 'content', 'images'); os.makedirs(outdir, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TW, TH = 1600, 900
im = Image.open(a.src).convert('RGB'); w, h = im.size
if w / h > TW / TH:
    nw = int(h * TW / TH); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else:
    nh = int(w * TH / TW); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
im = im.resize((TW, TH), Image.LANCZOS).convert('RGBA')

# logo -> RGBA
if logo_path.lower().endswith('.svg'):
    tmp = tempfile.mktemp(suffix='.png')
    # ImageMagick's renderer drops content under clip-path, so strip it first
    import re
    svg_tmp = tempfile.mktemp(suffix='.svg')
    open(svg_tmp, 'w').write(re.sub(r'\s*clip-path="[^"]*"', '', open(logo_path).read()))
    subprocess.check_call(['convert', '-background', 'none', '-density', '300', svg_tmp, '-resize', '400x400', 'PNG32:' + tmp])
    logo = Image.open(tmp).convert('RGBA'); os.remove(tmp); os.remove(svg_tmp)
else:
    logo = Image.open(logo_path).convert('RGBA')

M = 28; BAR_H = 64; cy = TH - M - BAR_H // 2
# soft dark gradient at the bottom for legibility
grad = Image.new('RGBA', im.size, (0, 0, 0, 0)); gp = grad.load()
gh = 150
for y in range(TH - gh, TH):
    al = int(150 * ((y - (TH - gh)) / gh) ** 1.6)
    for x in range(TW): gp[x, y] = (6, 12, 24, al)
im = Image.alpha_composite(im, grad)

ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
# logo bottom-left, blended (white-ish tint at ~65% so it stays subtle but visible)
lh = BAR_H + 6; lw = int(logo.width * lh / logo.height)
lg = logo.resize((lw, lh), Image.LANCZOS)
al = lg.getchannel('A').point(lambda v: int(v * 0.70))
tint = Image.new('RGBA', lg.size, (255, 255, 255, 255))
tint.putalpha(al)
col = Image.blend(lg.convert('RGBA'), tint, 0.55); col.putalpha(al)
ov.alpha_composite(col, (M, cy - lh // 2))
# center text
f = ImageFont.truetype(FONT, 26)
bb = d.textbbox((0, 0), a.site, font=f); tw_, th_ = bb[2] - bb[0], bb[3] - bb[1]
d.text(((TW - tw_) // 2 - bb[0], cy - th_ // 2 - bb[1]), a.site, font=f, fill=(255, 255, 255, 215))
# right label pill
f2 = ImageFont.truetype(FONT, 26)
bb = d.textbbox((0, 0), a.label, font=f2); lw2, lh2 = bb[2] - bb[0], bb[3] - bb[1]
pad = 14; x1 = TW - M; x0 = x1 - lw2 - 2 * pad; y0 = cy - (lh2 + 2 * pad) // 2; y1 = y0 + lh2 + 2 * pad
d.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=(8, 14, 26, 150))
d.text((x0 + pad - bb[0], y0 + pad - bb[1]), a.label, font=f2, fill=(255, 255, 255, 235))
out = Image.alpha_composite(im, ov).convert('RGB')
p = os.path.join(outdir, a.name + '.jpg')
out.save(p, 'JPEG', quality=84, optimize=True, progressive=True)
out.resize((800, 450), Image.LANCZOS).save(os.path.join(outdir, a.name + '-800.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)
print(p, os.path.getsize(p))
