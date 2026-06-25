import unittest
from pathlib import Path


class ApiRouteContractTests(unittest.TestCase):
    def setUp(self):
        self.main_source = Path("backend/app/main.py").read_text()

    def test_root_route_is_defined(self):
        self.assertIn('@app.get("/")', self.main_source)
        self.assertIn('"app": "DocuSense AI"', self.main_source)
        self.assertIn('"status": "running"', self.main_source)
        self.assertIn('"health": "/health"', self.main_source)
        self.assertIn('"docs": "/docs"', self.main_source)

    def test_health_route_is_defined(self):
        self.assertIn('@app.get("/health")', self.main_source)
        self.assertIn('"status": "DocuSense AI is running"', self.main_source)


if __name__ == "__main__":
    unittest.main()
