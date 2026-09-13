"""Makes the unread notification count available to every template."""


def notification_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"unread_count": 0, "recent_notifications": []}
    qs = user.notifications.all()
    return {
        "unread_count": qs.filter(is_read=False).count(),
        "recent_notifications": qs[:5],
    }
