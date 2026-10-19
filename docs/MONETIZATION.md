# Advertising and measurement preparation

Status: preparation only, no deployed tracking, no connected provider/account, no active campaign. Reviewed on 2026-10-19.

## Pages and surfaces

- `/werben/`: advertiser formats and mailto requests to the explicitly supplied public address. No form/backend or submission. No prices, reach, endorsements or existing partners asserted.
- `/werbung/`: editorial separation and labels. Use `Anzeige` first. `Gesponsert`/`Affiliate` supplement it. Commission explanation belongs immediately next to each affiliate link.
- `/cookies/`, `/datenschutz/`: accurate off-state disclosures, 180-day local consent record, revocation entry in every normal footer.
- Desktop privacy panel; mobile bottom drawer. Essential service fixed; statistics/advertising disabled while unavailable. Close/Escape never consent. Reject and accept have equal treatment. No focus trap because this is a non-modal settings region.
- Unbooked spots render nothing. V1 direct placement: maximum one campaign, after editorial content, no popups/autoplay/sticky ads. No dummy ad creative, buyer logo, price or performance.
- Print editions deliberately excluded from the new UI.

## Architecture and activation locks

`content/monetization.json` is the single config. `tools/monetization.py` runs last in `site/build.py`; assets are local. The subsequent existing author-page job inherits its common footer. Sitemap includes the new pages. No production dependency added.

Build intentionally fails if analytics, metrics or AdSense is turned on without an implementation review. This preparation is NOT a finished GA4 installation or a certified CMP. A real activation is a separate change with provider-specific disclosures and integration tests. No publisher IDs, keys, ads.txt entries or invented identifiers included.

1. Owner selects GA4 or another measurement service. No account has been created or inspected.
2. Obtain genuine measurement ID, review controller/processor arrangements, retention, transfers, security and actual events. Update all off-state disclosures and consent revision. Complete legal review with owner.
3. GA4 code seam is *basic* consent, not advanced: no Google request or tag before statistics consent; no denied-consent pings by default. Query strings/referrer are omitted from explicit page events; signals and ad personalization disabled. Review automatic/enhanced measurement in the actual property, redaction and IP/transfer implications before activation. Test withdrawal and cookies against the real property.
4. AdSense: apply using owner account, verify site access and original policy-compliant content, obtain approval. Aggregated RSS headlines do not guarantee approval. Obtain genuine publisher/slot IDs and account-provided ads.txt content if required. Select an appropriate Google-certified TCF CMP. Google's own Privacy & messaging is one possible option; do not silently select it. Our drawer is NOT certified and CANNOT unlock AdSense. Integrate CMP and avoid conflicting duplicate prompts. Rejection must leave scripts absent under this project's stricter no-request rule, including no non-personalized-ad workaround. Test the real integration and update notices before release.
5. Direct campaigns: owner reviews exact sponsor, wording, target and dates; destination/content must be real. Every paid preview and paid article must carry its own label. Do not turn an independent editorial article into paid content merely because a separate ad points to it. V1 configuration supports external offers; local paid article destinations deliberately require the separate article/list labeling pass first. No network is automatically joined.

No automatic booking, purchase, email or publishing is performed by the mailto link. It opens a draft in the visitor's mail application; copying the visible address works without an app.

## Measurement choices for the owner

| Option | Useful for | Tradeoff / setup |
| --- | --- | --- |
| GA4, basic consent | Page views, events, promotion clicks/views, reports | Google service and property required; consent, processor/transfer/retention decisions. Rejected visitors absent, so not total audience. |
| Self-hosted Matomo | Controlled first-party analytics and reports | Requires server, updates and operations. Static GitHub Pages alone cannot host it. Cookieless JavaScript is not automatically consent-free in Germany. Still consent-first in this implementation. |
| First-party aggregate collector | Narrow sponsored-spot counts, no third-party browser script | Requires explicit backend/log access, rate limiting, retention and reporting. Browser-only events are not aggregated reporting. Not implemented/connected. |

Recommendation for the current static site if standard reports matter: GA4 *basic consent*, only after the owner chooses it and supplies an actual property. Choose self-hosted Matomo if owning the analytics stack is worth operating another service. No paid service selected.

Prepared browser event seam: `iw:metric`, containing only `event`, `spot_id`, `page_path`. Only emits if configured AND statistics consent is current. No identifier/referrer/query string. Optional GA4 adapter can send the same event only after consent. This seam has no collection backend and reports nothing today.

