from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Max
from django.http import JsonResponse, HttpResponse
from .models import Profile, Meep, Comment, Notification, Hashtag, Message
from .forms import MeepForm, SignUpForm, ProfilePicForm, CommentForm
from .utils import calculate_meep_relevance, calculate_trending_hashtags
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Advertisement
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import Meep, Hashtag, Advertisement
import random

def home(request):
    # Calculate trending hashtags
    calculate_trending_hashtags()

    # Fetch trending hashtags
    trending_hashtags = Hashtag.objects.filter(trending=True).order_by('-name')[:10]  # Display top 10 trending hashtags
    page = request.GET.get('page', 1)

    if request.user.is_authenticated:
        meep_form = MeepForm(request.POST or None, request.FILES or None)
        
        if request.method == "POST" and meep_form.is_valid():
            meep = meep_form.save(commit=False)
            meep.user = request.user
            meep.save()

            # Handle AJAX request for meep submission
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': meep.user.username,
                    'body': meep.body,
                    'created_at': meep.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })

            messages.success(request, "Your Meep Has Been Posted!")
            return redirect('home')

    # Fetch Meeps
    meeps = Meep.objects.all().order_by('-created_at')
    paginator = Paginator(meeps, 10)  # 10 meeps per page
    meeps_page = paginator.get_page(page)

    # Fetch a random advertisement
    ads = Advertisement.objects.all()
    ad = random.choice(ads) if ads.exists() else None

    # Handle infinite scrolling (AJAX request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if not meeps_page.has_next():  # If there are no more pages
            return HttpResponse('')

        # Render meep cards for the current page
        html = ''.join([render_to_string('_meep_card.html', {'meep': meep}) for meep in meeps_page])
        return HttpResponse(html)

    context = {
        "meeps": meeps_page,
        "meep_form": meep_form if request.user.is_authenticated else None,
        "trending_hashtags": trending_hashtags,
        "ad": ad,  # Add the ad to the context
    }

    return render(request, 'home.html', context)

# Like a Meep
@login_required
def meep_like(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    
    if meep.likes.filter(id=request.user.id).exists():
        meep.likes.remove(request.user)
        liked = False
    else:
        meep.likes.add(request.user)
        liked = True
        Notification.objects.create(
            user=meep.user,
            message=f"{request.user.username} liked your Meep.",
            meep=meep
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "new_like_count": meep.likes.count(), "liked": liked})
    
    return redirect(request.META.get("HTTP_REFERER"))

# Show a Meep with Replies
def show_meep(request, pk):
    meep = get_object_or_404(Meep, pk=pk)
    order_by = request.GET.get('order_by', 'latest')
    
    if order_by == 'relevance':
        replies = meep.replies.all().annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    else:
        replies = meep.replies.all().order_by('-created_at')

    if request.method == "POST":
        reply_form = MeepForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user
            reply.reply_to = meep
            reply.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'reply': {
                        'user': {'username': reply.user.username},
                        'body': reply.body,
                        'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            messages.success(request, "Your reply has been posted!")
            return redirect('show_meep', pk=meep.pk)
    
    reply_form = MeepForm()
    return render(request, 'show_meep.html', {
        'meep': meep,
        'replies': replies,
        'reply_form': reply_form,
        'order_by': order_by,
    })

# Profile List View
@login_required
def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, 'profile_list.html', {"profiles": profiles})

# Follow/Unfollow Users
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from .models import Profile, Meep

@login_required
def profile(request, pk):
    profile = get_object_or_404(Profile, user_id=pk)
    meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")
    
    # Determine mutual followers
    mutual_followers = []
    if profile.user != request.user:
        mutual_followers = profile.followed_by.filter(user__in=request.user.profile.follows.all())

    if request.method == "POST":
        action = request.POST.get('follow')
        if action == "unfollow":
            request.user.profile.follows.remove(profile)
        elif action == "follow":
            request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, f"You have successfully {action}ed {profile.user.username}")
    
    return render(request, "profile.html", {
        "profile": profile,
        "meeps": meeps,
        "mutual_followers": mutual_followers,
    })
