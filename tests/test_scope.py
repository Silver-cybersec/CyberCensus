#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""资产范围过滤：URL 解析、可注册域、范围内/相似/无关分类。"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cybercensus  # noqa: E402


class TestRegistrable(unittest.TestCase):
    def test_common_suffixes(self):
        self.assertEqual(cybercensus.registrable_domain("a.b.example.com"), "example.com")
        self.assertEqual(cybercensus.registrable_domain("x.example.com.cn"), "example.com.cn")
        self.assertEqual(cybercensus.registrable_domain("gov.example.gov.cn"), "example.gov.cn")
        self.assertEqual(cybercensus.registrable_domain("localhost"), "localhost")


class TestScope(unittest.TestCase):
    def test_parse_urls_domains_ips(self):
        scope = cybercensus.parse_scope_items([
            "https://www.example.com/login?x=1",
            "api.example.com",
            "203.0.113.9",
            "# comment",
            "",
        ])
        self.assertIn("www.example.com", scope["hosts"])
        self.assertIn("api.example.com", scope["hosts"])
        self.assertIn("203.0.113.9", scope["ips"])
        self.assertIn("example.com", scope["registrables"])

    def test_classify(self):
        scope = cybercensus.parse_scope_items(["https://www.example.com"])
        self.assertEqual(cybercensus.classify_scope("www.example.com", "", scope), "范围内")
        self.assertEqual(cybercensus.classify_scope("sub.www.example.com", "", scope), "范围内")
        self.assertEqual(cybercensus.classify_scope("example.com", "", scope), "相似")
        self.assertEqual(cybercensus.classify_scope("other.com", "203.0.113.9",
                                                    cybercensus.parse_scope_items(["203.0.113.9"])),
                         "相似")
        self.assertEqual(cybercensus.classify_scope("other.com", "", scope), "无关")

    def test_scope_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "scope.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# 范围\nhttps://www.example.com\n10.0.0.1\n")
            items = cybercensus.load_scope_file(p)
            self.assertEqual(items, ["https://www.example.com", "10.0.0.1"])


if __name__ == "__main__":
    unittest.main()
