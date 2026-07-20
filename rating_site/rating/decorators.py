from functools import wraps

from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, 'is_admin', False):
            raise PermissionDenied(
                'У вас нет доступа к этой странице'
            )
        return view_func(request, *args, **kwargs)
    return wrapper