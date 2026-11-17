import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONF = (ROOT / "nginx.conf").read_text() if (ROOT / "nginx.conf").exists() else ""
EXPORT = ROOT / "gh40-export"
RULE = re.compile(r"location = /([^/\s]+)/ \{ return 301 (\S+); \}")
REDIRECTS = dict(RULE.findall(CONF))
# old bearblog slug -> slug of the same post on this site (when it differs)
RENAMED = {
    "deploy-request-baskets-on-ibm-cloud-code-engine-using-terraform": "code-engine-rb",
    "expose-vpc-services-to-your-local-network-with-custom-resolvers-and-tailscale": "ibmcloud-pdns-vpc",
    "refresh-schematics-workspaces-using-code-engine-periodic-timer": "code-engine-schematics",
    "today-i-found-volume-1": "tif-1",
    "use-terraform-to-deploy-a-tailscale-subnet-router-for-interconnecting-ibm-cloud-vpcs": "ibmcloud-vpc-tailscale",
    "using-ibm-cloud-code-engine-as-a-webhook-receiver": "code-engine-webhook",
}


class RedirectTests(unittest.TestCase):
    def test_every_target_exists_on_the_site(self):
        self.assertTrue(REDIRECTS, "no redirect rules found in nginx.conf")
        for old, target in REDIRECTS.items():
            if target.startswith("/posts/"):
                slug = target.split("/")[2]
                self.assertTrue((ROOT / "src/pages/posts" / f"{slug}.mdx").exists(), f"{old} -> {target}")

    @unittest.skipUnless(EXPORT.exists(), "gh40-export not present")
    def test_every_published_export_post_redirects_to_its_new_url(self):
        for md in EXPORT.glob("*.md"):
            head = md.read_text().split("---\n")[1]
            if "is_page: true" in head or "publish: false" in head:
                continue
            slug = md.stem
            expected = f"/posts/{RENAMED.get(slug, slug)}/"
            self.assertEqual(REDIRECTS.get(slug), expected, slug)

    def test_old_pages_and_www_are_handled(self):
        for page in ("cheat-sheets", "today-i-found", "projects", "elsewhere"):
            self.assertIn(page, REDIRECTS)
        self.assertIn("$host = www.ryantiffany.com", CONF)


if __name__ == "__main__":
    unittest.main()
