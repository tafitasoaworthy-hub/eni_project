"""Role-based access control helpers (sécurisation de l'accès aux fonctionnalités)."""
from functools import wraps
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def _check(user, roles):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.role in roles


def role_required(*roles):
    """View decorator restricting access to the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not _check(request.user, roles):
                raise PermissionDenied("Vous n'avez pas la permission d'accéder à cette page.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# Convenience decorators
def staff_required(view_func):
    """Admin or scolarité only."""
    return role_required("ADMIN", "SCOLARITE")(view_func)


def admin_required(view_func):
    return role_required("ADMIN")(view_func)


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return _check(self.request.user, self.allowed_roles)


class StaffRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("ADMIN", "SCOLARITE")


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("ADMIN",)
