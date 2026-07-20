---
name: web-ux-design
description: Audit and improve the UX and visual design of web pages and web apps — hierarchy, spacing, typography, color, states, forms, responsiveness, and accessibility. Use whenever the user asks to make a page or app "look better," "more professional," "cleaner," or "less ugly," asks for a design review or UX feedback, is building any user-facing web UI (landing page, dashboard, form, settings screen), or shares a screenshot/component and wants it improved — even if they never say the words "UX" or "design."
---

# Web UX & Design

Most "bad-looking" pages fail for the same handful of reasons: no visual
hierarchy, inconsistent spacing, too many competing elements, and missing
states. Fixing those four gets a page 80% of the way to professional. This
skill is a repeatable pass for finding and fixing them — not a style guide
to impose, but a set of checks that make the page's *own* intent legible.

## Step 0: Establish intent before touching anything

Ask (or infer from context): what is the **one thing** a user should do on
this page? Every screen has a primary action — sign up, read the thing, fix
the failing check. Design decisions get easy once it's named: the primary
action gets the visual weight, and everything else gets quieter. If you
can't tell what the primary action is, that *is* the finding — surface it
before restyling anything.

Also note the audience and context (marketing page vs. internal tool vs.
data-dense dashboard). Density that's wrong for a landing page is right
for a trading terminal. Don't sand every UI down to the same airy SaaS look.

## The audit pass

Work through these in order — earlier items constrain later ones.

### 1. Hierarchy
- Squint test: blur your mental view of the page. What stands out first,
  second, third? It should match importance. If everything is bold,
  nothing is.
- One primary button per view. Secondary actions get outline/ghost styles;
  destructive actions get separated, not reddened everywhere.
- Headings must step down consistently (one h1; sizes that visibly differ).
  Body text ≥16px in almost all cases; don't whisper the actual content.

### 2. Spacing and alignment
- Pick a spacing scale (4 or 8px base) and use only its steps. Most
  amateur-looking pages are random-spacing pages: 13px here, 22px there.
- Group by proximity: related things close, unrelated things far. Space
  *between* sections should clearly exceed space *within* them.
- Align to a grid. Mixed left-edges and centered-because-unsure content
  are the most common tells. Left-align text; center only short,
  standalone elements (hero headings, empty states).
- Whitespace is not wasted space — cramped UIs read as untrustworthy.
  When in doubt, double the margin between sections.

### 3. Typography
- Max two typefaces. One is usually enough (weights and sizes do the work).
- Line length 45–75 characters for body text (`max-width: 65ch` is a fine
  default). Full-width paragraphs on a wide monitor are unreadable.
- Line height ~1.5 for body, tighter (1.1–1.3) for large headings.
- Don't justify text on the web; don't use pure #000 on pure #fff for long
  reading — soften one side slightly.

### 4. Color and contrast
- One brand/accent color doing the interactive work (links, primary
  buttons, focus), a neutral scale (grays) doing everything else, plus
  semantic red/green/yellow used *only* for meaning. If the page has five
  decorative colors, cut to one.
- Contrast: 4.5:1 minimum for body text, 3:1 for large text and UI
  controls. Light gray text on white (#999 and lighter) fails — it's the
  single most common real-world violation.
- Never encode meaning in color alone (add an icon or label — colorblind
  users and grayscale printers exist).

### 5. States — the part everyone forgets
Every dynamic view needs, deliberately designed:
- **Empty**: first-run with no data. Say what goes here and give the
  action to create it — an empty table with just headers is a dead end.
- **Loading**: skeletons or spinners; prevent layout jump when content
  arrives. Instant-feeling (<200ms) needs nothing; longer needs feedback.
- **Error**: what went wrong, in human words, and what the user can do
  about it. Never a bare "Error" or a stack trace.
- **Success**: confirm destructive or important actions completed.
- Interactive elements need hover, focus-visible, active, and disabled
  styles. A missing `:focus-visible` outline breaks keyboard use — never
  remove it without replacing it.

### 6. Forms (highest-friction surface in most apps)
- Labels above inputs, always visible — placeholder-as-label vanishes the
  moment the user types.
- Validate inline, on blur or submit — not on every keystroke while the
  user is still typing, and never by clearing their input.
- Error messages next to the field they concern, saying how to fix it.
- Mark the *optional* fields, not the required ones, if most are required.
- Use the right input types (`email`, `number`, `date`) — mobile keyboards
  depend on it. Tap targets ≥44px.

### 7. Responsiveness
- Check ~375px (phone), ~768px (tablet), ~1440px (desktop). The most
  common breaks: fixed-width elements causing horizontal scroll, nav that
  doesn't collapse, tables that need `overflow-x: auto` containers,
  multi-column grids that should stack.
- Content, not devices, drives breakpoints: add one where the layout
  actually breaks.

### 8. Accessibility (non-negotiable minimum)
- Semantic HTML first: `button` for actions, `a` for navigation, real
  `label`s, landmarks (`nav`, `main`). Divs with onClick fail keyboards
  and screen readers at the same time.
- Full keyboard path through the primary flow; logical tab order.
- `alt` text on informative images (empty `alt=""` for decorative ones).
- Respect `prefers-reduced-motion` for nontrivial animation.

## Delivering the work

**When reviewing** (user asked for feedback, not changes): report findings
ordered by user impact, not by the checklist. Lead with the two or three
changes that would matter most, each as *problem → why it hurts → concrete
fix* (with values: "section padding varies 12–37px; use 24px throughout").
Don't dump all eight categories on every page — a focused review gets acted
on; an exhaustive one gets skimmed.

**When implementing**: fix in the audit order (hierarchy and spacing before
color polish), keep changes consistent with the project's existing design
tokens/framework (Tailwind scale, CSS variables, component library) rather
than introducing a parallel system, and verify at the three widths above.
If the project has no spacing/color system at all, introduce a minimal one
(CSS variables for the scale and palette) as part of the fix — that's what
prevents the drift from coming back.

**When building from scratch**: establish the system first — spacing scale,
type scale, one accent plus neutrals — then build screens with it. Design
the empty/loading/error states at the same time as the happy path, not as
an afterthought; retrofitting them is where inconsistency creeps in.
