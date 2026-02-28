from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
#


class Product(models.Model):
    # many products connected to one user
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True)
    price = models.FloatField(null=False)
    image = models.TextField(null=True)
    sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
