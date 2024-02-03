import json
from flask import Flask

app = Flask(__name__)

LAST_T = 0
DB = {}


@app.post("/event")
def event():
    # Validate `t` is increasing between requests.
    t = request.form.get("t")
    if t is None:
        # Missing required key in POST body!
        abort(400)
    _t = int(t)
    global LAST_T  # TODO: move away from `global` for global tracking!
    if _t <= LAST_T:
        # t needs to increase each request!
        abort(400)
    LAST_T = _t


    # TODO: Parse JSON body.
    # TODO: Validate body. Return 400 on invalid body.
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
