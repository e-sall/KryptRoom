# KRYPTROOM M8 — MARKETING REDESIGN REPORT

Founder-directed replacement of the previous homepage priorities, 2026-10-25.
The original PR7 focus/rotation work remains in the same feature branch.

## Composition and reference

The former page contained a hero, short collaboration card, How It Works,
product-boundary cards and demo invitation. The founder-approved order is now:

1. Hero.
2. Autoplay Product Demo.
3. Why KryptRoom.
4. How It Works.
5. Persistent Encrypted State.
6. Cryptographic Foundation.
7. Who's Building KryptRoom.
8. Final Call to Action.
9. Questions & Answers, followed only by the shared footer.

An automated DOM-order assertion preserves this sequence. The FAQ contains all
ten requested questions, using native details/summary with keyboard behavior.
Booking remains unavailable; both hero and final CTA link to the honest existing
booking page. The exact tagline and canonical K remain intact. The position line
is Persistent Encrypted Collaboration Infrastructure.

[TryClean](https://www.tryclean.ai/) was inspected in a real browser and as a
source of structural inspiration: compact floating navigation, editorial headline,
early product composition, narrative/visual scenes, a credible builder section,
large FAQ title and restrained dividers. No Clean text, photograph, illustration,
CSS, component or asset was copied. Its live page differs from the founder's
described screenshots; no separate Clean screenshots were available in the
project attachments. Comparison therefore uses the live reference plus the
founder's written criteria, not a pixel-perfect reproduction claim.

## Homepage showcase versus full P05

`HomeShowcase` is a separate, read-only marketing composition. It imports the
existing `demoScenes` and `demoGraph`, derived from PR3's immutable catalog. It
does not create another RoomState catalog. Ordered edges remain S1→S2, S1→S3,
S2→S4 and S3→S4, with S4 parents [S2,S3]. The full `/demo` remains the restored V1
Explore/Presentation experience, with no automatic progression added there.

The homepage starts on Organizations. After it becomes visible, a **6-second**
interval advances through seven scenes and wraps deterministically. Pause/Resume
control only presentation; Replay returns to scene one and resumes when motion
is allowed. Direct scene selection pauses so the chosen content can be read.
IntersectionObserver, document visibility and reduced-motion preference gate the
timer; cleanup removes it. Returning to the viewport resumes the retained scene,
without random reset or catch-up. Automatic text changes have live announcements
off; paused manual exploration uses a polite announcement. No audio or flashing.

Reduced motion disables autoplay and visual transitions; all scene buttons and
the full-demo link remain usable. Server-rendered content and native FAQ remain
readable without JavaScript; noscript explains the static state. Unsupported
observer/motion APIs fail to a static presentation. No network call or progress
event is fabricated. Not assessed / Not anchored remain explicit in every scene.

## Framing and rhythm

The homepage does not embed the tall, scrollable three-column `/demo` inspector.
Its own frame contains the complete visualization, concise context and controls,
with no inner scrolling or clipped content. Desktop uses a scene rail, graph and
context; tablet moves the rail above; mobile uses numbered scene controls,
vertical lineage and context below. All labels and ordered parents remain text.

Tests visit all seven scenes at **1440×900, 1366×768, 1280×800, 1024×768,
834×1112, 768×1024, 390×844, 375×812 and 320×800**, checking containment, no inner
overflow, stable total height and no page overflow. Mobile deliberately reflows
vertically and can exceed one screen; it is not shrunk into illegible columns.
Desktop's complete product frame can be scrolled into view without inner scroll.
No section is forced to 100vh. Long content, particularly FAQ and mobile scenes,
uses ordinary page scrolling.

How It Works retains all four exact steps and explanatory content. Manual step
selection takes priority over focus-induced/programmatic scrolling; new wheel,
touch or scroll-key input resumes desktop scroll-following. This fixes the real
regression found by the existing browser suite after homepage expansion.

The Why visual explains separate organization boundaries and an authorized joint
answer. Persistent State reuses the same ordered graph and distinguishes reusable
shares from encryption at rest. Cryptographic Foundation states the bounded M1–M7
evidence and semi-honest/trusted-host limits, with technical/security links. Neither
section associates historical proofs or the sole anchor with this synthetic demo.
Quantum computing appears only as future R&D in the required FAQ, never executed.

## Founder portrait and claims

The original supplied professional JPEG was located, opened and copied byte for
byte to `apps/web/public/images/elimane-sall.jpeg`. Dimensions **3367×3958**;
SHA-256 **99c3f94ae1e61e9e53109ed533ff140aed095f43eb0cc85ad0bce91d85117160**.
No GPS EXIF tag was found. No face change, AI generation, enhancement, image
transformation or replacement; CSS object-fit provides the display crop, with
reserved dimensions, descriptive alt and no distorted face proportions.

The section uses only the founder-supplied facts: Elimane Sall, Founder KryptRoom,
industrial engineering student at Polytechnique Montréal, interest in cryptographic
infrastructure/deep technology. No invented team, credential, client, funding or
institutional partnership. The project link is the real public GitHub repository.

## Visual review and limitations

Every homepage section has desktop/tablet/mobile captures in the
[visual inventory](VISUAL-EVIDENCE.md). The actual browser renders and images were
inspected; initial review led to a deliberate two-line hero and restoration of
warm neutral surfaces with discreet blue instead of unintended olive emphasis.
Keyboard and modal corrections are retained and extended for WebKit: native
focus scrolling is completed where needed, modal openers receive focus explicitly,
and Tab traverses all visible controls. Next Link speculative preloads are disabled
using the documented frontend prop after actual WebKit preload errors; explicit
navigation and all page-error guards remain. No security header or dependency changed. Product framing, the founder crop,
FAQ wrapping, narrative proportions and several scene states are review subjects.

This is an implementation review candidate. CI success is not aesthetic approval.
Original P11 composition remains a reference for the application; this new
founder mission explicitly supersedes old homepage layout priorities. Physical
devices, assistive technologies and Safari as an actual Apple browser remain
separate limitations. No public deployment was made.
