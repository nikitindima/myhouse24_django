from src.users.models import UserRole


def get_or_create_user_roles():
    qs = UserRole.objects.all()
    if not qs.exists():
        role_list = ["Директор", "Управляющий", "Бухгалтер", "Электрик", "Сантехник"]
        for role in role_list:
            new_role = UserRole(name=role)

            new_role.statistics_access = True
            new_role.cashbox_access = True
            new_role.receipt_access = True
            new_role.account_access = True
            new_role.flat_access = True
            new_role.house_user_access = True
            new_role.house_access = True
            new_role.message_access = True
            new_role.call_request_access = True
            new_role.meter_data_access = True
            new_role.site_access = True
            new_role.service_access = True
            new_role.tariff_access = True
            new_role.role_access = True
            new_role.staff_access = True
            new_role.payments_detail_access = True

            new_role.save()
        qs = UserRole.objects.all()
    return qs
