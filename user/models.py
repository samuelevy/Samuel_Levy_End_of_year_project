from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class AppUserManager(BaseUserManager): #Needed because using  a custom user ; might need tweaking
    def create_user(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError('The Name field must be set')
        user=self.model(name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return (self.create_user(name, password, **extra_fields))
    
    def get_by_natural_key(self, username):
        return self.get(name=username)
    

# Create your models here.
class AppUser(AbstractBaseUser, PermissionsMixin):
    """
    Main user model matching your database schema
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('PLAYER', 'Player'),
    ]
    
    user_id = models.AutoField(primary_key=True, db_column='user_id')
    name = models.CharField(max_length=100, db_column='name', unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_column='role')
    password = models.CharField(max_length=255, db_column='password_hash')
    
    #Handle authentication
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
    last_login = models.DateTimeField(null=True, blank=True, db_column='last_login')
    is_superuser = models.BooleanField(default=False, db_column='is_superuser')
    is_active = models.BooleanField(default=True, db_column='is_active')
    is_staff = models.BooleanField(default=False, db_column='is_staff')
    date_joined = models.DateTimeField(default=timezone.now, db_column='date_joined')
    
    objects = AppUserManager() #Sets as manager
    
    class Meta:
        db_table = 'app_user'
        managed = False  # Indicates that Django should not manage the database table
    def set_password(self, raw_password):
        self.password = make_password(raw_password) # Hash the password before saving
    def check_password(self, raw_password):
        return check_password(raw_password, self.password) # Verify the password
    def __str__(self):
        return f"{self.name} ({self.role})" # String representation of the user (name and role)