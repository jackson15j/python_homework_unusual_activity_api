from src.unusual_activity.constants import (
    ActivityType,
    EXCESSIVE_DEPOSIT_PERIOD_SECONDS
)


# Validate payload:
def is_user_id_unique(user_id: int) -> bool:
    raise NotImplementedError


def is_type_expected(activity_type: str) -> bool:
    return activity_type.lower() in ActivityType


def is_time_unique(t: int) -> bool:
    raise NotImplementedError


# Manipulating payload:
def _convert_str_to_float(text: str) -> float:
    return float(text)



# Business Logic Validation:
def get_alert_state(alert_codes: list[int]) -> bool:
    return True if alert_codes else False


def is_withdrawl_amount_excessive(amount: float) -> bool:
    raise NotImplementedError


def is_consecutive_withdrawls(user_id: int) -> bool:
    raise NotImplementedError


def is_consecutive_increasing_deposits(user_id: int) -> bool:
    raise NotImplementedError


def is_excessive_deposit_amount_in_period(
        user_id: int,
        period_seconds: int = EXCESSIVE_DEPOSIT_PERIOD_SECONDS
) -> bool:
    raise NotImplementedError


# Gluing it all together:
def get_user_data(user_id: int) -> dict:
    # TODO: DB lookup for all entries with `user_id`.
    raise NotImplementedError

def collate_alert_codes(user_data: dict) -> list[int]:
    # TODO: call each validation function.
    raise NotImplementedError
