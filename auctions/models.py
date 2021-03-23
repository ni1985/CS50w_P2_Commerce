from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ModelForm
import decimal


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
    start_bid = models.IntegerField(validators=[MinValueValidator(decimal.Decimal('0.01'))])
    url = models.URLField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(choices=CATEGORY_CHOICES, default = "no", max_length=2)
    finished = models.BooleanField(default=False)
    winner = models.ForeignKey(
        User,
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='winner')

    def __str__(self):
        return f"Title: {self.title}; Owner: {self.owner}; Start bid: {self.start_bid}; Category: {self.category}; Finished: {self.finished}; Winner: {self.winner}"


class Bid(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete = models.CASCADE)
    listing_id = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    bid = models.IntegerField(validators=[MinValueValidator(decimal.Decimal('0.01'))])
    winner = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Bidder: {self.user_id}; Listing: {self.listing_id}; Date: {self.date_time}; Bid: {self.bid}; Winner: {self.winner}"


class Comment(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete = models.CASCADE)
    listing_id = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE)
    com = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_id}; Listing: {self.listing_id}; Date: {self.date_time}"


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'start_bid', 'url', 'category']