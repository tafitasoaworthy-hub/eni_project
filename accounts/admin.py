from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AuditLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "email", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Profil université", {"fields": ("role", "phone", "photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profil université", {"fields": ("role", "phone")}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "message")
    list_filter = ("action",)
    search_fields = ("message", "user__username")
    readonly_fields = ("created_at",)
