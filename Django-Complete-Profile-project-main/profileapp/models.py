from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)

    name = models.CharField(default = 'John Doe (Default)', max_length=200, null=True)

    title = models.CharField(default = 'This is the default, title change it in profile.', max_length=200, null=True)

    desc_text = 'Hey, there this is a default text description about you that you can change on after clicking on "Edit" or going to your profile page.'

    desc = models.CharField(default = desc_text, max_length=200, null=True)

    profile_img =  models.ImageField(default = 'media/default.jpg', upload_to = 'media', null = True, blank = True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends")

    def __str__(self):
        return f"Friend list of {self.user.username}"

    def add_friend(self, friend):
        if not self.friends.filter(pk=friend.pk).exists():  # Vérifie si l'ami n'est pas déjà dans la liste
            self.friends.add(friend)
            self.save()

    def remove_friend(self, friend):
        if self.friends.filter(pk=friend.pk).exists():
            self.friends.remove(friend)
            self.save()

    def is_friend(self, friend):
        return self.friends.filter(pk=friend.pk).exists()

    def unfriend(self, friend):
        self.remove_friend(friend)
        friend.friend_list.remove_friend(self.user)  # Supprime également de l'autre côté


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

    def accept(self):
        if not self.is_active:
            return

        self.is_active = False
        self.save()

        try:
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if not sender_friend_list.is_friend(self.receiver):
                sender_friend_list.add_friend(self.receiver)
        except ObjectDoesNotExist:
            sender_friend_list = FriendList.objects.create(user=self.sender)
            sender_friend_list.add_friend(self.receiver)

        try:
            receiver_friend_list = FriendList.objects.get(user=self.receiver)
            if not receiver_friend_list.is_friend(self.sender):
                receiver_friend_list.add_friend(self.sender)
        except ObjectDoesNotExist:
            receiver_friend_list = FriendList.objects.create(user=self.receiver)
            receiver_friend_list.add_friend(self.sender)