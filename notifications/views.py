from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
    """Users only ever see their own notifications."""
    qs = request.user.notifications.all()
    unread_only = request.GET.get("unread") == "1"
    if unread_only:
        qs = qs.filter(is_read=False)
    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "notifications/notification_list.html", {
        "page_obj": page, "unread_only": unread_only,
    })


@login_required
def mark_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, user=request.user)
    note.is_read = True
    note.save(update_fields=["is_read"])
    return redirect("notifications:list")


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("notifications:list")
