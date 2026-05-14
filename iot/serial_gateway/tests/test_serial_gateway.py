import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from serial_gateway import ingest_url, normalize_reading, parse_json_line


class SerialGatewayTests(unittest.TestCase):
    def test_normalize_soil_saturated_and_light_score(self):
        result = normalize_reading(
            {
                "soil_raw": 0,
                "humidity": 36.5,
                "temperature": 27.1,
                "light_raw": 120,
            }
        )

        self.assertEqual(result["moisture"], 100.0)
        self.assertEqual(result["humidity"], 56.5)
        self.assertEqual(result["temperature"], 27.1)
        self.assertEqual(result["light"], 117.3)

    def test_normalize_soil_dry_and_null_dht_values(self):
        result = normalize_reading(
            {
                "soil_raw": 220,
                "humidity": None,
                "temperature": None,
                "light_raw": 5,
            }
        )

        self.assertEqual(result["moisture"], 0.0)
        self.assertIsNone(result["humidity"])
        self.assertIsNone(result["temperature"])
        self.assertEqual(result["light"], 4.9)

    def test_normalize_rejects_invalid_fields(self):
        with self.assertRaises(ValueError):
            normalize_reading({"soil_raw": "wet", "humidity": None, "temperature": None, "light_raw": 5})

        with self.assertRaises(ValueError):
            normalize_reading({"soil_raw": 500, "humidity": "bad", "temperature": 27.0, "light_raw": 5})

        with self.assertRaises(ValueError):
            normalize_reading(
                {"soil_raw": 120, "humidity": 33.0, "temperature": 25.0, "light_raw": 14},
                soil_wet_raw=100,
                soil_dry_raw=100,
            )

    def test_normalize_uses_current_demo_soil_calibration(self):
        result = normalize_reading(
            {
                "soil_raw": 120,
                "humidity": 33.0,
                "temperature": 25.0,
                "light_raw": 14,
            }
        )

        self.assertEqual(result["moisture"], 45.5)
        self.assertEqual(result["humidity"], 53.0)
        self.assertEqual(result["temperature"], 25.0)
        self.assertEqual(result["light"], 13.7)

    def test_lightly_wet_demo_reading_does_not_saturate_to_100(self):
        result = normalize_reading(
            {
                "soil_raw": 40,
                "humidity": 33.0,
                "temperature": 25.0,
                "light_raw": 14,
            }
        )

        self.assertEqual(result["moisture"], 81.8)

    def test_parse_json_line(self):
        self.assertEqual(parse_json_line('{"soil_raw":500,"light_raw":20}'), {"soil_raw": 500, "light_raw": 20})
        self.assertEqual(
            parse_json_line('noise {"soil_raw":500,"humidity":25.0,"light_raw":42} tail'),
            {"soil_raw": 500, "humidity": 25.0, "light_raw": 42},
        )
        self.assertIsNone(parse_json_line("not-json"))
        self.assertIsNone(parse_json_line("[1,2,3]"))

    def test_ingest_url(self):
        self.assertEqual(
            ingest_url("http://127.0.0.1:8000/", "arduino-uno-001"),
            "http://127.0.0.1:8000/api/v1/ingest/sensors/arduino-uno-001/data",
        )


if __name__ == "__main__":
    unittest.main()
