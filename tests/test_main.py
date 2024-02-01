"""Test the exposed endpoint in main.py.

Thoughts around using the features of pytest:

- Fixtures (`conftest.py`) to simplify the creation of common functionality.
- Parametrize decorator to do matrix testing.

I'm also doing some long-form tests (with duplication) just to get
code under test quickly. Usually I'll refactor these to reduce the
duplication, but will try not to optimise early. ie. Red-Green-Refactor
mentality.
"""
import json

import pytest

from src.unusual_activity.constants import (
    CODE_EXCESSIVE_WITHDRAWL_AMOUNT,
    CODE_CONSECUTIVE_WITHDRAWLS,
    CODE_CONSECUTIVE_INCREASING_DEPOSITS,
    CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD,
    EXCESSIVE_WITHDRAWL_AMOUNT,
    EXCESSIVE_DEPOSIT_AMOUNT,
    EXCESSIVE_DEPOSIT_PERIOD_SECONDS,
)


class TestMain:
    def test_hardcoded_event(self, client):
        """Testing of the initial stub.
        TODO: This will be deleted once the business logic has been
        implemented.
        """
        exp = (b'{"alert": true, "alert_codes": [30, 123], "user_id": 1}')
        exp_dict = {"alert": True, "alert_codes": [30, 123], "user_id": 1}
        response = client.post("/event")
        assert response.data == exp
        assert json.loads(response.data) == exp_dict

    def test_initial_event_no_alert(self, client):
        """Smoke check that no alerts are raised when there are no
        bad events to trigger an alert.
        """
        exp_dict = {"alert": False, "alert_codes": [], "user_id": 1}
        data = {"type": "deposit", "amount": "42.00", "user_id": 1, "t": 1}
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

    def test_excessive_withdrawl_alert(self, client):
        exp_dict = {
            "alert": True,
            "alert_codes": [
                CODE_EXCESSIVE_WITHDRAWL_AMOUNT,
            ],
            "user_id": 1
        }
        data = {
            "type": "withdrawl",
            "amount": f"{EXCESSIVE_WITHDRAWL_AMOUNT + 1}",
            "user_id": 1,
            "t": 1
        }
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

    def test_consecutive_withdrawls_alert(self, client):
        exp_dict = {"alert": False, "alert_codes": [], "user_id": 1}
        exp_alert_dict = {
            "alert": True,
            "alert_codes": [
                CODE_CONSECUTIVE_WITHDRAWLS,
            ],
            "user_id": 1
        }
        # TODO: Refactor to iterate for: CONSECUTIVE_WITHDRAWLS -1,
        # then explicit check for alert!
        data = {"type": "withdrawl", "amount": "2.00", "user_id": 1, "t": 1}
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 2
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 3
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_alert_dict

    def test_consecutive_increasing_deposits_alert(self, client):
        exp_dict = {"alert": False, "alert_codes": [], "user_id": 1}
        exp_alert_dict = {
            "alert": True,
            "alert_codes": [
                CODE_CONSECUTIVE_INCREASING_DEPOSITS,
            ],
            "user_id": 1
        }
        # TODO: Refactor to iterate for:
        # CONSECUTIVE_INCREASING_DEPOSITS -1, then explicit check for
        # alert!
        data = {"type": "deposit", "amount": "2.00", "user_id": 1, "t": 1}
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 2
        data["amount"] = "4.00"
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 3
        data["amount"] = "6.00"
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_alert_dict

    def test_consecutive_increasing_deposits_ignoring_withdrawls_alert(self, client):
        exp_dict = {"alert": False, "alert_codes": [], "user_id": 1}
        exp_alert_dict = {
            "alert": True,
            "alert_codes": [
                CODE_CONSECUTIVE_INCREASING_DEPOSITS,
            ],
            "user_id": 1
        }
        data = {"type": "deposit", "amount": "2.00", "user_id": 1, "t": 1}
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 2
        data["amount"] = "4.00"
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        print(
            "Withdrawl's MUST be ignored as part of the: 3 consecutive_"
            "increasing deposits, alert!"
        )
        withdrawl_data = {"type": "withdrawl", "amount": "1.00", "user_id": 1, "t": 3}
        response = client.post("/event", data=withdrawl_data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 4
        data["amount"] = "6.00"
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_alert_dict

    def test_excessive_deposit_amount_in_period_alert(self, client):
        exp_dict = {"alert": False, "alert_codes": [], "user_id": 1}
        exp_alert_dict = {
            "alert": True,
            "alert_codes": [
                CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD,
            ],
            "user_id": 1
        }
        data = {
            "type": "deposit",
            "amount": f"{EXCESSIVE_DEPOSIT_AMOUNT - 1}",
            "user_id": 1,
            "t": 1
        }
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = 2
        data["amount"] = "10.00"
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_alert_dict

    def test_excessive_deposit_amount_outside_period_does_not_alert(self, client):
        exp_dict = {"alert": False, "alert_codes": [], "user_id": 1}
        data = {
            "type": "deposit",
            "amount": f"{EXCESSIVE_DEPOSIT_AMOUNT - 1}",
            "user_id": 1,
            "t": 1
        }
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

        data["t"] = EXCESSIVE_DEPOSIT_PERIOD_SECONDS + 5
        data["amount"] = "10.00"
        response = client.post("/event", data=data)
        assert response.status_code == 200
        assert json.loads(response.data) == exp_dict

    def test_multiple_alerts(self, client):
        # Trigger: CODE_CONSECUTIVE_INCREASING_DEPOSITS
        # Trigger: CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD
        data = {
            "type": "deposit",
            "amount": f"{EXCESSIVE_DEPOSIT_AMOUNT}",
            "user_id": 1,
            "t": 1
        }
        assert client.post("/event", data=data).status_code == 200
        data["t"] = 2
        data["amount"] = f"{EXCESSIVE_DEPOSIT_AMOUNT + 2}"
        assert client.post("/event", data=data).status_code == 200
        data["t"] = 3
        data["amount"] = f"{EXCESSIVE_DEPOSIT_AMOUNT + 3}"
        response = client.post("/event", data=data).status_code
        assert response.status_code == 200
        _alert_codes = json.loads(response.data)["alert_codes"]
        assert CODE_CONSECUTIVE_INCREASING_DEPOSITS in _alert_codes
        assert CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD in _alert_codes

    @pytest.mark.parametrize(
        "msg,data,exp_code", (
            # 200
            ("Good deposit", {"type": "deposit", "amount": "42.00", "user_id": 1, "t": 1} , 200),
            ("Good withdrawl", {"type": "withdrawl", "amount": "40.00", "user_id": 1, "t": 2} , 200),
            # 400 - Missing Required fields.
            ("Empty Body", {} , 400),
            ("Missing type", {"amount": "40.00", "user_id": 1, "t": 10} , 400),
            ("Missing amount", {"type": "withdrawl", "user_id": 1, "t": 11} , 400),
            ("Missing user_id", {"type": "withdrawl", "amount": "40.00", "t": 12} , 400),
            ("Missing t", {"type": "withdrawl", "amount": "40.00", "user_id": 1,} , 400),
            # 400 - Bad types.
            ("Bad type type", {"type": None, "amount": "40.00", "user_id": 1, "t": 20} , 400),
            ("Bad amount type", {"type": "withdrawl", "amount": None, "user_id": 1, "t": 21} , 400),
            ("Bad user_id type", {"type": "withdrawl", "amount": "40.00", "user_id": None, "t": 22} , 400),
            ("Bad t type", {"type": "withdrawl", "amount": "40.00", "user_id": 1, "t": None} , 400),
            # 400 - Unexpected Values.
            ("Unexpected type", {"type": "unknown", "amount": "40.00", "user_id": 1, "t": 30} , 400),
            ("Unexpected amount deposit", {"type": "deposit", "amount": "-40.00", "user_id": 1, "t": 31} , 400),
            ("Unexpected amount withdrawl", {"type": "withdrawl", "amount": "-40.00", "user_id": 1, "t": 32} , 400),
            ("Unexpected user_id", {"type": "deposit", "amount": "40.00", "user_id": -1, "t": 33} , 400),
            ("Unexpected t", {"type": "deposit", "amount": "40.00", "user_id": 1, "t": -34} , 400),
        )
    )
    def test_invalid_event_post_body_returns_400(self, client, msg, data, exp_code):
        response = client.post("/event", data=data)
        print(msg)
        assert response.status_code == exp_code
