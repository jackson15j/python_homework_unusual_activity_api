import json

from flask import (
    Flask,
    request,
)

from src.unusual_activity.constants import (
    CODE_EXCESSIVE_WITHDRAWL_AMOUNT,
    EXCESSIVE_WITHDRAWL_AMOUNT,
)

app = Flask(__name__)

LAST_T = 0
DB = {}


@app.post("/event")
def event():
    req = request.get_json()
    alert_codes = []

    # # Validate body. Return 400 on missing required key from body.
    amount = req["amount"]
    # if amount is None:
    #     abort(400)
    # t = request.form.get("t")
    # if t is None:
    #     abort(400)
    # _type = request.form.get("type")
    # if _type is None:
    #     abort(400)
    # user_id = request.form.get("user_id")
    # if user_id is None:
    #     abort(400)

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



def _has_excessive_withdrawl_amount(amount: str) -> bool:
    # Validate excessive withdrawl amount:
    _amount = float(amount)
    return _amount > EXCESSIVE_WITHDRAWL_AMOUNT
