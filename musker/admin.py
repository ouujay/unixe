from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Meep, Hashtag, Notification, Message, UserActivityLog

# Unregister Groups
admin.site.unregister(Group)

# Mix Profile info into User info
class ProfileInline(admin.StackedInline):
    model = Profile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    # Just display username fields on admin page
    fields = ["username"]
    inlines = [ProfileInline]

# Unregister initial User
admin.site.unregister(User)

# Reregister User with extended Profile
admin.site.register(User, UserAdmin)

# Register remaining models
admin.site.register(Profile)
admin.site.register(Meep)
admin.site.register(Hashtag)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(UserActivityLog)


# admin.py
from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'clicks', 'created_at')
