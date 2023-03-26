from django.db import models
import string
import random
import uuid
# Create your models here.

def generate_unique_code():
    return str(uuid.uuid4())[:8]


class Room(models.Model):
    """
    A room model for storing information about a music room.
    """

    code = models.CharField(
        max_length=8, default=generate_unique_code, unique=True
    )
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(default=False)
    votes_to_skip = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    current_song = models.CharField(max_length=50, null=True)
