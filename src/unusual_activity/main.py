import json

from flask import (
    Flask,
    request,
)

from src.unusual_activity.constants import (
    CODE_EXCESSIVE_WITHDRAWL_AMOUNT,
    CODE_CONSECUTIVE_WITHDRAWLS,
    EXCESSIVE_WITHDRAWL_AMOUNT,
    CONSECUTIVE_WITHDRAWLS,
)


class EventStore:
    def __init__(self):
        self.db = []

    def reset(self):
        self.db = []

    def add_event(self, event: dict) -> None:
        self.db.append(event)

    def has_consecutive_withdrawls(self, user_id: int) -> bool:
        user_recs = [x for x in self.db if x["user_id"] == user_id]
        last_recs = user_recs[-CONSECUTIVE_WITHDRAWLS:]
        if len(last_recs) < CONSECUTIVE_WITHDRAWLS:
            return False
        return all(x for x in last_recs if x["type"] == "withdrawl")


def create_app(event_store: EventStore):

    app = Flask(__name__)

    LAST_T = 0


    @app.post("/event")
    def event():
        req = request.get_json()
        alert_codes = []
        event_store.add_event(req)

        # # Validate body. Return 400 on missing required key from body.
        amount = req["amount"]

        # # Validate `t` is increasing between requests.
        # _t = int(t)
        # global LAST_T  # TODO: move away from `global` for global tracking!
        # if _t <= LAST_T:
        #     # t needs to increase each request!
        #     abort(400)
        # LAST_T = _t

        ## Stateless validation checks:

        if _has_excessive_withdrawl_amount(amount):
            alert_codes.append(CODE_EXCESSIVE_WITHDRAWL_AMOUNT)

        if event_store.has_consecutive_withdrawls(req["user_id"]):
            alert_codes.append(CODE_CONSECUTIVE_WITHDRAWLS)


        # TODO: Parse JSON body.
        # TODO: Minor: Return 201 on POST success.
        # TODO: Business Logic validation.
        # TODO: Generate Response.



        ret_val = {
            "alert": bool(alert_codes),
            "alert_codes": alert_codes,
            "user_id": req["user_id"]
        }
        return json.dumps(ret_val)

    return app



def _has_excessive_withdrawl_amount(amount: str) -> bool:
    # Validate excessive withdrawl amount:
    _amount = float(amount)
    return _amount > EXCESSIVE_WITHDRAWL_AMOUNT
