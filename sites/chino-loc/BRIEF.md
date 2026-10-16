# Chino Loc — Artist Site Brief

**Goal:** Launch-ready artist website for Chino Loc, announcing his signing to Shift The Culture. Single static page, 3D animations, mobile-first, deployable to GitHub Pages and publishable as a Claude Artifact.

**Repo / branch:** `stcmain/dispatch`, branch `claude/tender-cannon-mfzsep`. Site lives at `sites/chino-loc/index.html`. Add `.github/workflows/pages.yml` to deploy `sites/` to GitHub Pages on push to `main`. Draft PR when pushed.

## Facts (do not invent beyond these)
- Artist: Chino Loc. Signing to Shift The Culture (shifttheculture.media) in 2026. Hip-hop.
- No public discography, bio, hometown, or social handles confirmed. Every link, release title, date, and bio line is a placeholder in one `CONFIG` object at the top of the script. Placeholder links are `#` and render with a small "soon" pill. Never use a real-looking handle that could belong to someone else.

## Stack
- One HTML file. No build step. Vanilla JS.
- Three.js **r128** UMD from cdnjs: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- GSAP **3.12.5** + ScrollTrigger from cdnjs: `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`, `.../ScrollTrigger.min.js`
- Fonts (Google Fonts): Pirata One (blackletter display for the name and eyebrows), Anton (condensed headlines), Archivo (body).
- Artifact CSP: scripts only from cdnjs, stylesheets only from fonts.googleapis.com, no iframes (YouTube links out), no external fetch. Keep everything else inline. Images are canvas-generated data URIs.

## Design tokens (single committed dark theme, `color-scheme: dark` on :root)
```
--bg: #090609      --bg-2: #140b10     --fg: #f4ede6     --muted: #a89a93
--accent: #e3243f  (candy-paint red)   --gold: #e2b860   --line: rgba(244,237,230,.12)
--chrome: linear-gradient(180deg,#fff 0%,#c9ccd3 35%,#5d6068 50%,#e8eaef 52%,#8a8e96 100%)
```
Direction: West Coast lowrider chrome and candy paint. Blackletter + condensed sans. Left-aligned, big type, one bold accent, everything else quiet. No purple gradients, no Inter, no emoji markers, no cards-with-shadows-everywhere.

## Sections (in order)
1. **Nav** (sticky, blurred): "Chino Loc" wordmark in Pirata One, links Music / Videos / Shows / Story / Contact, CTA "Listen". Mobile: menu toggle.
2. **Hero** with full-bleed Three.js canvas behind: eyebrow "Shift The Culture presents", H1 "CHINO LOC" in Anton with chrome `background-clip: text`, sub "Officially signed. New era loading.", CTAs "Listen now" + "Join the list". Height ~78vh so the next section peeks.
3. **Marquee** ticker: "CHINO LOC • SHIFT THE CULTURE • OFFICIAL ROSTER 2026 •" (CSS keyframes, duplicated content for seamless loop).
4. **The Deal**: 3D spinning gold coin (second Three.js canvas) left, copy right: "Chino Loc × Shift The Culture. Officially signed, 2026." Short paragraph on what the label brings (records, visuals, rollout, platform). List: Debut single under STC / Visuals / Live dates.
5. **Music**: "Latest" spotlight card (generated cover, "Title TBA", Pre-save button) + platform buttons (Spotify, Apple Music, YouTube, SoundCloud, Audiomack from CONFIG) + catalog grid of 3 tilt cards ("Release 01–03 · Title TBA · 2026"). Line: "Catalog populates as drops land."
6. **Videos**: 3 cards with generated thumbnails + play glyph, each links out to CONFIG youtube URL.
7. **Shows**: table, one row "TBA · Your city · Request a date". CTA "Book Chino Loc" reveals booking email as selectable text with copy button (CONFIG.bookingEmail; default `info@shifttheculture.media`, confirm before go-live).
8. **Story**: positioning copy only, no biography claims. "A new name on the Shift The Culture roster. Chino Loc arrives with a sound of his own and a team built to take it everywhere." Button "Request press kit" (same email).
9. **Join the list**: email + city form. On submit: if `CONFIG.signupEndpoint` set, POST JSON to it; else show "List opens with the first drop. Follow on Instagram so you don't miss it." Never fake a success.
10. **Footer**: socials from CONFIG, "© 2026 Chino Loc. A Shift The Culture artist."

