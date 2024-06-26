import random
from django.db import models


def generate_unique_code():
    lenght = 4

    while True:
        code = "".join(random.choices("1234567890", k=lenght))
        if Room.objects.filter(code=code).count() == 0:
            return code


class Room(models.Model):
    code = models.CharField(max_length=4, default=generate_unique_code, unique=True)
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    current_song = models.CharField(max_length=50, null=True)