def follow(request, pk):
    profile_to_follow = get_object_or_404(Profile, pk=pk)
    
    if request.user.profile.follows.filter(pk=pk).exists():
        request.user.profile.follows.remove(profile_to_follow)
        messages.success(request, f'You have unfollowed {profile_to_follow.user.username}')
    else:
        request.user.profile.follows.add(profile_to_follow)
        messages.success(request, f'You are now following {profile_to_follow.user.username}')
    
    return redirect('profile', pk=pk)
@login_required
def unfollow(request, pk):
    profile = get_object_or_404(Profile, user_id=pk)
    request.user.profile.follows.remove(profile)
    request.user.profile.save()
    messages.success(request, f"You have successfully unfollowed {profile.user.username}")
    return redirect(request.META.get("HTTP_REFERER"))

# Profile View
@login_required
def profile(request, pk):
    profile = get_object_or_404(Profile, user_id=pk)
    meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")
    
    if request.method == "POST":
        action = request.POST.get('follow')
        if action == "unfollow":
            request.user.profile.follows.remove(profile)
        elif action == "follow":
            request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, f"You have successfully {action}ed {profile.user.username}")
    
    return render(request, "profile.html", {"profile": profile, "meeps": meeps})

# Followers View
@login_required
def followers(request, pk):
    profiles = Profile.objects.filter(follows__id=pk)
    return render(request, 'followers.html', {"profiles": profiles})

# User Authentication Views
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In! Get MEEPING!")
            return redirect('home')
        else:
            messages.error(request, "There was an error logging in. Please Try Again...")
            return redirect('login')
    return render(request, "login.html")

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out. Sorry to Meep You Go...")
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have successfully registered! Welcome!")
            return redirect('home')
    return render(request, "register.html", {'form': form})

# Update User Profile View
@login_required
def update_user(request):
    current_user = get_object_or_404(User, id=request.user.id)
    profile_user = get_object_or_404(Profile, user__id=request.user.id)
    user_form = SignUpForm(request.POST or None, instance=current_user)
    profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
    
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user = user_form.save(commit=False)
        password = user_form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        user.save()
        profile_form.save()
        login(request, user)
        messages.success(request, "Your Profile Has Been Updated!")
        return redirect('home')
    return render(request, "update_user.html", {'user_form': user_form, 'profile_form': profile_form})

# Delete Meep View
@login_required
def delete_meep(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if request.user == meep.user:
        meep.delete()
        messages.success(request, "The Meep Has Been Deleted!")
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.error(request, "You Don't Own That Meep!!")
        return redirect('home')

# Edit Meep View
@login_required
def edit_meep(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if request.user == meep.user:
        form = MeepForm(request.POST or None, instance=meep)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Your Meep Has Been Updated!")
            return redirect('home')
        return render(request, "edit_meep.html", {'form': form, 'meep': meep})
    else:
        messages.error(request, "You Don't Own That Meep!!")
        return redirect('home')

# Search View
def search(request):
    if request.method == "POST":
        search = request.POST['search']
        searched = Meep.objects.filter(body__icontains=search)
        return render(request, 'search.html', {'search': search, 'searched': searched})
    return render(request, 'search.html')

# Notifications View
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications.update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})

