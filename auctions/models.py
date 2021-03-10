from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title
    owner
    description
    start_bid
    url
    category
    finished
    winner

class Bid(models.Model):
    user_id
    listing_id
    time
    bid

class Comments(models.Model):
    user_id
    listing_id
    com
    time

