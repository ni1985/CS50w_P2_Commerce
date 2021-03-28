from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, ListingForm, Listing, Category_Choice, Watchlist


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def new_listing_view(request):
    if request.method == "POST":
        listing_form = ListingForm(request.POST)

        print(request.user.username)
        print(request.user)


        if listing_form.is_valid():
            new_listing = listing_form.save(commit=False)
            new_listing.owner = request.user
            new_listing.winner = None
            new_listing.save() 

        return HttpResponseRedirect(reverse("index"))

    else:
        listing_form = ListingForm()
        return render(request, "auctions/new_listing.html", {'listing_form':listing_form})


def listing(request, listing_page):
    listing_id = request.GET.get('id')
    listing = Listing.objects.get(id=listing_id)
    print(listing.title)
    return render(request, "auctions/listing.html",{
        "listing": listing
    })


def categories(request):
    return render(request, "auctions/categories.html",{
        "cat": Category_Choice.objects.all()    
    })


def category(request, category_page):
    
    listings = Listing.objects.filter(listing_cat=category_page)
    print(listing)
    
    return render(request, "auctions/category.html",{
        "category": category_page,
        "listings": listings
    })


def watchlist(request):
    user = request.user.id
    print(user)

    listing = Listing.objects.filter(watchlist = user)
    print(listing)

    return render(request, "auctions/watchlist.html",{
        "listings": listing
    })


def comments(request):
    return render(request, "auctions/comments.html",{
        "comment": "test name for comment"
    })