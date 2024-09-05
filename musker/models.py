from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import re

from django.db import models
from django.contrib.auth.models import User
import re

# Define the Hashtag model
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    total_meeps = models.IntegerField(default=0)  # Total Meeps ever associated with this hashtag
    trending = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    def __str__(self):
        return self.name

# Define the Meep model
class Meep(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="meep_likes", blank=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="meeps")
    
    # Media fields
    image = models.ImageField(upload_to='meep_images/', null=True, blank=True)
    video = models.FileField(upload_to='meep_videos/', null=True, blank=True)

    def __str__(self):
        return self.body[:50]

    # Extract hashtags from the body of the Meep
    def extract_hashtags(self):
        # Clear old hashtags to avoid duplication
        self.hashtags.clear()
        
        hashtags = re.findall(r"#(\w+)", self.body)
        hashtag_objects = []
        
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag)
            if not created:
                hashtag.usage_count += 1  # Increment count if hashtag already exists
            else:
                hashtag.usage_count = 1  # Set count to 1 if hashtag is newly created
            hashtag.save()
            hashtag_objects.append(hashtag)
        
        self.hashtags.set(hashtag_objects)

# Signal to extract hashtags after saving a Meep
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Meep)
def save_hashtags(sender, instance, **kwargs):
    instance.extract_hashtags()


# Comment model
class Comment(models.Model):
    meep = models.ForeignKey(Meep, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:50]

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")
    profile_bio = models.CharField(null=True, blank=True, max_length=500)
    homepage_link = models.CharField(null=True, blank=True, max_length=100)
    facebook_link = models.CharField(null=True, blank=True, max_length=100)
    instagram_link = models.CharField(null=True, blank=True, max_length=100)
    linkedin_link = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return self.user.username

# Create profile when a new user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        # Have the user follow themselves
        user_profile.follows.set([instance.profile.id])
        user_profile.save()

post_save.connect(create_profile, sender=User)

# Notification model
from django.db import models
from django.contrib.auth.models import User
from .models import Meep

class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Add references to related Meep and User (if applicable)
    meep = models.ForeignKey(Meep, null=True, blank=True, on_delete=models.CASCADE)
    related_user = models.ForeignKey(User, null=True, blank=True, related_name="related_notifications", on_delete=models.CASCADE)

    def __str__(self):
        return self.message
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    image = models.ImageField(upload_to='message_images/', null=True, blank=True)
    video = models.FileField(upload_to='message_videos/', null=True, blank=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} at {self.timestamp}"
from django.db import models
from django.contrib.auth.models import User

class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # e.g., 'login', 'post_meep'
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.action} at {self.timestamp}'
# models.py
from django.db import models

class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/')
    link = models.URLField()  # The URL the ad will redirect to
    clicks = models.PositiveIntegerField(default=0)  # Track the number of clicks
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
