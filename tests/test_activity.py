from src.unusual_activity.activity import (
    # Validate payload:
    is_user_id_unique,
    is_type_expected,
    is_time_unique,
    # Manipulating payload:
    _convert_str_to_float,
    # Business Logic Validation:
    get_alert_state,
    is_withdrawl_ammount_excessive,
    is_consecutive_withdrawls,
    is_consecutive_increasing_deposits,
    is_excessive_deposit_ammount_in_period,
)


class TestPayload:
    def test_is_user_id_unique(self):
        pass

    def test_is_type_expected(self):
        pass

    def test_is_time_unique(self):
        pass


class TestPayloadParser:
    def test__convert_str_to_float(self):
        pass


class TestActivityBusinessLogic:
    def test_get_alert_state(self):
        pass

    def test_is_withdrawl_ammount_excessive(self):
        pass

    def test_is_consecutive_withdrawls(self):
        pass

    def test_is_consecutive_increasing_deposits(self):
        pass

    def test_is_excessive_deposit_ammount_in_period(self):
        pass

