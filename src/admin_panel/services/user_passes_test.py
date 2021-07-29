# region ACCESS


def check_access(user, access_type):
    if not user.is_authenticated:
        return False
    else:
        pass1, pass2, pass3 = False, False, False
        pass1 = user.is_superuser

        if user.role is not None:
            access_check = getattr(user.role, access_type)
            pass2 = user.role.name == "Директор"
            pass3 = access_check

        return any([pass1, pass2, pass3])


def statistics_access(user):
    return check_access(user, "statistics_access")


def cashbox_access(user):
    return check_access(user, "cashbox_access")


def receipt_access(user):
    return check_access(user, "receipt_access")


def account_access(user):
    return check_access(user, "account_access")


def flat_access(user):
    return check_access(user, "flat_access")


def house_user_access(user):
    return check_access(user, "house_user_access")


def house_access(user):
    return check_access(user, "house_access")


def message_access(user):
    return check_access(user, "message_access")


def call_request_access(user):
    return check_access(user, "call_request_access")


def meter_data_access(user):
    return check_access(user, "meter_data_access")


def site_access(user):
    return check_access(user, "site_access")


def service_access(user):
    return check_access(user, "service_access")


def tariff_access(user):
    return check_access(user, "tariff_access")


def role_access(user):
    return check_access(user, "role_access")


def staff_access(user):
    return check_access(user, "staff_access")


def payments_detail_access(user):
    return check_access(user, "payments_detail_access")


# endregion ACCESS
