from django.contrib import admin
from .models import Listing, Bid, Comment, User, Category_Choice, Watchlist

# Register your models here.
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Category_Choice)
admin.site.register(Watchlist)
