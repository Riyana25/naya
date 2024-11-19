from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    pharmacyName = models.CharField(max_length=255, blank=True)
    registrationNumber = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    registrationCertificate = models.FileField(upload_to='certificates/', null=True, blank=True)
    terms = models.BooleanField(default=False)
    
    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',  # Specify a unique related_name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Specify a unique related_name
        blank=True,
    )
    
   
    # The issue you mentioned earlier is related to reverse accessor clashes between the CustomUser model and Django's default User model. In this new model (Custom), since you're inheriting from AbstractUser, the problem might arise if you don't specify related_name for certain fields like groups and user_permissions that Django automatically adds to the AbstractUser class.

# To avoid reverse accessor conflicts, you need to explicitly specify a related_name for these fields when defining your custom user model.

    # def __str__(self):
    #     return self.username
