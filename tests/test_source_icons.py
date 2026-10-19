import os, re, subprocess, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SourceIcons(unittest.TestCase):
    def test_every_archive_source_has_local_icon_and_no_hotlinks(self):
        import json
        src = {i['src'] for i in json.load(open(ROOT + '/data/ai_archive.json'))}
        for s in src:
            slug = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
            self.assertTrue(os.path.isfile('%s/site/source-icons/%s.png' % (ROOT, slug)), s)
        out = ROOT + '/site/out/index.html'
        if os.path.exists(out):
            h = open(out).read()
            self.assertIn('/assets/source-icons/', h)
            self.assertNotRegex(h, r'<img[^>]+src="https?://(?!intelligenz-welt)[^"]*(favicon|icon)')
            self.assertNotIn('google.com/s2/favicons', h)

if __name__ == '__main__':
    unittest.main()
