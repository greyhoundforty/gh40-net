# ToC toggle, post import, rename: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a show/hide ToC to posts, import 16 posts from `gh40-export/`, and rename the site to ryantiffany.com.

**Architecture:** Astro 2 static site (astro-cactus), posts are `src/pages/posts/*.mdx` using `@/layouts/BlogPost`. ToC toggle is a small inline script plus a class on the grid. Import is a one-off Python script (kept outside `src/`) that writes `.mdx` files.

**Tech Stack:** Astro, MDX, Tailwind, Python 3 (stdlib only) for conversion.

**Spec:** `docs/superpowers/specs/2026-11-17-toc-toggle-import-rename-design.md`

## Global Constraints

- Imported posts live at `src/pages/posts/<export-slug>.mdx` (existing code globs `*.mdx`).
- Frontmatter keys: `layout: "@/layouts/BlogPost"`, `title`, `publishDate`, `description`, `tags` (array).
- Tag `today-i-found` becomes `todayifound`.
- Images stay hotlinked; `images.gh40-dev.systems`, repo name and `githubUrl` are NOT renamed.
- Toggle key is `t`; ignored in input/textarea/select/contenteditable and with ctrl/meta/alt.
- `localStorage` access is wrapped in try/catch; ToC defaults to open.
- `npm run build` must pass; run prettier/eslint only on files touched (`npm run format` rewrites everything, don't use it).

## Review Focus

- Post with no headings: no ToC, no button, `t` does nothing.
- `t` pressed while typing in a form field or with Cmd/Ctrl held does not toggle.
- `localStorage` unavailable (private window): page still renders, toggle works for the session.
- Export post with missing `meta_description` or no `tags` (`thanks-i-hate-it`, `today-i-found-*`): builds, no `undefined` in output.
- Export post bodies containing `<`, `{`, or bare HTML that MDX rejects.

---

### Task 1: ToC toggle

**Files:**
- Modify: `src/layouts/BlogPost.astro` (aside + grid + script)

**Interfaces:**
- Produces: grid element `#post-grid` with `data-toc="open|closed"`; button `#toc-toggle`; aside `#toc`.

- [ ] **Step 1: Render only when headings exist.** Wrap the `<aside>` in `headings.length > 0`; add `id="post-grid"` to the grid div; when there are no headings use a single-column grid.
- [ ] **Step 2: Button.** In the aside header add `<button id="toc-toggle" type="button" aria-expanded="true" aria-controls="toc">Hide</button>` with a `<kbd>t</kbd>` hint. When closed, the aside collapses to just a "Show ToC (t)" button so the control stays reachable; the grid becomes one column (`data-toc="closed"` → `sm:grid-cols-1`) so the article gets full width.
- [ ] **Step 3: Script.** Inline `<script>` that reads `localStorage["toc"]` (try/catch), applies state on load, toggles on button click and on `keydown` for `t` (guards per Global Constraints), updates `aria-expanded` and button label, and writes state (try/catch).
- [ ] **Step 4: Verify.** `npm run build` passes. `npm run dev`, open `/posts/ibmcloud-pdns-vpc`: button and `t` hide/show, reload keeps state, article widens. Open a post without headings (check with `grep -L '^##' src/pages/posts/*.mdx`) and confirm no button. Check keyboard focus ring on the button and run the dev page with an input focused to confirm `t` is ignored (the site has no inputs; verify via the guard code path in devtools console by dispatching a keydown on `document.body` with `contentEditable`).
- [ ] **Step 5: Commit.** `git add src/layouts/BlogPost.astro && git commit -m "feat: toggleable table of contents"`

### Task 2: Import posts

**Files:**
- Create: `scripts/import_export.py` (outside `src/`), `src/pages/posts/<slug>.mdx` x16

**Interfaces:**
- Produces: `convert(path: Path) -> str` (full mdx text); CLI `python3 scripts/import_export.py gh40-export src/pages/posts` that converts the 16 slugs listed in the spec only.

- [ ] **Step 1: Write `convert`.** Parse the `---` frontmatter (simple `key: value` lines, stdlib only; split on first `: `). Map `published_date` → `publishDate` formatted `D Month YYYY` (matches existing posts, e.g. `13 September 2024`; keep the time-of-day ordering irrelevant), `meta_description` → `description` (fallback: first non-empty body line stripped of markdown, truncated to 160 chars), `tags` (comma-split, `today-i-found` → `todayifound`) → array, omitted when absent. Emit the layout line. Quote strings with `json.dumps`.
- [ ] **Step 2: MDX-safety pass in `convert`.** Outside fenced code blocks and inline code, escape `{`→`\{`, `}`→`\}` and `<` not starting a real tag or autolink→`&lt;`. Leave fenced blocks untouched.
- [ ] **Step 3: Run it** for the 16 slugs; refuse to overwrite an existing file (exit nonzero listing it).
- [ ] **Step 4: Verify.** `npm run build` passes (fix any remaining MDX errors by hand-editing the offending post and noting it). `ls src/pages/posts | wc -l` shows 30. Spot check `/posts/2024-homelab-recap`, `/posts/thanks-i-hate-it` (no tags, no description), `/tags/todayifound` lists old and new TIF posts, and `/posts` lists them in date order.
- [ ] **Step 5: Commit.** `git add scripts src/pages/posts && git commit -m "feat: import posts from second blog"`

### Task 3: Rename to ryantiffany.com

**Files:**
- Modify: `src/site-meta.config.ts:2`, `src/components/Header.astro:45`, `src/pages/index.astro:9`, `public/manifest.webmanifest` (name `ryantiffany.com`, short_name `ryantiffany.com`), `astro.config.ts:14` (`site: "https://ryantiffany.com"`), `public/robots.txt:3`, `src/pages/posts/terraform-variables-and-complex-uses.mdx:276`, `src/pages/posts/ibmcloud-pdns-vpc.mdx:13`, `src/components/Footer.astro` if it carries a site name.

- [ ] **Step 1: Replace** display name and absolute `https://gh40.net` URLs in the files above; do not touch `images.gh40-dev.systems`, `githubUrl`, or the repo name. Check imported posts for `gh40.net` links too: `grep -rn "gh40.net\|www.ryantiffany.com" src public`.
- [ ] **Step 2: Verify.** `grep -rn "gh40\.net" src public astro.config.ts` returns nothing except intentional ones; `npm run build` passes; `dist/sitemap-index.xml` and `dist/index.html` show ryantiffany.com.
- [ ] **Step 3: Commit.** `git add -A src public astro.config.ts && git commit -m "chore: rename site to ryantiffany.com"`

### Task 4: Final check

- [ ] `npm run build` clean; `npm run dev` smoke test of home, `/posts`, one old post, one imported post with toggle. Report anything skipped.

---

Self-review: all spec sections map to tasks (toggle→1, import→2, rename→3). `Dockerfile`/`.github` workflow may reference the old domain; Task 3 Step 1's grep covers `src public` only, so also run `grep -rn gh40 Dockerfile .github` and report rather than change deploy config.