## 3D spec
**Hero scene (Three.js r128, MeshMatcapMaterial, no lights needed):**
- Procedural matcaps drawn on canvas: chrome (white→steel, hard horizon line at 50%, dark lower half, specular blob top-left, dark rim) and gold (cream→#e9c46a→dark horizon→#f3d98a→#2b1c05). `texture.encoding = THREE.sRGBEncoding`, `renderer.outputEncoding = THREE.sRGBEncoding`.
- Chain link = TubeGeometry along a closed CatmullRomCurve3 of a stadium path (L=1.1, R=0.42, tube r=0.13, 96 segments, 20 radial).
- Necklace = 30 links around a ring in the XY plane, pitch 1.05, ring radius = 30*1.05/(2π) ≈ 5.0. Each link: pivot.rotation.z = θ, link at (Rc,0,0), link.rotation.y = i*π/2 (alternating twist so links interlock).
- Pendant at θ=-π/2: gold cylinder coin (r 1.3, h 0.18, rotation.x=π/2) with canvas texture "CL" in Pirata One (wait for `document.fonts.ready` before drawing, then `needsUpdate`).
- Gold-flake particles: THREE.Points, ~1500 desktop / 600 mobile, additive blending, slow drift.
- Fog: FogExp2(0x090609, 0.045). Camera fov 40 at z≈15. On wide screens offset group x≈+2.5 so the H1 sits left.
- Motion: slow rotation.y; pointer parallax lerped (desktop only); GSAP ScrollTrigger scrub on the hero drives group.rotation.z (0→π/2) and camera z (15→21).
- Perf: pixelRatio capped at 2; pause RAF when hero is offscreen (IntersectionObserver) or tab hidden; handle resize. `prefers-reduced-motion`: render one frame, no loop, no parallax.

**Coin scene:** CylinderGeometry(1.3,1.3,0.18,64), materials [side gold matcap, face gold matcap + canvas map]. Map: gold base, concentric rings, rim text "SHIFT THE CULTURE ★ OFFICIAL ROSTER ★" drawn per-character around the circle, center "STC" in Anton + "2026", engraved color #3a2a0a. Spin on y, slight x wobble, speeds up on hover.

**Tilt cards:** pointermove → rotateX/rotateY (±10°) with perspective(900px) + moving glare overlay; reset on leave. Touch: no tilt.

**Covers/thumbnails:** canvas 600×600 per `data-seed`: dark gradient hue from seed, diagonal chrome stripe, big low-opacity "CL" in Pirata One, small label text → `toDataURL` into `<img>`.

**Reveals:** transform-only (y 24→0) via ScrollTrigger. Never leave content at opacity 0 before scroll; the page must be complete at rest.

## Layout rules
- Gutter on every wrapper: `padding-left: max(16px, env(safe-area-inset-left,0px))`, same for right; vertical padding via `padding-block`. Add `<meta name="claude:viewport-fit-sides" content="cover">` next to `<title>`.
- Sticky nav `top: env(safe-area-inset-top,0px)` with `body::before` fixed band painting the top inset.
- No horizontal scroll at 400px. Grids stack to one column. `min-width: 0` on flex/grid text children. Headings `text-wrap: balance`.
- Visible focus states. Close every tag, double-quote attributes.

## Artifact + repo dual output
- Repo file is a full document (doctype, html, head, body).
- Artifact file = same content minus doctype/html/head/body wrappers and charset/viewport metas (the Artifact tool wraps a skeleton). Generate it with sed/python from index.html; publish with `icon: "music"`, title "Chino Loc".

## Verification before push
- `node --check` on the extracted inline script.
- One Playwright screenshot of the local file at 1280 and 400 widths (Chromium is at `/opt/pw-browsers/chromium`; cdnjs is blocked from the cloud container, so for the local screenshot swap script src to local copies from `npm pack three@0.128.0 gsap@3.12.5`). Locally on the user's machine cdnjs loads fine.
- Repo CI is pytest only; the site adds no Python, so CI stays green.

## Deploy
- `.github/workflows/pages.yml`: on push to main (paths `sites/**`) + workflow_dispatch; permissions pages/id-token; `actions/configure-pages@v5`, `actions/upload-pages-artifact@v3` (path `sites`), `actions/deploy-pages@v4`.
- `sites/index.html` meta-refresh → `chino-loc/`.
- Live URL after merge + enabling Pages (Settings → Pages → Source: GitHub Actions): `https://stcmain.github.io/dispatch/chino-loc/`.
- Custom domain later: add `sites/CNAME`.

## Decision points for ZP (owner), needed before go-live
1. Real links: Spotify, Apple Music, YouTube, SoundCloud, Audiomack, Instagram, TikTok, X.
2. Booking/press email (default `info@shifttheculture.media`).
3. Mailing-list endpoint (Formspree/Mailchimp/Beehiiv) for `CONFIG.signupEndpoint`.
4. First single title, art, pre-save link, release date.
5. Approve bio copy or send 3 lines of real bio.

## Done looks like
- `sites/chino-loc/index.html` renders at 1280 and 400 with 3D hero + coin + tilt cards, no console errors, no horizontal scroll.
- Published Artifact link shared.
- Branch pushed, draft PR open with the live/preview links and the 5 decision points in the body.