- `promotion_view`: a prepared local proxy definition, at least 50% visible for one continuous second in a foreground tab, once per rendered placement. Not a certified/viewability-audited metric, not Google's AdSense impression definition. Not billable inventory by itself.
- `promotion_click`: click on the placement's marked link, after statistics consent.
- CTR = measured clicks / measured impressions * 100, only for a matched campaign/window. CPM = agreed campaign spend / agreed impressions * 1000; revenue CPM/eCPM = realized revenue / measured impressions * 1000. No revenue source connected and no numeric dashboard invented.
- Consent losses, blockers, repeat clicks and bots affect coverage. Never represent these counts as all visitors or audited ad delivery. No cross-tab/user deduplication or fraud controls in this preparation.

## QA

Production build: unpack payload (`cat payload-*.b64 | base64 -d | tar xz --skip-old-files`), then `cd site && python3 build.py`; existing author page job remains unchanged.

Optional developer-only UI test: install Playwright outside the production tree, set `NODE_PATH` to its node_modules and `CHROME_PATH` if needed; run `node tools/monetization/test-ui.cjs`. No production package added. Test starts and closes a local ephemeral server and browser. Screenshots go to `SCREENSHOT_DIR` (default `/tmp/iw-monetization-screenshots`).

42 browser checks: 1440px, 390px and 320px, no external network calls, disabled unavailable categories, reject/accept-available persistence, expiry, settings reopen, article integration, mailto and overflow. Visual review covers desktop + mobile advertiser page and drawer. IW currently has no dark mode; no unrelated theme introduced.

## Sources, checked 2026-10-19

- Google AdSense, eligibility: https://support.google.com/adsense/answer/9724
- Google AdSense, certified TCF CMP requirements for personalized ads in EEA/UK/Switzerland; Google certification is not full legal certification: https://support.google.com/adsense/answer/13554116
- Google Analytics, basic vs advanced consent: https://support.google.com/analytics/answer/10000067?hl=en
- Matomo, current cookie/consent guidance (vendor source, not legal advice): https://matomo.org/faq/new-to-piwik/how-do-i-use-matomo-analytics-without-consent-or-cookie-banner/
- §25 TDDDG, consent and necessary-service exception: https://www.gesetze-im-internet.de/ttdsg/__25.html
- German media authorities, labeling guide: https://www.die-medienanstalten.de/service/merkblaetter-und-leitfaeden/leitfaden-werbekennzeichnung-bei-online-medien/
- Accessible guide PDF (commercial posts: Werbung/Anzeige at start; affiliate disclosure beside link): https://www.die-medienanstalten.de/fileadmin/user_upload/die_medienanstalten/Service/Merkblaetter_Leitfaeden/Leitfaden_Werbekennzeichnung_Onlinemedien_ua.pdf

The owner reviews legal/business matters. These pages document the actual inactive implementation, not a declaration of legal compliance or a promise of AdSense approval.

## GA4 follow-up (2026-10-19)

Owner selected GA4, not self-hosting. Integration now has a reviewed-profile gate rather than an unconditional provider lock: `enabled`, a genuine `G-...` measurement ID, `activationApproved`, and `privacyReviewed` must all be set only in a separately approved activation. Short profile: 2-month event/user retention, retention reset on activity OFF in GA4 admin; browser cookie lifetime fixed at 180 days (`cookie_expires=15552000`, `cookie_update=false`). Ads remain hard-locked. No actual property/stream has been created by this patch.

GA4 disclosure is generated on both privacy/cookies pages, explicitly PREPARATION while off and actual-use wording only after the activation gate. It describes provider, data, purpose, voluntary consent, IP transmission vs storage distinction, cookies, retention (aggregate report caveat), transfers, Art.28 DPA review and revocation. No claim that a DPA has already been accepted or a particular transfer mechanism verified. Activation MUST verify actual contract entity, current DPF coverage/other transfer basis and account terms, disable Google Signals/user-provided data, enhanced measurement, Google Ads links and advertising features in the actual property. No replay, form text or search terms. Consent revision changed so no old off-state choice authorizes the new service.

Withdrawal disables GA immediately without emitting a denied ping, deletes accessible known GA cookies and reloads. Cross-tab consent changes reload existing tags; expiry is checked per event and on foreground return. Genuine account settings and end-to-end behavior still require checking before activation.

Additional sources read:
- https://support.google.com/analytics/answer/7667196 (2/14-month settings; aggregate-report exception)
- https://support.google.com/analytics/answer/11397207 (cookie defaults vs custom configuration)
- https://support.google.com/analytics/answer/3379636?hl=en (DPA contractual status differs by account/region, not universally a fresh click)
- https://support.google.com/analytics/answer/6004245?hl=en (GA as processor, data safeguards)
- https://business.safety.google/adsprocessorterms/
- https://policies.google.com/privacy?gl=IE&hl=en
- https://policies.google.com/privacy/frameworks?hl=de

