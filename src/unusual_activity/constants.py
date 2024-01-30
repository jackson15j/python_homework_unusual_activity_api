
from enum import Enum


class ActivityType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


# Codes:
CODE_EXCESSIVE_WITHDRAWL_AMMOUNT = 1100
CODE_CONSECUTIVE_WITHDRAWLS = 30
CODE_CONSECUTIVE_INCREASING_DEPOSITS = 300
CODE_EXCESSIVE_DEPOSIT_AMMOUNT_IN_PERIOD = 123

# Code Expectations:
EXCESSIVE_WITHDRAWL_AMMOUNT = 100
CONSECUTIVE_WITHDRAWLS = 3
CONSECUTIVE_INCREASING_DEPOSITS = 3
EXCESSIVE_DEPOSIT_AMMOUNT = 200
EXCESSIVE_DEPOSIT_PERIOD_SECONDS = 30
