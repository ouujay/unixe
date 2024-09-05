from django.utils import timezone
from datetime import timedelta
from .models import Hashtag, Meep
from django.utils import timezone
from datetime import timedelta
from .models import Meep, Hashtag

def calculate_meep_relevance(meep, user, trending_hashtags):
    score = 0
    
    # 1. Prioritize Meeps from followed users
    if user.profile.follows.filter(user=meep.user).exists():
        score += 10  # Score for followed user

    # 2. Prioritize Meeps with trending hashtags
    if meep.hashtags.filter(id__in=trending_hashtags).exists():
        score += 5  # Score for trending hashtags

    # 3. Prioritize Meeps with high engagement (likes + replies)
    score += meep.likes.count() * 2  # Score for each like
    score += meep.replies.count() * 2  # Score for each reply

    # 4. Time decay factor (reduce score for older Meeps)
    time_diff = timezone.now() - meep.created_at
    if time_diff < timedelta(hours=1):
        score += 10  # High relevance for Meeps within the last hour
    elif time_diff < timedelta(days=1):
        score += 5  # Moderate relevance for Meeps within the last day
    elif time_diff < timedelta(weeks=1):
        score += 2  # Lower relevance for Meeps within the last week

    # 5. Prioritize Meeps from users with high past engagement with the current user
    # Checking if the current user has liked or replied to this user's Meeps
    if meep.user.meep_likes.filter(id=user.id).exists() or Meep.objects.filter(reply_to__user=user, user=meep.user).exists():
        score += 8  # Score for high engagement history with the user

    # 6. Longer Meeps may have more detailed content
    if len(meep.body) > 100:  # Example threshold for content length
        score += 3  # Score for longer content

    # 7. Prioritize Meeps with hashtags the user has interacted with in the past
    interacted_hashtags = Hashtag.objects.filter(meeps__likes=user).distinct()
    if meep.hashtags.filter(id__in=interacted_hashtags).exists():
        score += 5  # Score for personal hashtag interactions

    # 8. Meep's user has high reputation (e.g., many followers)
    if meep.user.profile.followers.count() > 100:
        score += 4  # Score for high-reputation users

    # 9. Meep's content is similar to user's past interactions
    # (e.g., using natural language processing techniques)
    # score += calculate_content_similarity(meep.body, user)  # Example

    return score
# your_app/utils.py

from django.utils import timezone
from datetime import timedelta
from .models import Hashtag, Meep

def calculate_trending_hashtags():
    # Get all Meeps created in the last 24 hours
    last_24_hours = timezone.now() - timedelta(hours=24)
    meeps_last_24_hours = Meep.objects.filter(created_at__gte=last_24_hours)

    # Count the occurrences of each hashtag
    hashtag_counts = {}
    for meep in meeps_last_24_hours:
        hashtags = meep.hashtags.all()
        for hashtag in hashtags:
            if hashtag.name in hashtag_counts:
                hashtag_counts[hashtag.name] += 1
            else:
                hashtag_counts[hashtag.name] = 1

    # Set trending hashtags based on a threshold (e.g., 5 posts in 24 hours)
    trending_threshold = 5
    for hashtag in Hashtag.objects.all():
        if hashtag.name in hashtag_counts and hashtag_counts[hashtag.name] >= trending_threshold:
            hashtag.trending = True
        else:
            hashtag.trending = False
        hashtag.save()
