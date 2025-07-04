
import uuid as uuid
from datetime import timedelta
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import PermissionsMixin
from model_utils import Choices
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from custom_auth.managers import ApplicationUserManager
from django.utils.crypto import get_random_string

from custom_auth.mixins import UserPhotoMixin


# Create your models here.
class ApplicationUser(
    AbstractBaseUser,
    PermissionsMixin
):
    LOGIN_TYPE = Choices(
        ("Simple", "Simple"),
    )
    username_validator = UnicodeUsernameValidator()
    uuid = models.UUIDField(
        verbose_name=_('uuid'),
        unique=True,
        help_text=_('Required. A 32 hexadecimal digits number as specified in RFC 4122.'),
        error_messages={
            'unique': _('A user with that uuid already exists.'),
        },
        default=uuid.uuid4,
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True,
                              error_messages={'unique': _('A user with that email already exists.')}, )
    # is_email_verified = models.BooleanField(_('email verified'), default=True)
    # nick_name = models.CharField(_('nick name'), max_length=30, unique=True, null=True, blank=True)
    # promo_code = models.CharField(_('promo code'), max_length=30, null=True, blank=True)
    # referral_code = models.CharField(_('referral code '), max_length=30, null=True, blank=True)

    # Social Login Fields
    # login_type = models.CharField(choices=LOGIN_TYPE, default=LOGIN_TYPE.Simple, max_length=7)
    # social_key = models.CharField(max_length=2048, blank=True, null=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)
    last_user_activity = models.DateTimeField(_('last activity'), default=timezone.now)
    coins = models.PositiveBigIntegerField(_('coins'), default=25000, null=True, blank=True)
    otp = models.PositiveSmallIntegerField(_('otp'), null=True, blank=True)

    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    # bind_email = models.EmailField(_('bind email'), null=True, blank=True, unique=True,
    #                                error_messages={'unique': _('Failed! This Email is bound to another account.')}, )
    # bind_email_verification = models.PositiveSmallIntegerField(_('bind email verification'), null=True, blank=True)

    # is_agent = models.BooleanField(
    #     _('is agent'),
    #     default=False,
    #     help_text=_(
    #         'Designates whether this user should be treated as agent. '
    #         'Unselect this instead of deleting agent.'
    #     ),
    # )
    # time_bank = models.DurationField(verbose_name=_('time bank (time)'),
    #                                  help_text=_('time bank time should be in (HH:MM:SS) format.'), default=timedelta)

    objects = ApplicationUserManager()

    # EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username or self.email or str(self.uuid)

    def save(self, *args, **kwargs):
        self.last_user_activity = timezone.now()
        self.last_modified = timezone.now()

        # if self.referral_code is None:
        #     if self.is_agent == 1:
        #         self.referral_code = get_random_string(8)

        # if self.photo and (not self.width_photo or not self.height_photo):
        #     self.width_photo = self.photo.width
        #     self.height_photo = self.photo.height

        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

        # if not self.nick_name:
        #     new_nick_name = self.email.split('@')[0] if self.email else ''
        #
        #     if self._meta.model._default_manager.filter(nick_name=new_nick_name).exists() or new_nick_name == '':
        #         postfix = timezone.now().strftime('%Y%m%d%H%M%S')
        #
        #         while self._meta.model._default_manager.filter(nick_name=new_nick_name + postfix).exists():
        #             postfix = timezone.now().strftime('%Y%m%d%H%M%S')
        #
        #         new_nick_name += postfix
        #
        #     self.nick_name = new_nick_name

        return super(ApplicationUser, self).save(*args, **kwargs)

    def update_last_activity(self):
        now = timezone.now()

        print(self.last_user_activity)
        self.last_user_activity = now
        self.save(update_fields=('last_user_activity', 'last_modified'))