# Reply to Meep View
@login_required
def reply_to_meep(request, pk):
    original_meep = get_object_or_404(Meep, pk=pk)
    if request.method == "POST":
        form = MeepForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.reply_to = original_meep
            reply.save()

            Notification.objects.create(
                user=original_meep.user,
                message=f"{request.user.username} replied to your Meep.",
                meep=original_meep
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'reply': {
                        'user': {'username': reply.user.username},
                        'body': reply.body,
                        'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            messages.success(request, "Your reply has been posted!")
            return redirect('show_meep', pk=original_meep.pk)
    
    form = MeepForm()
    return render(request, 'reply_to_meep.html', {'form': form, 'original_meep': original_meep})

# Show Thread View
@login_required
def show_thread(request, pk):
    meep = get_object_or_404(Meep, pk=pk)
    replies = meep.replies.all().order_by('created_at')
    return render(request, 'show_thread.html', {
        'meep': meep,
        'replies': replies,
    })

# Change Password View
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile', pk=request.user.pk)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

# Trending Topics View
def trending_topics(request):
    trending_hashtags = Hashtag.objects.order_by('-usage_count')[:10]
    return render(request, 'trending_topics.html', {'trending_hashtags': trending_hashtags})

# Hashtag Detail View
def hashtag_detail(request, hashtag_name):
    hashtag = get_object_or_404(Hashtag, name=hashtag_name)
    meeps = Meep.objects.filter(hashtags=hashtag).annotate(like_count=Count('likes')).order_by('-like_count')
    return render(request, 'hashtag_detail.html', {'hashtag': hashtag, 'meeps': meeps})

# Search & Explore View
def search_results(request):
    query = request.GET.get('q', '')
    
    user_results = User.objects.filter(username__icontains=query) if query else None
    meep_results = Meep.objects.filter(body__icontains=query) if query else None
    hashtag_results = Hashtag.objects.filter(name__icontains=query) if query else None

    trending_hashtags = Hashtag.objects.filter(trending=True)

    context = {
        'query': query,
        'user_results': user_results,
        'meep_results': meep_results,
        'hashtag_results': hashtag_results,
        'trending_hashtags': trending_hashtags,
    }

    return render(request, 'search_explore.html', context)
from django.shortcuts import get_object_or_404
from .models import Message, User

@login_required
def conversation_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Fetch all messages in this conversation
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) | 
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('timestamp')

    # Mark all unread messages in this conversation as read
    messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    if request.method == "POST":
        body = request.POST.get('message')
        if body:
            Message.objects.create(sender=request.user, recipient=other_user, body=body)
            return redirect('conversation_view', user_id=user_id)

    return render(request, 'conversation.html', {
        'messages': messages,
        'other_user': other_user,
    })

@login_required
def inbox_view(request):
    query = request.GET.get('q')

    # Fetch conversations and include the unread message count
    conversations = (
        Message.objects
        .filter(Q(sender=request.user) | Q(recipient=request.user))
        .select_related('sender', 'recipient')
        .values('sender', 'recipient')
        .annotate(last_message_time=Max('timestamp'))
        .order_by('-last_message_time')
    )

    conversations_data = []
    participants = set()

    for conversation in conversations:
        other_user_id = conversation['recipient'] if conversation['sender'] == request.user.id else conversation['sender']

        if other_user_id not in participants:
            participants.add(other_user_id)

            unread_count = Message.objects.filter(sender_id=other_user_id, recipient=request.user, is_read=False).count()

            last_message = Message.objects.filter(
                sender_id__in=[request.user.id, other_user_id],
                recipient_id__in=[request.user.id, other_user_id]
            ).order_by('-timestamp').first()

            conversations_data.append({
                'other_user': User.objects.get(id=other_user_id),
                'unread_count': unread_count,
                'last_message': last_message.body if last_message else '',
            })

    # Optional search functionality
    if query:
        conversations_data = [conv for conv in conversations_data if query.lower() in conv['other_user'].username.lower()]

    return render(request, 'inbox.html', {'conversations': conversations_data})

# Send Message View
@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == "POST":
        body = request.POST.get('message')
        if body:
            Message.objects.create(sender=request.user, recipient=recipient, body=body)
            messages.success(request, f"Message sent to {recipient.username}!")
        else:
            messages.error(request, "Message cannot be empty.")
    return redirect('profile', pk=recipient_id)

# Utility View for AJAX Data Fetching Example
def get_data(request):
    return HttpResponse("This is data loaded via AJAX.")

# Post Meep via AJAX
# Post Meep via AJAX
@login_required
def post_meep(request):
    if request.method == "POST":
        form = MeepForm(request.POST, request.FILES)
        if form.is_valid():
            meep = form.save(commit=False)
            meep.user = request.user
            meep.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': request.user.username,
                    'body': meep.body,
                    'created_at': meep.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })

            return redirect('home')  # Fallback for non-AJAX requests
    return redirect('home')

# Live Search View
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Meep, Hashtag

