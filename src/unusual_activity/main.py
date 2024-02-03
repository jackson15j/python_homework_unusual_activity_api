"""Entrypoint into the Unusual Activity Application.

Exposes an `/event` endpoint that can be sent deposit/withdrawal events
to. See: `README.org` for the requirements around validation.
"""
import json

from src.unusual_activity.constants import (
    CODE_CONSECUTIVE_INCREASING_DEPOSITS,
    CODE_CONSECUTIVE_WITHDRAWALS,
    CODE_EXCESSIVE_DEPOSIT_AMOUNT_IN_PERIOD,
    CODE_EXCESSIVE_WITHDRAWAL_AMOUNT,
    CONSECUTIVE_WITHDRAWALS,
    CONSECUTIVE_INCREASING_DEPOSITS,
    EVENT_TYPE_LITERAL,
    EXCESSIVE_DEPOSIT_AMOUNT,
    EXCESSIVE_DEPOSIT_PERIOD_SECONDS,
    EXCESSIVE_WITHDRAWAL_AMOUNT,
)

from flask import (
    Flask,
    request,
)
from pydantic import (
    BaseModel,
    model_validator,
    NonNegativeInt,
    PositiveInt,
    ValidationError,
)
from werkzeug.exceptions import (
    BadRequest,
    HTTPException,
)


class EventRequest(BaseModel):
    """Pydantic model used in `/event` request validation.

    :raises: pydantic.ValidationError.
    """
    amount: str
    t: NonNegativeInt
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
    """In-memory store of events + boolean functions for each of the
    required stateful validations.

    TODO: FUTURE REFACTORING

    - Move Class out to it's own file
      (eg. `event_store/in_memory.py::InMemory`).
    - Create interface class with abstract methods
      (eg. `event_store/ievent_store.py::IEventStore`)
    - Update the EventStore to inherit the interface.
    - Move test logic into a base class and use inheritance to avoid
      duplication when testing each EventStore implementation.
      (eg. `TestInMemory(BaseEventStore)`).
    - Create a DB-backed EventStore
      (eg. `event_store/sqlite.py::Sqlite`).
    """
    def __init__(self):
        self.db = []

    def add_event(self, event: dict) -> None:
        """Store Event."""
        self.db.append(event)

    def has_consecutive_withdrawals(self, user_id: int) -> bool:
        """Returns True if consecutive withdrawals threshold is met."""
        # TODO: Refactor reduce the number of passes to get the list
        # of <CONSECUTIVE_WITHDRAWALS> to focus on!
        user_recs = [x for x in self.db if x["user_id"] == user_id]
        withdrawal_recs = [x for x in user_recs if x["type"] == "withdrawal"]
        last_recs = withdrawal_recs[-CONSECUTIVE_WITHDRAWALS:]
        return bool(len(last_recs) >= CONSECUTIVE_WITHDRAWALS)

    def has_consecutive_increasing_deposits(self, user_id: int) -> bool:
        """Returns True if consecutive increasing deposits threshold is
        met, ignoring withdrawals.
        """
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
        """Returns True if excessive deposit amount threshold, during
        period, is met.
        """
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
        return bool(total_deposit > EXCESSIVE_DEPOSIT_AMOUNT)


def create_app(event_store: EventStore) -> Flask:
    """Create Flask application with the passed in EventStore.

    :param EventStore event_store: Data store of events to add to and
        query.
    :returns: flask.Flask() app instance.
    """

    app = Flask(__name__)

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
        # Store state.
        event_store.add_event(req)

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

        ## Response Generation:
        ret_val = {
            "alert": bool(alert_codes),
            "alert_codes": alert_codes,
            "user_id": req["user_id"]
        }
        # TODO: Minor: Return 201 on POST success.
        return json.dumps(ret_val)

    return app



def _has_excessive_withdrawal_amount(req: request) -> bool:
    """Stateless check to validate if the withdrawal amount has been
    exceeded.

    :param request req: Flask `/event` request to inspect.
    :returns bool. True if Withdrawal amount has been exceeded.
    """
    if req["type"] != "withdrawal":
        return False
    # Validate excessive withdrawal amount:
    _amount = float(req["amount"])
    return _amount > EXCESSIVE_WITHDRAWAL_AMOUNT
