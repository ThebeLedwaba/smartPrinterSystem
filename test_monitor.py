import unittest
from monitor import validate_printer, load_json_file

class TestMonitor(unittest.TestCase):
    def test_validate_printer(self):
        self.assertTrue(validate_printer({"name": "Printer1", "ip": "192.168.0.101"}))
        self.assertFalse(validate_printer({"name": "Printer2"}))
        self.assertFalse(validate_printer({"ip": "192.168.0.102"}))

    def test_load_json_file(self):
        # Should return default if file not found
        self.assertEqual(load_json_file("nonexistent.json", default={"a": 1}), {"a": 1})

if __name__ == "__main__":
    unittest.main()