from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ModelForm
import decimal


class User(AbstractUser):
    pass


class Category_Choice(models.Model):
    category = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
            return f"{self.category}"


class Listing(models.Model):
        
    title = models.CharField(max_length=30)
    owner = models.ForeignKey(
        User, 
        on_delete = models.CASCADE,
        related_name='owner')
    description = models.TextField()
    start_bid = models.IntegerField(validators=[MinValueValidator(decimal.Decimal('0.01'))])
    url = models.URLField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    listing_cat = models.ForeignKey(
        Category_Choice,
        null=True, 
        blank=True,
        default = None,
        on_delete=models.SET_NULL,
        to_field="category",
        db_column="listing_cat")
    finished = models.BooleanField(default=False)
    winner = models.ForeignKey(
        User,
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='winner')
    watchlist = models.ManyToManyField(
        User, 
        blank = True,
        related_name = 'watchlist')

    def __str__(self):
        return f"Title: {self.title}; Owner: {self.owner}; Start bid: {self.start_bid}; Finished: {self.finished}; Winner: {self.winner}"


class Bid(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete = models.CASCADE)
    listing_id = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    bid = models.IntegerField(validators=[MinValueValidator(decimal.Decimal('0.01'))])
    win = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Bidder: {self.user_id}; Listing: {self.listing_id}; Date: {self.date_time}; Bid: {self.bid}; Win: {self.win}"


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
        fields = ['title', 'description', 'start_bid', 'listing_cat', 'url']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'


class CategoryForm(ModelForm):
    class Meta:
        model = Category_Choice
        fields = ['category']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['com']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'