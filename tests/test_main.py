"""Test the exposed endpoint in main.py."""
import json


class TestMain:
    def test_hardcoded_event(self, client):
        exp = (b'{"alert": true, "alert_codes": [30, 123], "user_id": 1}')
        exp_dict = {"alert": True, "alert_codes": [30, 123], "user_id": 1}
        response = client.post("/event")
        assert response.data == exp
        assert json.loads(response.data) == exp_dict
