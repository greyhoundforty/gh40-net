# ToC toggle, second-blog import, rename to ryantiffany.com

## Intent
Return to the astro-cactus template with three changes: (1) let readers hide/show the
post table of contents, (2) fold posts from the old second blog (`gh40-export/`) into
this site, (3) rename the site to ryantiffany.com.

## Goals
- ToC toggle on posts with headings: button in the ToC header plus the `t` key
  (ignored while typing in inputs/textareas/contenteditable, and with modifier keys).
  Collapsing hides the sidebar and lets the article use full width. State persists in
  `localStorage` (wrapped in try/catch). ToC is open by default.
- Import the 16 posts missing from the site (see list below), converted to this site's format.
- Rename: display name and canonical URL become ryantiffany.com.

## Non-goals / anti-goals
- No mobile ToC (it is already hidden below `sm`).
- No redesign of the theme. Do not touch the Cheatsheet layout beyond what it already shares.
- Do not import pages (`cheat-sheets`, `elsewhere`, `projects`, `today-i-found`),
  unpublished `test-referrer`, or posts already on the site under other slugs.

## Approaches
- ToC toggle: (a) small inline script + CSS class on the grid (chosen: no new deps, fits Astro
  static output); (b) a framework island (rejected: overkill).
- Import: (a) one-off conversion script, files committed as `.mdx` (chosen: existing code globs
  `*.mdx`); (b) switch the site to also glob `.md` (rejected: touches several pages).

## Decisions
- Import list (16): 2024-homelab-recap, homelab-monitoring, default-apps-2025,
  expose-local-services-to-your-tailnet-and-beyond-with-serve-and-funnel, claude-oco,
  claude-mcp-cookiecutter, ibmcloud-vpc-mcp, tg-ssh-manager, new-project-kylfuskofu,
  seven-songs-the-beths, thanks-i-hate-it, today-i-found-volume-2, -volume-3,
  -volume-2025-01-03, -volume-2025-01-09, -volume-2025-03-03.
- Frontmatter: `layout: "@/layouts/BlogPost"`, `title`, `publishDate` (from `published_date`),
  `description` (from `meta_description`, fallback to a first-sentence or empty), `tags` array.
  Slug = filename, kept as the export slug. Images stay hotlinked.
- Tag `today-i-found` becomes `todayifound` to match existing posts.
- Rename: `site-meta.config.ts` title, Header, index title, manifest name/short_name,
  `astro.config.ts` site, `robots.txt` sitemap, and absolute self-links to gh40.net in posts.
  Left alone: image host `images.gh40-dev.systems`, repo name and `githubUrl`.
- `astro build` must pass; fix MDX-hostile content (`<`, `{`) in imported posts.

## Left to the builder
Exact markup/styling of the button, wording of the key hint, handling of posts whose
`meta_description` is missing, and any import-time MDX escaping fixes.
