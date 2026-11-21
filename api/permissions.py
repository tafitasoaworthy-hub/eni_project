from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffMember(BasePermission):
    """Admin ou scolarité (back-office)."""
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_superuser or u.is_staff_member))


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_admin)


class StaffWriteAuthenticatedRead(BasePermission):
    """Lecture pour tout utilisateur connecté, écriture réservée au back-office."""
    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return u.is_superuser or u.is_staff_member


class AdminWriteStaffRead(BasePermission):
    """Lecture back-office, écriture réservée aux administrateurs."""
    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return u.is_superuser or u.is_staff_member
        return u.is_superuser or u.is_admin
