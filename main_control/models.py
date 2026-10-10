from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(max_length=20, blank=True, default='')  # 'female', 'male', 'other'
    birth_date = models.DateField(null=True, blank=True)
    birth_time = models.TimeField(null=True, blank=True)
    unknown_birth_time = models.BooleanField(default=False)
    birth_place = models.CharField(max_length=150, blank=True, default='')
    agreed_terms = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    oauth_provider = models.CharField(max_length=30, blank=True, default='')  # 'google' or 'local'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class UserInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='saved_fortunes')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    birth_date = models.DateField()
    birth_time = models.TimeField(null=True, blank=True)
    unknown_birth_time = models.BooleanField(default=False)
    birth_place = models.CharField(max_length=150, blank=True, default='')
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)