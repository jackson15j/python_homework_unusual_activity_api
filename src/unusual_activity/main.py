import json
from flask import Flask

app = Flask(__name__)


@app.post("/event")
def event():
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
