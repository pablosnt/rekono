from security.authorization.roles import DEFAULT_GROUPS


def initialize_user_groups(sender, **kwargs):
    apps = kwargs.get('apps')
    group_model = apps.get_model('auth', 'group')
    permission_model = apps.get_model('auth', 'permission')
    for group_name in DEFAULT_GROUPS:
        group, created = group_model.objects.get_or_create(name=group_name.name.capitalize())
        if not created:
            continue
        permission_set = []
        for permission_name in DEFAULT_GROUPS[group_name]:
            permission = permission_model.objects.get(codename=permission_name)
            permission_set.append(permission)
        group.permissions.set(permission_set)
        group.save()
