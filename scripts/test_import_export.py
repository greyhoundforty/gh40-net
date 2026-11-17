import unittest

from import_export import convert_text

SAMPLE = """---
title: Today I Found: Volume 2
slug: today-i-found-volume-2
published_date: 2024-11-04T10:00:00+00:00
tags: today-i-found, curl
publish: true
meta_description: The second post in the series.
---

Body with {braces} and a < b.

```bash
echo {keep} < this
```

Inline `{code}` stays.
"""


class ConvertTests(unittest.TestCase):
    def test_frontmatter_is_mapped(self):
        out = convert_text(SAMPLE)
        self.assertIn('layout: "@/layouts/BlogPost"', out)
        self.assertIn('title: "Today I Found: Volume 2"', out)
        self.assertIn("publishDate: 04 November 2024", out)
        self.assertIn('description: "The second post in the series."', out)
        self.assertIn('tags: ["todayifound", "curl"]', out)
        self.assertNotIn("slug:", out)
        self.assertNotIn("publish: true", out)

    def test_missing_tags_omitted_and_description_falls_back_to_first_line(self):
        src = "---\ntitle: Horse\npublished_date: 2025-09-16T07:29:28.604879+00:00\ntags: \n---\n\nOn today's **episode**: [link](http://x.y)\n"
        out = convert_text(src)
        self.assertNotIn("tags:", out)
        self.assertIn('description: "On today\'s episode: link"', out)

    def test_braces_and_angle_escaped_outside_code_only(self):
        out = convert_text(SAMPLE)
        self.assertIn(r"Body with \{braces\} and a &lt; b.", out)
        self.assertIn("echo {keep} < this", out)
        self.assertIn("`{code}`", out)

    def test_real_html_tags_survive_and_autolinks_become_markdown_links(self):
        out = convert_text("---\ntitle: T\npublished_date: 2025-01-01T00:00:00+00:00\n---\n\n<img src=\"a.png\"> and <https://x.y>\n")
        self.assertIn('<img src="a.png">', out)
        self.assertIn("[https://x.y](https://x.y)", out)
        self.assertNotIn("<https://x.y>", out)

    def test_fallback_description_is_cut_at_a_word_boundary(self):
        words = " ".join(["alpha"] * 40)
        out = convert_text(f"---\ntitle: T\npublished_date: 2025-01-01T00:00:00+00:00\n---\n\n{words}\n")
        desc = [l for l in out.splitlines() if l.startswith("description:")][0]
        self.assertTrue(desc.endswith('alpha…"'), desc)
        self.assertLessEqual(len(desc), len('description: ""') + 161)


if __name__ == "__main__":
    unittest.main()
