import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    last_login = None
    is_active = None
    is_superuser = None
    is_staff = None
    date_joined = None

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4())
    username = models.CharField(max_length=75)
    muid = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=200)
    phone = models.CharField(unique=True, max_length=15)
    password = models.CharField(max_length=200, blank=True, null=True)
    qr_code = models.CharField(unique=True, max_length=36, default=uuid.uuid4())
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    @classmethod
    def email_exists(cls, email):
        """
        Check if an email address exists in the User model.
        """

        return cls.objects.filter(email=email).exists()

    class Meta:
        db_table = 'user'


class Role(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36, default=uuid.uuid4())
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'role'


class UserRoleLink(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36, default=uuid.uuid4())
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_role_link_user')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_role_link_role')
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'user_role_link'


class Group(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36, default=uuid.uuid4())
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'group'


class UserGroupLink(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36,
                          default=uuid.uuid4()
                          )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_group_link_user'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='user_group_link_group'
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'user_group_link'


class LearningStation(models.Model):
    id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=36,
        default=uuid.uuid4()
    )
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'learning_station'


class Reward(models.Model):
    id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=36,
        default=uuid.uuid4()
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:

        db_table = 'reward'


class UserRewardLink(models.Model):
    id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=36,
        default=uuid.uuid4()
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_reward_link_user'
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name='user_reward_link_reward'
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'user_reward_link'


class FlashCard(models.Model):
    id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=36,
        default=uuid.uuid4()
    )
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'flash_card'


class UserFlashCardLink(models.Model):
    id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=36,
        default=uuid.uuid4()
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_flash_card_link_user'
    )
    flash_card = models.ForeignKey(
        FlashCard,
        on_delete=models.CASCADE,
        related_name='user_flash_card_link_flash_card'
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'user_flash_card_link'


class ForgetPassword(models.Model):
    id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=36,
        default=uuid.uuid4()
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forgot_password_user'
    )
    otp = models.CharField(
        unique=True,
        max_length=6
    )
    expiry = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'forgot_password'
