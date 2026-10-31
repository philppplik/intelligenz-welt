import unittest,sys,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import model_rich as m
class ModelRichTests(unittest.TestCase):
 def test_visible_faq_matches_schema(self):
  d=json.loads((ROOT/'content/portraits.json').read_text())
  a=[x for x in d['models'] if x.get('rich_model')];self.assertEqual(len(a),23)
  for x in a:
   faq=x['rich_model'].get('faq') or []
   text=m.render(x,d,ROOT.name=='kfb')
   schemas=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
   fq=[s for s in schemas if s.get('@type')=='FAQPage']
   if faq:
    self.assertEqual(len(fq),1,x['slug']);self.assertEqual(len(fq[0]['mainEntity']),len(faq),x['slug'])
    for q,_a in faq:self.assertIn(q,text,x['slug'])
   else:self.assertEqual(fq,[],x['slug'])
 def test_price_caveats(self):
  d=json.loads((ROOT/'content/portraits.json').read_text())
  def num(v):return isinstance(v,(int,float))
  for x in d['models']:
   if not x.get('rich_model'):continue
   t=m.render(x,d,True);r=x['rich_model']
   self.assertNotIn('None',t,x['slug'])
   if num(r.get('input')) and num(r.get('output')):
    self.assertIn('Preisstand',t,x['slug']);self.assertIn(r.get('price_currency','USD'),t,x['slug'])
    self.assertIn(r.get('price_unit','je 1 Mio. Texttoken'),t,x['slug'])
   else:self.assertNotIn('Standard-Eingabe',t,x['slug'])
   if x['slug']=='gpt-6-astra':
    self.assertIn('Preisstand 19.10.2026',t);self.assertIn('Batch',t);self.assertIn('Cache',t)
 def test_no_unverified_typo_pages(self):
  d=json.loads((ROOT/'content/portraits.json').read_text());self.assertFalse(any('atsra' in x['slug'] or 'flable' in x['slug'] for x in d['models']))
if __name__=='__main__':unittest.main()
