from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, user_id, email, password=None):
        if not id:
            raise ValueError('must have user id')
        if not email:
            raise ValueError('must have user email')
        user = User(
            name=user_id,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password):
        user = self.create_user(user_id=name,
                                email=self.normalize_email(email),
                                password=password,
                                )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_payedOn = models.DateTimeField(null=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name


    def has_perm(self, perm, obj=None):
        return True


    def has_module_perms(self, app_label):
        return True


    @property
    def is_staff(self):
        return self.is_admin