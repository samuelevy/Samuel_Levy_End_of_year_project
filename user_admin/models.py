from django.db import models
from user.models import AppUser

# Create your models here.
class Admin(models.Model):
    # Link to AppUser (one-to-one relationship)
    user = models.OneToOneField(
        AppUser, 
        on_delete=models.CASCADE,  # If user deleted, delete admin too
        primary_key=True,
        related_name='admin_profile'
    )

    class Meta:
        db_table = 'admin_user'
        managed=False