#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定时巡航（--tasks）的单元测试：周期解析、任务文件加载、参数拆分。"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cybercensus  # noqa: E402


class TestIntervals(unittest.TestCase):
    def test_units(self):
        self.assertEqual(cybercensus.parse_interval("30m"), 1800)
        self.assertEqual(cybercensus.parse_interval("6h"), 21600)
        self.assertEqual(cybercensus.parse_interval("1d"), 86400)
        self.assertEqual(cybercensus.parse_interval(" 7D "), 604800)

    def test_invalid_uses_default(self):
        self.assertEqual(cybercensus.parse_interval("abc", 123), 123)
        self.assertEqual(cybercensus.parse_interval("", 123), 123)
        self.assertEqual(cybercensus.parse_interval("10s", 123), 123)


class TestPrune(unittest.TestCase):
    def test_keeps_newest_and_skips_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            names = []
            for ts in ("20260101_000000", "20260102_000000", "20260103_000000"):
                for suffix in (".html", ".csv", "_all.csv", ".json"):
                    n = "cybercensus_%s%s" % (ts, suffix)
                    open(os.path.join(d, n), "w").close()
                    names.append(n)
            baseline = os.path.join(d, "baseline.json")
            open(baseline, "w").close()

            removed = cybercensus.prune_reports(d, 2)
            self.assertEqual(len(removed), 4)
            left = sorted(os.listdir(d))
            self.assertIn("baseline.json", left)
            self.assertFalse(any("20260101" in n for n in left))
            self.assertTrue(any("20260103" in n for n in left))

    def test_zero_disables(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "cybercensus_20260101_000000.html"), "w").close()
            self.assertEqual(cybercensus.prune_reports(d, 0), [])


class TestTaskFile(unittest.TestCase):
    def test_load_both_shapes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "tasks.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"tasks": [{"name": "a", "argv": ["--version"]}]}, f)
            self.assertEqual(len(cybercensus.load_task_file(p)), 1)
            with open(p, "w", encoding="utf-8") as f:
                json.dump([{"name": "b"}], f)
            self.assertEqual(cybercensus.load_task_file(p)[0]["name"], "b")

    def test_argv_and_args(self):
        self.assertEqual(cybercensus._task_argv({"argv": ["-n", "某单位"]}),
                         ["-n", "某单位"])
        self.assertEqual(cybercensus._task_argv({"args": '-n "某单位" -d example.com'}),
                         ["-n", "某单位", "-d", "example.com"])
        self.assertEqual(cybercensus._task_argv({}), [])

    def test_active_detection(self):
        self.assertTrue(cybercensus._task_is_active(["-d", "x", "--active"]))
        self.assertTrue(cybercensus._task_is_active(["--scan-asn"]))
        self.assertFalse(cybercensus._task_is_active(["--verify"]))


if __name__ == "__main__":
    unittest.main()
