import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from securesystemslib.exceptions import VerificationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import intoto_ci  # noqa: E402


class TestIntotoCI(unittest.TestCase):
    def test_end_to_end_pipeline_pass_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            keys_dir = root / "keys"
            meta_dir = root / "meta"
            work_dir = root / "work"
            work_dir.mkdir(parents=True)
            (work_dir / "input.txt").write_text("kata-agent-patch-v1\n", encoding="utf-8")

            owner_priv, owner_pub, owner_keyid = intoto_ci.generate_keypair(keys_dir, "owner")
            step1_priv, step1_pub, step1_keyid = intoto_ci.generate_keypair(keys_dir, "step1")
            step2_priv, step2_pub, _ = intoto_ci.generate_keypair(keys_dir, "step2")

            self.assertEqual(len(owner_keyid), 64)
            self.assertTrue(owner_priv.exists())
            self.assertTrue(owner_pub.exists())

            rc1 = intoto_ci.main(
                [
                    "run",
                    "--step-name",
                    "prepare",
                    "--working-dir",
                    str(work_dir),
                    "--metadata-dir",
                    str(meta_dir),
                    "--key-path",
                    str(step1_priv),
                    "--materials",
                    "input.txt",
                    "--products",
                    "manifest.txt",
                    "--",
                    sys.executable,
                    "-c",
                    "import pathlib; pathlib.Path('manifest.txt').write_text(pathlib.Path('input.txt').read_text().upper())",
                ]
            )
            self.assertEqual(rc1, 0)
            self.assertTrue((meta_dir / f"prepare.{step1_keyid[:8]}.link").exists())

            rc2 = intoto_ci.main(
                [
                    "run",
                    "--step-name",
                    "build",
                    "--working-dir",
                    str(work_dir),
                    "--metadata-dir",
                    str(meta_dir),
                    "--key-path",
                    str(step2_priv),
                    "--materials",
                    "manifest.txt",
                    "--products",
                    "artifact.bin",
                    "--",
                    sys.executable,
                    "-c",
                    "import pathlib; pathlib.Path('artifact.bin').write_text('built:' + pathlib.Path('manifest.txt').read_text())",
                ]
            )
            self.assertEqual(rc2, 0)

            spec_path = root / "layout-spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "expires_days": 7,
                        "steps": [
                            {
                                "name": "prepare",
                                "expected_materials": [["ALLOW", "input.txt"], ["ALLOW", "*"]],
                                "expected_products": [["CREATE", "manifest.txt"], ["ALLOW", "*"]],
                                "expected_command": [],
                                "threshold": 1,
                            },
                            {
                                "name": "build",
                                "expected_materials": [["MATCH", "manifest.txt", "WITH", "PRODUCTS", "FROM", "prepare"], ["ALLOW", "*"]],
                                "expected_products": [["CREATE", "artifact.bin"], ["ALLOW", "*"]],
                                "expected_command": [],
                                "threshold": 1,
                            },
                        ],
                        "inspect": [],
                    }
                ),
                encoding="utf-8",
            )

            layout_path = meta_dir / "root.layout"
            rc_lay = intoto_ci.main(
                [
                    "layout",
                    "--spec",
                    str(spec_path),
                    "--output",
                    str(layout_path),
                    "--key-path",
                    str(owner_priv),
                    "--step-key",
                    f"prepare={step1_pub}",
                    "--step-key",
                    f"build={step2_pub}",
                ]
            )
            self.assertEqual(rc_lay, 0)
            self.assertTrue(layout_path.exists())

            rc_ver = intoto_ci.main(
                [
                    "verify",
                    "--layout",
                    str(layout_path),
                    "--layout-key",
                    str(owner_pub),
                    "--link-dir",
                    str(meta_dir),
                ]
            )
            self.assertEqual(rc_ver, 0)

            link_files = list(meta_dir.glob("build.*.link"))
            self.assertEqual(len(link_files), 1)
            tampered = json.loads(link_files[0].read_text(encoding="utf-8"))
            tampered["signed"]["products"]["artifact.bin"]["sha256"] = "0" * 64
            link_files[0].write_text(json.dumps(tampered), encoding="utf-8")

            with self.assertRaises((VerificationError, Exception)):
                intoto_ci.main(
                    [
                        "verify",
                        "--layout",
                        str(layout_path),
                        "--layout-key",
                        str(owner_pub),
                        "--link-dir",
                        str(meta_dir),
                    ]
                )

    def test_ephemeral_key_and_key_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gh_out = root / "gh_output.txt"
            work_dir = root / "work"
            work_dir.mkdir(parents=True)
            meta_dir = root / "meta"

            old_out = os.environ.get("GITHUB_OUTPUT")
            os.environ["GITHUB_OUTPUT"] = str(gh_out)
            try:
                py_exe = sys.executable.replace("\\", "/")
                rc = intoto_ci.main(
                    [
                        "run",
                        "--step-name",
                        "ephemeral-step",
                        "--working-dir",
                        str(work_dir),
                        "--metadata-dir",
                        str(meta_dir),
                        "--products",
                        "out.txt",
                        "--command-str",
                        f"{py_exe} -c \"open('out.txt','w').write('hi')\"",
                    ]
                )
                self.assertEqual(rc, 0)
                output_text = gh_out.read_text(encoding="utf-8")
                self.assertIn("link-file=", output_text)
                self.assertIn("public-key-path=", output_text)
                self.assertIn("keyid=", output_text)
            finally:
                if old_out is None:
                    os.environ.pop("GITHUB_OUTPUT", None)
                else:
                    os.environ["GITHUB_OUTPUT"] = old_out


if __name__ == "__main__":
    unittest.main()
