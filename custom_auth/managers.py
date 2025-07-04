from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager


class ApplicationUserManager(UserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        if not email:
            # using None instead of empty string if there's no email to bypass unique=True constraint
            return None
        return super().normalize_email(email)

    def get_by_natural_key(self, value):
        return self.get(**{'%s__iexact' % self.model.USERNAME_FIELD: value})

    def _create_user(self, email, password, **extra_fields):
        """
            Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
            Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        self._create_user(email, password, **extra_fields)