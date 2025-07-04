import os
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Subquery


def get_user_photo_random_filename(instance, filename):
    extension = os.path.splitext(filename)[1]
    return '{}/{}{}'.format(settings.USER_PHOTOS, uuid.uuid4(), extension)


def get_lobby_photo_random_filename(instance, filename):
    extension = os.path.splitext(filename)[1]
    return '{}/{}{}'.format(settings.LOBBY_PHOTOS, uuid.uuid4(), extension)

def get_emoji_photo_random_filename(instance, filename):
    extension = os.path.splitext(filename)[1]
    return '{}/{}{}'.format(settings.EMOJI_PHOTO, uuid.uuid4(), extension)


def get_avatar_photo_random_filename(instance, filename):
    extension = os.path.splitext(filename)[1]
    return '{}/{}{}'.format(settings.AVATAR_PHOTOS, uuid.uuid4(), extension)


class SQCount(Subquery):
    template = "(SELECT count(1) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()