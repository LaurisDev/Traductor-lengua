import unittest
from unittest.mock import patch

from pymongo.errors import ServerSelectionTimeoutError

try:
    import web_server
except ModuleNotFoundError as error:
    if error.name != "flask":
        raise
    web_server = None


@unittest.skipIf(web_server is None, "Instala Flask para correr las pruebas de la version web.")
class WebServerTests(unittest.TestCase):
    def setUp(self):
        self.client = web_server.app.test_client()

    def test_health_and_web_ui_are_served(self):
        health = self.client.get("/health")
        page = self.client.get("/")
        bridge = self.client.get("/browser_api.js")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json(), {"status": "ok"})
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"browser_api.js", page.data)
        self.assertEqual(bridge.status_code, 200)
        page.close()
        bridge.close()

    def test_api_proxy_dispatches_browser_calls(self):
        class FakeAPI:
            def login(self, username, password):
                return {"ok": True, "username": username}

        class FakeController:
            def get_web_api(self):
                return FakeAPI()

        with patch.object(web_server, "_controller", return_value=FakeController()):
            response = self.client.post("/api/login", json=["demo", "password"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True, "username": "demo"})

    def test_api_proxy_rejects_invalid_argument_shape(self):
        response = self.client.post("/api/login", json={"username": "demo"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_api_reports_database_initialization_failure(self):
        with patch.object(web_server, "_controller", side_effect=RuntimeError("database unavailable")):
            response = self.client.post("/api/get_state", json=[])

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "database_unavailable")
        self.assertNotIn("database unavailable", response.get_json()["error"])

    def test_api_reports_database_query_failure(self):
        class FakeAPI:
            def get_state(self):
                raise ServerSelectionTimeoutError("database unavailable")

        class FakeController:
            def get_web_api(self):
                return FakeAPI()

        with patch.object(web_server, "_controller", return_value=FakeController()):
            response = self.client.post("/api/get_state", json=[])

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "database_unavailable")


if __name__ == "__main__":
    unittest.main()