GA4 QA fixture: `test-ga4.cjs` uses `G-LOCALFIXTURE` only in temporary generated output and intercepts ALL HTTPS requests. It is not a property and must never be copied to production config. 30 additional browser assertions verify no requests before consent/rejection; one intercepted tag after consent; denied-then-granted ordering, fixed cookies, flags, query stripping, revocation/reload/cookie deletion, active disclosure, in mobile and desktop. Tests reset committed config to OFF afterwards. Live end-to-end GA ingestion is deliberately NOT tested before approval.

### Actual property created, tag still OFF

User approval: WhatsApp 2026-10-19 14:15:23, "darfste", direct reply to the specific free new-property question, no new terms and tag stays off. Verified original channel record.

- Signed-in Google identity: philipp.l.paulik@gmail.com (account menu checked).
- Existing GA account: Default Account for Firebase, 363019915. Existing Chrome Web Store account does not permit new properties; reused the user's existing editable web-project account, no new account.
- New property: Intelligenz Welt - intelligenz-welt.de, 559488833.
- Webstream: Intelligenz Welt Web, https://intelligenz-welt.de, 16158398372.
- Genuine measurement ID: G-E1XCJME97G. Non-secret public measurement identifier; present in OFF config only.
- Actual opened property home: https://analytics.google.com/analytics/web/#/a363019915p559488833/reports/intelligenthome
- Actual opened stream: https://analytics.google.com/analytics/web/?hl=en#/a363019915p559488833/admin/streams/table/16158398372
- Germany reporting timezone, EUR. Industry News; smallest size bucket (1-10), web traffic objective.
- Retention saved and read back: event data 2 months, user data 2 months; activity reset OFF. UI warns changes take effect after 24 hours. Screenshot inspected.
- Google Signals and user-provided data both OFF (UI offers Turn on, not clicked).
- Advertising personalization changed from default 307/307 allowed to 0/307; saved and read back. Granular device/location collection also disabled.
- Enhanced Measurement creation toggle did not persist as expected. Detected on post-creation verification and switched OFF again in actual stream; read back aria-checked=false and pixels inspected. Do not assume creation defaults.
- No new terms, DPA acknowledgment, paid feature or tag installation accepted. No Measurement Protocol secret generated.

Still required before activation: actual contract/DPA/entity/transfer basis review in this existing account, explicit activation approval, refresh consent revision as needed, deploy and test real browser traffic including reject/accept/withdraw, verify GA ingestion. No claim of accepted DPA or live metrics. The property currently reports no website data, as expected.

## Consent-gated activation, 2026-10-19

Supersedes the preparation-only status above. Account 363019915, property 559488833, web stream 16158398372, tag G-E1XCJME97G. Owner approved activation after DPA review, then separately approved accepting the account-wide Data Processing Terms. Account settings confirmed acceptance on October 19, 2026 after a full reload. Country Germany and all other account data-sharing choices were left unchanged. A separately approved Primary contact was added using the owner's name, email and imprint address; no DPO/EEA representative role or company entity was invented.

The German standard Analytics terms name Google Ireland Limited as contract party: https://www.google.com/analytics/terms/de.html . Accepted processor terms: https://privacy.google.com/businesses/processorterms/ . Google LLC is Active in the official EU-US DPF register (checked 2026-10-19; next certification due 2027-09-13): https://www.dataprivacyframework.gov/participant/5780 . Transfer explanation: https://policies.google.com/privacy/frameworks?hl=de . This is a factual configuration/source review, not a legal compliance certification.

Analytics is now enabled in this patch, with activationApproved/privacyReviewed true and a new consent revision. Advertising and promotion metrics remain OFF. No script/preconnect/ping before explicit statistics consent. The production tag ID is tested with ALL HTTPS intercepted; no QA traffic is sent to Google. 30 browser assertions pass on desktop and mobile, covering reject/accept/revoke, query/referrer redaction, 180-day fixed cookie settings and advertising disabled. Existing off-state UI test requires an off config and is not an activation test. Current live Google Admin settings were reviewed separately: retention 2 months (may take 24 hours to apply), reset OFF, Enhanced Measurement OFF, Signals/user-provided data OFF, ads personalization 0/307, granular location/device OFF.

Deploy handoff: apply after the GA4 preparation patch; build and publish with the normal pipeline. Verify the live site on a fresh browser context: no Google request on initial load/reject; exactly the intended tag and analytics endpoint after explicit statistics consent; withdrawal removes accessible cookies and reloads without the tag. Confirm real event ingestion separately in GA4. This patch does not itself deploy or prove ingestion and does not provide a live metrics dashboard. Consent-based statistics are not total audience counts. No paid service or ad code activated.
