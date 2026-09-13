"""Authentication, profile, user management and error views."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required
from .forms import LoginForm, ProfileForm, UserForm
from .models import AuditLog, log_action

User = get_user_model()


def login_view(request):
    """Log a user in and send them to their role dashboard."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        log_action(user, "USER_LOGIN", resource=f"User {user.username}", ip_address=request.META.get("REMOTE_ADDR", ""))
        messages.success(request, f"Welcome back, {request.user.full_name}!")
        return redirect(request.GET.get("next") or "dashboard:home")
    if request.method == "POST":
        messages.error(request, "Invalid credentials. Please try again.")
    return render(request, "accounts/login.html", {"form": form})



def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def profile_view(request):
    """View / edit own account details."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@admin_required
def user_list(request):
    """Admin: list, search and filter all system users."""
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    users = User.objects.all()
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
    if role:
        users = users.filter(role=role)

    page = Paginator(users, 10).get_page(request.GET.get("page"))
    return render(request, "accounts/user_list.html", {
        "page_obj": page, "query": query, "role": role,
        "roles": User.ROLE_CHOICES,
    })


@admin_required
def user_add(request):
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"User '{user.username}' created.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "Add User"})


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "User updated.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {
        "form": form, "title": f"Edit User - {user.username}",
    })


@admin_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(
            request,
            f"User '{user.username}' is now {'active' if user.is_active else 'inactive'}.",
        )
    return redirect("accounts:user_list")


@admin_required
def audit_log_list(request):
    """Admin: Audit Trail dashboard to review all PHI access & system security logs."""
    query = request.GET.get("q", "").strip()
    logs = AuditLog.objects.select_related("user")
    if query:
        logs = logs.filter(
            Q(action__icontains=query)
            | Q(resource__icontains=query)
            | Q(user__username__icontains=query)
            | Q(details__icontains=query)
        )
    page = Paginator(logs, 20).get_page(request.GET.get("page"))
    return render(request, "accounts/audit_log.html", {
        "page_obj": page, "query": query,
    })


# ---------------------------------------------------------------------------
# Error pages
# ---------------------------------------------------------------------------

def error_403(request, exception=None):
    return render(request, "403.html", status=403)


def error_404(request, exception=None):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)
