from pathlib import Path
import tempfile
import unittest
import update


class BuildTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(update.parse("EXAMPLE.COM\nexample.com\n# comment\n"), {"example.com"})
        for bad in ("<html>error</html>", "https://example.com", "999.999.999.999/32", "bad domain"):
            with self.assertRaises(ValueError):
                update.parse(bad)
        self.assertEqual(update.parse("149.154.160.0/20\n2001:b28:f23d::/48", True), {"149.154.160.0/20"})

    def test_build_and_failure_keeps_previous(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "additions.txt").write_text("72.56.28.223/32\n")
            (root / "exclusions.txt").write_text(".ua\nua\n")
            base = "\n".join([f"domain{i}.example" for i in range(800)] + ["x.com", "youtube.com", "googlevideo.com", "tiktok.com", ".ua", "specific.ua"])
            telegram = "\n".join([f"telegram{i}.example" for i in range(10)] + ["telegram.org"])
            sources = [base, "tiktok.com", telegram, "149.154.160.0/20"]
            mapping = dict(zip((item[0] for item in update.SOURCES), sources))
            update.build(root, mapping.__getitem__)
            previous = (root / "domains.txt").read_bytes()
            entries = update.parse(previous.decode())
            self.assertNotIn(".ua", entries)
            self.assertIn("specific.ua", entries)
            self.assertIn("72.56.28.223/32", entries)
            self.assertEqual(previous.count(b"tiktok.com\n"), 1)
            mapping[update.SOURCES[0][0]] = "<html>upstream failure</html>"
            with self.assertRaises(ValueError):
                update.build(root, mapping.__getitem__)
            self.assertEqual((root / "domains.txt").read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
