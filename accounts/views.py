from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetConfirmView,
    PasswordResetDoneView, PasswordResetCompleteView,
)
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import (
    LoginForm, UserCreateForm, UserEditForm, ProfileForm,
    StyledPasswordChangeForm, StyledSetPasswordForm,
)
from .models import User, AuditLog, log_action
from .permissions import admin_required, staff_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Ce compte est désactivé. Contactez l'administrateur.")
            else:
                login(request, user)
                log_action(request, "LOGIN", f"Connexion de {user.username}")
                messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
                return redirect(request.GET.get("next") or "dashboard:home")
        else:
            username = request.POST.get("username", "")
            log_action(request, "LOGIN_FAILED", f"Échec de connexion pour '{username}'")
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    log_action(request, "LOGOUT", f"Déconnexion de {request.user.username}")
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("accounts:login")


# --- Profile (self) ---
@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", "Modification du profil personnel")
        messages.success(request, "Profil mis à jour.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def password_change_view(request):
    form = StyledPasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        log_action(request, "PASSWORD", "Changement de mot de passe (self)")
        messages.success(request, "Mot de passe modifié avec succès.")
        return redirect("accounts:profile")
    return render(request, "accounts/password_change.html", {"form": form})


# --- User management (admin) ---
@admin_required
def user_list(request):
    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    users = User.objects.all().order_by("username")
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
            | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    if role:
        users = users.filter(role=role)
    paginator = Paginator(users, 15)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "accounts/user_list.html", {
        "page_obj": page, "q": q, "role": role, "roles": User.Role.choices,
    })


@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        log_action(request, "CREATE", f"Création de l'utilisateur {user.username}", user)
        messages.success(request, f"Utilisateur {user.username} créé.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "titre": "Nouvel utilisateur"})


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification de l'utilisateur {user.username}", user)
        messages.success(request, "Utilisateur mis à jour.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {
        "form": form, "titre": f"Modifier {user.username}", "obj": user,
    })


@admin_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("accounts:user_list")
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    etat = "activé" if user.is_active else "désactivé"
    log_action(request, "PERMISSION", f"Compte {user.username} {etat}", user)
    messages.success(request, f"Compte {user.username} {etat}.")
    return redirect("accounts:user_list")


@admin_required
def user_reset_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = StyledSetPasswordForm(user=user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "PASSWORD", f"Réinitialisation du mot de passe de {user.username}", user)
        messages.success(request, f"Mot de passe de {user.username} réinitialisé.")
        return redirect("accounts:user_list")
    return render(request, "accounts/password_set.html", {"form": form, "obj": user})


@staff_required
def audit_log(request):
    q = request.GET.get("q", "").strip()
    action = request.GET.get("action", "")
    logs = AuditLog.objects.select_related("user")
    if q:
        logs = logs.filter(Q(message__icontains=q) | Q(user__username__icontains=q))
    if action:
        logs = logs.filter(action=action)
    paginator = Paginator(logs, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "accounts/audit_log.html", {
        "page_obj": page, "q": q, "action": action, "actions": AuditLog.ACTIONS,
    })


# --- Password reset (email based, uses console backend by default) ---
class AppPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class AppPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class AppPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class AppPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
