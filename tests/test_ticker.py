import os, re, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Ticker(unittest.TestCase):
    def test_ticker_local_and_accessible(self):
        p = ROOT + '/site/out/index.html'
        if not os.path.exists(p): self.skipTest('no build')
        h = open(p).read()
        m = re.search(r'<div class="iwt".*?</script>', h, re.S)
        self.assertTrue(m)
        t = m.group(0)
        self.assertIn('aria-label="KI-Pulse', t)
        self.assertIn('aria-label="Ticker anhalten"', t)
        for a in re.findall(r'<a [^>]*>', t):
            self.assertIn('rel="noopener nofollow"', a); self.assertIn('target="_blank"', a)
        self.assertNotRegex(t, r'<img[^>]+src="https?:')
        self.assertNotRegex(t, r'<script[^>]+src=')
        self.assertIn('/assets/ticker.css', h)

if __name__ == '__main__': unittest.main()
