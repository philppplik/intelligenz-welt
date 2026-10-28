import pathlib, tempfile, unittest
import exit_intent as m

class ExitIntentTests(unittest.TestCase):
    def test_attach_and_skip_reports_page(self):
        h='<html><body>x</body></html>'
        self.assertIn('id="iw-exit"', m.attach(h,'/'))
        self.assertIn('id="iw-exit"', m.attach(h,'/artikel/test/'))
        self.assertEqual(m.attach(h,'/berichte/'), h)
    def test_attach_idempotent(self):
        h=m.attach('<html><body>x</body></html>','/')
        self.assertEqual(m.attach(h,'/'), h)
    def test_accessibility_markup(self):
        s=m.SNIPPET
        self.assertIn('role="dialog"',s); self.assertIn('aria-modal="true"',s)
        self.assertIn('aria-labelledby="iw-exit-t"',s); self.assertIn('id="iw-exit-t"',s)
        self.assertIn('aria-label="Hinweis schlie',s)
        self.assertIn('id="iw-exit" hidden',s)
        self.assertIn('Escape',s); self.assertIn('Tab',s)
        self.assertIn('data-x',s)  # X + "Nein, danke" + backdrop close
    def test_links_point_to_current_report(self):
        self.assertIn('href="/tagesbericht-anmelden/"',m.SNIPPET)
        self.assertIn('href="/berichte/"',m.SNIPPET)
    def test_no_tracking_no_external_calls(self):
        s=m.SNIPPET
        self.assertNotIn('http://',s); self.assertNotIn('https://',s)
        self.assertNotIn('document.cookie',s); self.assertNotIn('localStorage',s)
        self.assertNotIn('fetch(',s); self.assertNotIn('XMLHttpRequest',s)
        self.assertNotIn('navigator.sendBeacon',s); self.assertNotIn('history.pushState',s)
    def test_once_per_session_and_armed_delay(self):
        s=m.SNIPPET
        self.assertIn('sessionStorage.getItem("iw-exit-report")',s)
        self.assertIn('sessionStorage.setItem("iw-exit-report","1")',s)
        self.assertIn('var ARM=8000',s)
        self.assertGreaterEqual(m.ARM_MS,5000)
    def test_never_over_menu_consent_or_modal(self):
        s=m.SNIPPET
        self.assertIn('"menu"',s); self.assertIn('"iw-consent"',s)
        self.assertIn('body>[aria-modal=true]',s)
    def test_no_fixed_layout_shift(self):
        self.assertIn('position:fixed',m.SNIPPET)
    def test_main_pass(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)
            (out/'artikel/x').mkdir(parents=True)
            (out/'berichte').mkdir()
            page='<html><body><p>x</p></body></html>'
            (out/'index.html').write_text(page)
            (out/'artikel/x/index.html').write_text(page)
            (out/'berichte/index.html').write_text(page)
            (out/'alt/index.html').mkdir and None
            (out/'alt').mkdir()
            (out/'alt/index.html').write_text('<html><head><meta http-equiv="refresh" content="0; url=/artikel/"></head><body>r</body></html>')
            m.main(str(out))
            self.assertIn('id="iw-exit"',(out/'index.html').read_text())
            self.assertIn('id="iw-exit"',(out/'artikel/x/index.html').read_text())
            self.assertNotIn('id="iw-exit"',(out/'berichte/index.html').read_text())
            self.assertNotIn('id="iw-exit"',(out/'alt/index.html').read_text())
            m.main(str(out))  # second run is a no-op
            self.assertEqual((out/'index.html').read_text().count('id="iw-exit"'),1)

if __name__=='__main__': unittest.main()
