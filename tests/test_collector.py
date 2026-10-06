import json
import unittest
from unittest import mock

from collector import sys_info_collector as collector


class CollectorTests(unittest.TestCase):
    def test_no_battery_is_reported_cleanly(self):
        with mock.patch.object(collector.psutil, "sensors_battery", return_value=None):
            info = collector.get_battery_info()
        self.assertFalse(info["present"])
        self.assertIn("No battery", info["status"])

    def test_system_info_has_expected_shape(self):
        info = collector.get_system_info()
        for key in (
            "boot_time",
            "uptime_days",
            "uptime_hours",
            "uptime_minutes",
            "current_time",
            "timezone",
        ):
            self.assertIn(key, info)

    def test_collect_all_json_serializes_unicode(self):
        sample = {"os": {"name": "Test OS"}, "note": "شبکه"}
        with mock.patch.object(collector, "collect_all", return_value=sample):
            raw = collector.collect_all_json()
        self.assertEqual(json.loads(raw), sample)
        self.assertIn("شبکه", raw)


if __name__ == "__main__":
    unittest.main()
