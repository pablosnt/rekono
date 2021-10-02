from authorization.groups.roles import DEFAULT_GROUPS


def initialize_user_groups(sender, **kwargs):
    apps = kwargs.get('apps')
    GroupModel = apps.get_model('auth', 'group')
    PermissionModel = apps.get_model('auth', 'permission')
    for group_name in DEFAULT_GROUPS:
        group, created = GroupModel.objects.get_or_create(name=group_name.name.capitalize())
        if not created:
            continue
        permission_set = []
        for permission_name in DEFAULT_GROUPS[group_name]:
            permission = PermissionModel.objects.get(codename=permission_name)
            permission_set.append(permission)
        group.permissions.set(permission_set)
        group.save()
