"""Offline contract checks; never calls LibTV or submits media generation."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/libtv/skills/libtv-video-production"


class VideoProductionTests(unittest.TestCase):
    def test_reference_inventory(self):
        expected = {
            "mcp-reference.md", "production-workflow.md", "prompt-recipes.md",
            "editing-pipeline.md", "content-safety-and-env.md", "pitfalls.md",
            "capability-boundaries.md",
        }
        self.assertEqual({p.name for p in (SKILL / "references").glob("*.md")}, expected)
        for name in ("SKILL.md", "README.md", "DESIGN.md", "UPSTREAM.md", "LICENSE"):
            self.assertTrue((SKILL / name).is_file(), name)

    def test_mcp_contract_and_authorization_are_documented(self):
        contract = (SKILL / "references/mcp-reference.md").read_text()
        for token in ("doctor", "target_project", "search_models", "get_model",
                      "{{Node <nodeId>}}", "idempotencyKey", "task_id",
                      "mediaPersistence", "params.count", "upload_complete"):
            self.assertIn(token, contract)
        entry = (SKILL / "SKILL.md").read_text()
        for token in ("图片、视频、音频", "明确授权", "run=false", "付费", "原键"):
            self.assertIn(token, entry)

    def test_no_cli_execution_or_fixed_model_routing(self):
        patterns = (
            r"libtv (?:login|node|project|upload|model|account)\b",
            r"\.libtv/(?:credentials|project)\.json", r"\{\{(?:Image|Video) \d+\}\}",
            r"-s (?:model|modeType|resolution)=", r"curl[^\n]*\|\s*(?:sh|bash)",
        )
        for path in SKILL.rglob("*.md"):
            # Describing forbidden old placeholders is allowed, executing them is not.
            text = "\n".join(re.findall(r"```[^\n]*\n(.*?)```", path.read_text(), re.S))
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, text), f"{path}: {pattern}")

    def test_license_and_pinned_source(self):
        license_text = (SKILL / "LICENSE").read_text()
        for token in ("MIT License", "2026 LibTV Video Agent contributors",
                      "Permission is hereby granted", 'THE SOFTWARE IS PROVIDED "AS IS"'):
            self.assertIn(token, license_text)
        provenance = (SKILL / "UPSTREAM.md").read_text()
        self.assertIn("https://github.com/PomeloR611/libtv-video-agent", provenance)
        self.assertRegex(provenance, r"`[0-9a-f]{40}`")


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                     "ffmpeg/ffprobe unavailable; static tests still run")
class EditingExamplesTests(unittest.TestCase):
    def run_command(self, command, **kwargs):
        return subprocess.run(command, check=True, capture_output=True, text=True,
                              timeout=60, **kwargs)

    def run_example(self, name, **values):
        doc = (SKILL / "references/editing-pipeline.md").read_text()
        blocks = re.findall(r"```bash\n(.*?)```", doc, re.S)
        matches = [block for block in blocks if block.startswith(f"# example: {name}\n")]
        self.assertEqual(len(matches), 1)
        # Executes only this repository's authored examples, with synthetic local media.
        env = {**os.environ, **{key: str(value) for key, value in values.items()}}
        self.run_command(["bash", "-eu", "-c", matches[0]], env=env)

    def test_audio_and_silent_inputs_crossfade(self):
        with tempfile.TemporaryDirectory(prefix="libtv-editing-") as folder:
            base = Path(folder)
            raw_a, raw_b = base / "有声 input.mp4", base / "无声 input.mp4"
            a, b, output = base / "a.mp4", base / "b.mp4", base / "final.mp4"
            common = ["ffmpeg", "-v", "error", "-nostdin", "-n"]
            self.run_command(common + ["-f", "lavfi", "-i", "color=red:s=160x120:r=24:d=2",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(raw_a)])
            self.run_command(common + ["-f", "lavfi", "-i", "color=blue:s=160x120:r=24:d=3",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(raw_b)])
            settings = dict(WIDTH=160, HEIGHT=120, FPS=24)
            self.run_example("normalize-audio", INPUT=raw_a, OUTPUT=a, DURATION=2, **settings)
            self.run_example("normalize-silent", INPUT=raw_b, OUTPUT=b, DURATION=3, **settings)
            original = a.read_bytes()
            with self.assertRaises(subprocess.CalledProcessError):
                self.run_example("normalize-audio", INPUT=raw_a, OUTPUT=a, DURATION=2, **settings)
            self.assertEqual(a.read_bytes(), original)
            self.run_example("crossfade", A=a, B=b, OUTPUT=output, DA=2, DB=3, T=0.5, OFFSET=1.5)
            result = self.run_command(["ffprobe", "-v", "error", "-show_streams",
                                       "-show_format", "-of", "json", str(output)])
            media = json.loads(result.stdout)
            video = next(s for s in media["streams"] if s["codec_type"] == "video")
            audio = next(s for s in media["streams"] if s["codec_type"] == "audio")
            self.assertEqual((video["width"], video["height"]), (160, 120))
            self.assertEqual(video["avg_frame_rate"], "24/1")
            self.assertAlmostEqual(float(video["duration"]), 4.5, delta=0.1)
            self.assertAlmostEqual(float(audio["duration"]), 4.5, delta=0.1)
            self.assertEqual(audio["sample_rate"], "48000")
            self.assertEqual(audio["channels"], 2)


if __name__ == "__main__":
    unittest.main()
