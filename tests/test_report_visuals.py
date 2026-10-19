"""Run with python3 -m unittest discover -s tests -p 'test_report_visuals.py'."""
import datetime, importlib.util, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import report_visuals as V
NOW = datetime.datetime(2026, 10, 19, 12, 0, tzinfo=datetime.timezone.utc)
T = NOW.timestamp()
AI = [{'title': 'OpenAI und Claude im Vergleich', 'ts': T - 3600, 'src': 'A', 'url': 'u'}, {'title': 'Nvidia RTX neu', 'ts': T - 86400 * 9, 'src': 'B', 'url': 'u'}]
MODELS = [{'id': 'nvidia/X', 'likes': 10, 'dl': 100, 'tag': 'text-generation', 'url': 'u'}, {'id': 'foo/Y', 'likes': 5, 'dl': 50, 'tag': None, 'url': 'u'}, {'id': 'foo/Z', 'likes': 3, 'dl': 500, 'tag': 'x', 'url': 'u'}]

class T_(unittest.TestCase):
    def test_logos_hash_verified_and_mapped(self):
        V.load_logos(str(ROOT)); self.assertIn('nvidia', V.LOGOS)
        for v in V.HF_ORG_LOGO.values(): self.assertIn(v, V.LOGOS)
    def test_tampered_logo_dropped(self):
        V.load_logos('/nonexistent'); self.assertEqual(V.LOGOS, {})
        self.assertIn('class="mono"', V.badge('nvidia', 'nvidia', V.AC))
    def test_no_model_logo_for_company_assets(self):
        self.assertNotIn('google', V.HF_ORG_LOGO); self.assertNotIn('facebook', V.HF_ORG_LOGO)
    def test_topics_count_titles(self):
        h = V.topic_bars(AI, NOW); self.assertIn('OpenAI', h); self.assertIn('Anthropic', h)
    def test_blocks_render_and_escape(self):
        V.load_logos(str(ROOT))
        for h in (V.kpis(AI, MODELS, NOW), V.per_day(AI, NOW), V.source_donut(AI, NOW), V.trend_bars(MODELS), V.task_donut(MODELS), V.scatter(MODELS), V.org_bars(MODELS)):
            self.assertTrue(h)
        self.assertEqual(V.per_day([], NOW), ''); self.assertEqual(V.trend_bars([]), '')
        self.assertIn('Logos und Marken', V.logo_credits())
    def test_no_remote_resources(self):
        V.load_logos(str(ROOT)); h = V.web_models(AI, MODELS, NOW) + V.web_news(AI, MODELS, NOW)
        import re
        self.assertFalse(re.findall(r'(?:src|href)="https?://(?!huggingface\.co|github\.com)[^"]*"', h.replace('u"', '')))
if __name__ == '__main__': unittest.main()
