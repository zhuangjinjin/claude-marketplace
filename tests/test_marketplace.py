"""Offline regression checks for the Claude Code marketplace conversion."""

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/libtv"
SKILLS = {
    "libtv-to-treatment", "libtv-blender-live-action",
    "music-driven-product-ad", "libtv-video-production",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MarketplaceTests(unittest.TestCase):
    def test_marketplace_resolves_plugin(self):
        market = read_json(ROOT / ".claude-plugin/marketplace.json")
        self.assertEqual(market["name"], "libtv-claude")
        self.assertTrue(market["owner"]["name"])
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual((ROOT / entry["source"]).resolve(), PLUGIN)
        manifest = read_json(PLUGIN / ".claude-plugin/plugin.json")
        self.assertEqual(entry["name"], manifest["name"])
        self.assertEqual(entry["version"], manifest["version"])
        self.assertNotIn("interface", manifest)

    def test_mcp_is_http_without_codex_options_or_credentials(self):
        config = read_json(PLUGIN / ".mcp.json")
        self.assertEqual(config, {"mcpServers": {"libtv": {
            "type": "http", "url": "https://mcp.liblib.tv/mcp",
        }}})

    def test_all_skills_have_matching_frontmatter(self):
        entries = list((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual({p.parent.name for p in entries}, SKILLS)
        for path in entries:
            text = path.read_text()
            frontmatter = text.split("---", 2)[1]
            self.assertIn(f"name: {path.parent.name}\n", frontmatter)
            self.assertRegex(frontmatter, r"(?m)^description: .+")
            self.assertIn("## Claude Code compatibility", text)

    def test_no_codex_manifests_or_runtime_calls(self):
        self.assertFalse((ROOT / ".agents").exists())
        self.assertFalse(list(PLUGIN.rglob(".codex-plugin")))
        self.assertFalse(list(PLUGIN.rglob("openai.yaml")))
        for path in (PLUGIN / "skills").rglob("*.md"):
            text = path.read_text()
            for legacy in ("right Codex panel", "tab.pressKey(", "$music-driven-product-ad", "~/.codex"):
                self.assertNotIn(legacy, text, str(path))

    def test_local_markdown_links_resolve(self):
        for path in (PLUGIN / "skills").rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                self.assertTrue((path.parent / target).exists(), f"{path}: {target}")

    def test_score_assets_and_attribution_preserved(self):
        scores = PLUGIN / "skills/music-driven-product-ad/assets/scores"
        catalog = read_json(scores / "catalog.json")
        self.assertEqual(len(catalog["pieces"]), 8)
        for piece in catalog["pieces"]:
            self.assertTrue((scores / f'{piece["id"]}.score.json').is_file())
            self.assertTrue((scores / f'{piece["id"]}.mid').is_file())
        reference = (PLUGIN / "skills/music-driven-product-ad/references/repertoire.md").read_text()
        self.assertIn("Creative Commons Attribution-ShareAlike 4.0", reference)
        self.assertIn("Alexander Brock", reference)


if __name__ == "__main__":
    unittest.main()
