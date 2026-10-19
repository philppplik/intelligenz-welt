# Intelligenz Welt: editorial pipeline

Own articles live next to the auto-aggregated news. They are plain files; CI renders them on every push and every 3 hours.

## Layout
- `content/articles/<slug>.json` - one article (format below)
- `content/images/<slug>.jpg` - hero image, 1600x900 JPEG, max 350 KB, with the visible label "KI-generiert" burned into the pixels when AI-made. Optional `<slug>-800.jpg` (800x450) enables `srcset`.
- `tools/articles.py` - renderer, called at the end of `site/build.py`. Stdlib only. Fails the build with a clear message on invalid input.
- `tools/search.py` + `tools/search.js` - site search on `/suche/`: the build writes `search-index.json` (articles, legacy analyses, latest 300 KI-Pulse headlines, main pages); the page searches it locally in the browser (umlaut- and typo-tolerant, no external service).
- `site/` - site generator (`build.py`, `data.py`, `common.py`, `src/`). It used to live only inside `payload-*.b64`; the unpack step in `.github/workflows/pages.yml` uses `--skip-old-files`, so the committed files win. The payload files are now obsolete and can be removed together with that step.
- `authorpage/` - author page generator (post-build step in `pages.yml`).

## Output
`/artikel/<slug>/` (article), `/artikel/` (list), `/thema/<section>/` (section pages), `/redaktion/` (editorial policy), `/suche/` (client-side full-text search), `news-sitemap.xml` (own news/analysis from the last 48 hours), `sitemap.xml` with image entries (`http://www.google.com/schemas/sitemap-image/1.1`), `feed.xml` items, home page block "Neueste Artikel", nav link.
URLs are extensionless with a trailing slash; canonical, sitemap and internal links use the same form.

## Article JSON (v1)
Required: `slug`, `title` (max 70), `dek` (100-160 chars, used as meta description), `section` (`news|trends|tools|modelle|analyse|praxis`), `type` (`news|analysis|explainer`), `published`, `modified` (ISO 8601 with offset, e.g. `2026-10-19T08:00:00+02:00`; a future `published` means "scheduled", not built yet), `author` (`philipp-paulik`), `tags`, `key_takeaways` (3-5), `hero` (`alt`, `caption`, `ai_generated`, optional `credit`), `body` (blocks), `sources` (`title`, `publisher`, `url` https, optional `accessed`; at least 1, aim for 3+).
Optional: `faq` (`q`,`a`), `related` (slugs), `method`, `limitations`, `lang`.
Body blocks: `p`, `h2`, `h3` (`x`), `ul`/`ol` (`items`), `quote` (`x`, `cite`, `url`), `table` (`head`, `rows`, `caption`), `figure` (`file`, `alt`, `caption`, `ai_generated`), `callout` (`title`, `x`), `code` (`x`). Inline: `**bold**`, `*italic*`, `[text](url)`, `[^1]` (links to source 1).
`news` and `analysis` articles go into the news sitemap (Google News: only articles of the last 2 days, publication name "Intelligenz Welt", language `de`). Schema: `NewsArticle` for news/analysis, `Article` for explainer, with `ImageObject` (AI images carry `digitalSourceType: trainedAlgorithmicMedia`), `BreadcrumbList`, `FAQPage`, author = Person `https://philipp-paulik.de/#person`, `citation`.

## Publishing
1. Add the JSON and JPG in one commit on `main` (author Philipp Paulik, no agent trailer). Batch pushes: the Pages workflow cancels in-progress runs, the last one wins.
2. CI builds and deploys. Check the live URL, the news sitemap and JSON-LD.
3. Never change a slug after publishing. Corrections: edit, bump `modified`, say so in the text.

## Local test
```
cd site && python3 data.py && python3 build.py && cd .. && python3 authorpage/authorpage.py iw site/out --assets authorpage/assets
```

## Google News checklist (checked against Google's pages, 2026-10-18)
Eligibility needs no application; follow the content policies. Required: clear dates and bylines, author/publisher/contact information, permanent unique article URLs, headline and date easily identifiable, HTML body text, one language per article, UTF-8, no robots blocking. Sources: https://support.google.com/news/publisher-center/answer/6204050 , https://support.google.com/news/publisher-center/answer/9606708 , https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap

## Secrets
The push token (fine-grained PAT, contents write on this repo and kifachblatt only) expires 2026-11-17. Renew around 2026-11-14.

## KI-Pulse source icons

Each headline in the KI-Pulse (home sidebar and /news/) shows a 20px source icon. Icons are local 64px PNG copies in site/source-icons/<slug>.png (slug = source name lowercased, non-alphanumerics to "-"), copied to /assets/source-icons/ by build.py. No hotlinks, no third-party favicon service. Exact origin URLs: site/source-icons/sources.json. They only identify the source; no endorsement is claimed. A source without icon gets a colored monogram. Test: tests/test_source_icons.py.
