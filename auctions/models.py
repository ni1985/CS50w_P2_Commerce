from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    
    CATEGORY_CHOICES = [
        ('bk', 'Books'),
        ('no', 'No category listed'),
        ('ki', 'Kitchen'),
        ('gd', 'Garden'),
        ('mg', 'Magic'),
    ]
    
    title = models.CharField(max_length=30)
    owner = models.ForeignKey(
        User, 
        on_delete = models.CASCADE,
        related_name='owner')
    description = models.TextField()
    start_bid = models.IntegerField()
    url = models.URLField()
    category = models.CharField(choices=CATEGORY_CHOICES, default = "no", max_length=2)
    finished = models.BooleanField()
    winner = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name='winner')

class Bid(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete = models.CASCADE)
    listing_id = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    bid = models.IntegerField()
    winner = models.BooleanField()

class Comments(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete = models.CASCADE)
    listing_id = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE)
    com = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)