def live_search(request):
    query = request.GET.get('q', '')

    user_results = []
    meep_results = []
    hashtag_results = []

    if query:
        # Search for users
        user_results = list(User.objects.filter(username__icontains=query).values('id', 'username'))

        # Search for meeps
        meep_results = list(Meep.objects.filter(body__icontains=query).values('id', 'body'))

        # Search for hashtags
        hashtag_results = list(Hashtag.objects.filter(name__icontains=query).values('name'))

    return JsonResponse({
        'user_results': user_results,
        'meep_results': meep_results,
        'hashtag_results': hashtag_results,
    })

# Fetch Notifications View
@login_required
def fetch_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    notifications_data = [{
        'message': notification.message,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': notification.is_read,
    } for notification in notifications]

    # Mark notifications as read
    notifications.update(is_read=True)

    return JsonResponse({'notifications': notifications_data})

# Toggle Follow View (for AJAX)
@login_required
def toggle_follow(request, pk):
    profile = Profile.objects.get(user_id=pk)
    if request.user.profile.follows.filter(id=profile.id).exists():
        request.user.profile.follows.remove(profile)
        following = False
    else:
        request.user.profile.follows.add(profile)
        following = True

    return JsonResponse({'success': True, 'following': following})

# Send Message via AJAX
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Message
from django.contrib.auth.models import User

@login_required
def send_message_ajax(request, recipient_id):
    if request.method == "POST":
        recipient = get_object_or_404(User, id=recipient_id)
        message_body = request.POST.get('message')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if message_body or image or video:
            # Save the message
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                body=message_body,
                image=image,
                video=video
            )
            return JsonResponse({
                'success': True,
                'message': {
                    'body': message.body,
                    'image': message.image.url if message.image else None,
                    'video': message.video.url if message.video else None,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })

    return JsonResponse({'success': False}, status=400)

# Fetch New Messages View
@login_required
def fetch_new_messages(request, conversation_with):
    # Fetch the latest messages between the logged-in user and another user
    messages = Message.objects.filter(
        sender_id__in=[request.user.id, conversation_with],
        recipient_id__in=[request.user.id, conversation_with]
    ).order_by('timestamp')

    message_list = [{
        'body': message.body,
        'sender': message.sender.username,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    } for message in messages]

    return JsonResponse({'messages': message_list})
@login_required
def unread_message_count(request):
    unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_message_count': unread_count})
@login_required
def unread_conversation_counts(request):
    conversations = (
        Message.objects
        .filter(Q(sender=request.user) | Q(recipient=request.user))
        .select_related('sender', 'recipient')
        .values('sender', 'recipient')
        .annotate(last_message=Max('timestamp'))
        .order_by('-last_message')
    )

    conversation_data = []
    for conversation in conversations:
        other_user = conversation['recipient'] if conversation['sender'] == request.user.id else conversation['sender']
        unread_count = Message.objects.filter(sender_id=other_user, recipient=request.user, is_read=False).count()

        conversation_data.append({
            'other_user_id': other_user,
            'unread_count': unread_count,
        })

    return JsonResponse({'conversations': conversation_data})
@login_required
def mark_as_read(request, user_id):
    if request.method == "POST":
        other_user = get_object_or_404(User, id=user_id)
        Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, User

@login_required
def followers_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    followers = user.profile.followed_by.all()

    # If viewing someone else's profile, show mutual followers first
    if user != request.user:
        followers = sorted(followers, key=lambda u: request.user in u.profile.followed_by.all(), reverse=True)

    return render(request, 'followers_list.html', {'followers': followers, 'profile_user': user})

@login_required
def following_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Only the profile owner can view the "Following" list
    if user != request.user:
        return render(request, 'error.html', {'message': "You cannot view this user's following list."})
    
    following = user.profile.follows.all()

    return render(request, 'following_list.html', {'following': following, 'profile_user': user})
def track_profile_visit(visitor, profile_owner):
    if visitor != profile_owner.user:
        profile_owner.profile_visits.add(visitor)
        profile_owner.save()
def mute_user(request, user_to_mute):
    request.user.profile.muted_users.add(user_to_mute)
    request.user.profile.save()

def block_user(request, user_to_block):
    request.user.profile.blocked_users.add(user_to_block)
    request.user.profile.save()
# views.py
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

def track_ad_click(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.clicks += 1  # Increment the click count
    ad.save()  # Save the updated ad
    return HttpResponseRedirect(ad.link)  # Redirect to the ad's link
