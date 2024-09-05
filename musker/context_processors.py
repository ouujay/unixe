# musker/context_processors.py

from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_notifications_count = 0
    return {'unread_notifications_count': unread_notifications_count}

from .models import Message

def unread_message_count(request):
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {'unread_message_count': unread_count}
