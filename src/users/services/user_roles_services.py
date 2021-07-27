from src.users.models import UserRole


def get_or_create_user_roles():
    qs = UserRole.objects.all()
    if not qs.exists():
        role_list = ['Директор', 'Управляющий', 'Бухгалтер', 'Электрик', 'Сантехник']
        for role in role_list:
            UserRole(name=role).save()
        qs = UserRole.objects.all()
    return qs
