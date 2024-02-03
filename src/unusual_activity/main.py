import json
from flask import Flask

app = Flask(__name__)

LAST_T = 0
DB = {}


@app.post("/event")
def event():
    # Validate body. Return 400 on missing required key from body.
    amount = request.form.get("amount")
    if amount is None:
        abort(400)
    t = request.form.get("t")
    if t is None:
        abort(400)
    _type = request.form.get("type")
    if _type is None:
        abort(400)
    user_id = request.form.get("user_id")
    if user_id is None:
        abort(400)

    # Validate `t` is increasing between requests.
    _t = int(t)
    global LAST_T  # TODO: move away from `global` for global tracking!
    if _t <= LAST_T:
        # t needs to increase each request!
        abort(400)
    LAST_T = _t


    # TODO: Parse JSON body.
    # TODO: Minor: Return 201 on POST success.
    # TODO: Business Logic validation.
    # TODO: Generate Response.
    _hardcoded_data = {
        "alert": True,
        "alert_codes": [
            30,
            123
        ],
        "user_id": 1
    }
    return json.dumps(_hardcoded_data)
