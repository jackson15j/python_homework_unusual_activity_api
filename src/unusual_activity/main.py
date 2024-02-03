import json

from src.unusual_activity.constants import (
    CODE_EXCESSIVE_WITHDRAWAL_AMOUNT,
    CODE_CONSECUTIVE_WITHDRAWALS,
    CODE_CONSECUTIVE_INCREASING_DEPOSITS,
    CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD,
    EXCESSIVE_WITHDRAWAL_AMOUNT,
    CONSECUTIVE_WITHDRAWALS,
    CONSECUTIVE_INCREASING_DEPOSITS,
    EXCESSIVE_DEPOSIT_AMOUNT,
    EXCESSIVE_DEPOSIT_PERIOD_SECONDS,
    EVENT_TYPE_LITERAL,
)

from flask import (
    Flask,
    request,
)
from pydantic import (
    BaseModel,
    model_validator,
    PositiveInt,
    ValidationError,
)
from werkzeug.exceptions import BadRequest, HTTPException


class EventRequest(BaseModel):
    """Pydantic model used in `/event` request validation.

    :raises: pydantic.ValidationError.
    """
    amount: str
    t: PositiveInt
    type: EVENT_TYPE_LITERAL
    user_id: PositiveInt

    @model_validator(mode="after")
    def check_positivefloat_in_str(self):
        # Haven't found a clean way to do something like:
        # `amount: str[PositiveFloat]` in above pydantic BaseModel
        # validation.
        a = self.amount
        if float(a) < 0:
            raise ValueError("amount needs to be a positive float in a str type!")
        return self


class EventStore:
    def __init__(self):
        self.db = []

    def reset(self):
        self.db = []

    def add_event(self, event: dict) -> None:
        self.db.append(event)

    def has_consecutive_withdrawals(self, user_id: int) -> bool:
        # TODO: Refactor reduce the number of passes to get the list
        # of <CONSECUTIVE_WITHDRAWALS> to focus on!
        user_recs = [x for x in self.db if x["user_id"] == user_id]
        withdrawal_recs = [x for x in user_recs if x["type"] == "withdrawal"]
        last_recs = withdrawal_recs[-CONSECUTIVE_WITHDRAWALS:]
        return bool(len(last_recs) >= CONSECUTIVE_WITHDRAWALS)

    def has_consecutive_increasing_deposits(self, user_id: int) -> bool:
        # TODO: Refactor reduce the number of passes to get the list
        # of <CONSECUTIVE_INCREASING_DEPOSITS> to focus on!
        user_recs = [x for x in self.db if x["user_id"] == user_id]
        # Filter out withdrawal's.
        deposit_recs = [x for x in user_recs if x["type"] == "deposit"]
        last_recs = deposit_recs[-CONSECUTIVE_INCREASING_DEPOSITS:]
        if len(last_recs) < CONSECUTIVE_INCREASING_DEPOSITS:
            return False

        # Check consecutive deposits are increasing.
        amount = 0.0
        for rec in last_recs:
            current_amount = float(rec["amount"])
            if current_amount <= amount:
                return False
            amount = current_amount
        return True

    def has_excessive_deposit_amount_in_period(self, user_id: int) -> bool:
        last_t = self.db[-1]["t"]
        first_t = 0
        if last_t - EXCESSIVE_DEPOSIT_PERIOD_SECONDS > 0:
            first_t = last_t - EXCESSIVE_DEPOSIT_PERIOD_SECONDS
        # TODO: Refactor reduce the number of passes to get the list
        # of <CONSECUTIVE_INCREASING_DEPOSITS> to focus on!
        user_recs = [x for x in self.db if x["user_id"] == user_id]
        # Filter out withdrawal's.
        deposit_recs = [x for x in user_recs if x["type"] == "deposit" and x["t"] >= first_t]
        total_deposit = sum(float(x["amount"]) for x in deposit_recs)
        print(total_deposit)
        return bool(total_deposit > EXCESSIVE_DEPOSIT_AMOUNT)


def create_app(event_store: EventStore):

    app = Flask(__name__)

    LAST_T = 0

    @app.errorhandler(ValidationError)
    def handle_validation_errors(e):
        if isinstance(e, HTTPException):
            return e
        errors = e.errors()
        for error in errors:
            if "ctx" in error:
                # Pop non-json serialisable key/value pair.
                # Message is duplicated in "msg" value.
                error.pop("ctx")
        return errors, BadRequest.code

    @app.post("/event")
    def event():
        req = request.get_json()
        # Validate request body.
        EventRequest(**req)

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
        if _has_excessive_withdrawal_amount(req):
            alert_codes.append(CODE_EXCESSIVE_WITHDRAWAL_AMOUNT)

        ## Stateful validation checks:
        if event_store.has_consecutive_withdrawals(req["user_id"]):
            alert_codes.append(CODE_CONSECUTIVE_WITHDRAWALS)

        if event_store.has_consecutive_increasing_deposits(req["user_id"]):
            alert_codes.append(CODE_CONSECUTIVE_INCREASING_DEPOSITS)

        if event_store.has_excessive_deposit_amount_in_period(req["user_id"]):
            alert_codes.append(CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD)

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



def _has_excessive_withdrawal_amount(req: request) -> bool:
    if req["type"] != "withdrawal":
        return False
    # Validate excessive withdrawal amount:
    _amount = float(req["amount"])
    return _amount > EXCESSIVE_WITHDRAWAL_AMOUNT
