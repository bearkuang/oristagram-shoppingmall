from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class ManagerAccountManager(BaseUserManager):
    def create_user(self, manager_id, password=None, **extra_fields):
        if not manager_id:
            raise ValueError('The Manager ID must be set')
        user = self.model(manager_id=manager_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, manager_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(manager_id, password, **extra_fields)

class ManagerAccount(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    manager_id = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = 'manager_id'
    REQUIRED_FIELDS = []

    objects = ManagerAccountManager()

    def __str__(self):
        return self.manager_id

class CompanyAccount(models.Model):
    id = models.AutoField(primary_key=True)
    company_id = models.CharField(max_length=20, unique=True)
    company_pwd = models.CharField(max_length=20)
    activate = models.IntegerField(default=0)

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    cust_username = models.CharField(max_length=20, unique=True)
    cust_name = models.CharField(max_length=50)
    cust_password = models.CharField(max_length=20)
    cust_gender = models.CharField(max_length=1, null=True, default='F')
    cust_birthday = models.DateField(null=True)
    cust_address = models.CharField(max_length=256)
    cust_email = models.CharField(max_length=256)
    cust_create_date = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_authenticated(self):
        return True
