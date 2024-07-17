from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import FriendList, FriendRequest
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import CreateUserForm, ProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
# Create your views here.

@login_required(login_url='login')
def index(request):
    return render(request, 'profileapp/home.html')

@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if 'save_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                username = request.user.username
                messages.success(request, f'{username}, Your profile is updated.')
                return redirect('home')  # Redirige vers la page d'accueil après la mise à jour du profil

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important, pour garder l'utilisateur connecté après le changement de mot de passe
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')  # Redirige vers la page de profil après la mise à jour du mot de passe
            else:
                messages.error(request, 'Please correct the error below.')

    else:
        profile_form = ProfileForm(instance=request.user.profile, user=request.user)
        password_form = PasswordChangeForm(user=request.user)

    # Ajouter la liste des utilisateurs et des demandes d'ami
    users = User.objects.exclude(id=request.user.id)
    friend_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True)

    context = {
        'form': profile_form,
        'password_form': password_form,
        'users': users,
        'friend_requests': friend_requests,
    }
    return render(request, 'profileapp/profile.html', context)
# def profile(request):
#     if request.method == 'POST':
#         profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
#         password_form = PasswordChangeForm(user=request.user, data=request.POST)
        
#         if 'save_profile' in request.POST:
#             if profile_form.is_valid():
#                 profile_form.save()
#                 username = request.user.username
#                 messages.success(request, f'{username}, Your profile is updated.')
#                 return redirect('home')  # Redirige vers la page d'accueil après la mise à jour du profil

#         elif 'change_password' in request.POST:
#             if password_form.is_valid():
#                 user = password_form.save()
#                 update_session_auth_hash(request, user)  # Important, pour garder l'utilisateur connecté après le changement de mot de passe
#                 messages.success(request, 'Your password was successfully updated!')
#                 return redirect('profile')  # Redirige vers la page de profil après la mise à jour du mot de passe
#             else:
#                 messages.error(request, 'Please correct the error below.')

#     else:
#         profile_form = ProfileForm(instance=request.user.profile, user=request.user)
#         password_form = PasswordChangeForm(user=request.user)

#     context = {'form': profile_form, 'password_form': password_form}
#     return render(request, 'profileapp/profile.html', context)

@unauthenticated_user
def login_user(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f'{username}, You are logged in.')
            return redirect("/")
        else:
            messages.info(request, 'Wrong passwrod or username')
            return redirect('login')
    return render(request, 'profileapp/login_page.html')

@unauthenticated_user
def register_user(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Account is created.')
            return redirect('login')
        else:
            context = {'form': form}
            messages.info(request, 'Invalid credentials')
            return render(request, 'profileapp/register_page.html', context)

    context = {'form': form}
    return render(request, 'profileapp/register_page.html', context)

@login_required(login_url='login')
def logout_user(request):
    logout(request)
    messages.info(request, 'You logged out successfully')
    return redirect('login')

@login_required
def send_friend_request(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    if request.method == 'POST':
        if receiver != request.user:  # Assurez-vous que l'utilisateur ne peut pas s'envoyer une demande à lui-même
            # Vérifiez si une demande similaire existe déjà
            existing_request = FriendRequest.objects.filter(sender=request.user, receiver=receiver, is_active=True).first()
            if not existing_request:
                # Créer une nouvelle demande d'ami avec is_active=True
                FriendRequest.objects.create(sender=request.user, receiver=receiver, is_active=True)
                messages.success(request, f"Friend request sent to {receiver.username}.")
            else:
                messages.warning(request, f"You have already sent a friend request to {receiver.username}.")
        else:
            messages.error(request, "You cannot send a friend request to yourself.")

    return redirect(reverse('profile'))  # Redirigez vers la page de profil après avoir envoyé la demande d'ami

@login_required
# def accept_friend_request(request, request_id):
#     friend_request = get_object_or_404(FriendRequest, id=request_id)

#     # Vérifie si l'utilisateur connecté est le destinataire de la demande d'ami
#     if friend_request.receiver == request.user:
#         friend_request.accept()
#         messages.success(request, 'Friend request accepted.')
#     else:
#         messages.error(request, 'You cannot accept this friend request.')

#     # Redirige vers le profil de l'utilisateur qui a envoyé la demande d'ami
#     return redirect('profile', user_id=friend_request.sender.id)
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.receiver == request.user:
        friend_request.accept()
        messages.success(request, f'You have accepted the friend request from {friend_request.sender.username}')
    return redirect('profile')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.receiver == request.user:
        friend_request.decline()
        messages.success(request, f'You have declined the friend request from {friend_request.sender.username}')
    return redirect('profile')