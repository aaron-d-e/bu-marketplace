from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import storages


def get_profile_storage():
    """Return the profile_images storage backend."""
    return storages["profile_images"]

class Product(models.Model):
    # many products connected to one user
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True)
    category = models.ForeignKey('Category', null=True, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    image = models.ImageField(null=True)
    sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.name

# enum for product condition
class ProductCondition(models.TextChoices):
    NEW = 'new'
    USED = 'used'
    LIKE_NEW = 'like new'
    GOOD = 'good'
    FAIR = 'fair'
    POOR = 'poor'

class Inquiry(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    make = models.CharField(max_length=100, null=False)
    model = models.CharField(max_length=100, null=False)
    years_of_use = models.IntegerField(null=True)
    category = models.ForeignKey('Category', null=True, on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=ProductCondition.choices, default=ProductCondition.GOOD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class UserProfile(models.Model):

    """Extended user profile with profile picture support."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_image = models.ImageField(
        storage=get_profile_storage,
        upload_to='',
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_initials(self):
        """Generate initials for avatar fallback."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        elif self.user.first_name:
            return self.user.first_name[:2].upper()
        else:
            return self.user.username[:2].upper()

    def delete_profile_image(self):
        """Delete the profile image from storage and clear the field."""
        if self.profile_image:
            self.profile_image.delete(save=False)
            self.profile_image = None
            self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile exists for existing users."""
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
