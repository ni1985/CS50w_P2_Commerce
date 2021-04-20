from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max, Count
from django.core.exceptions import ObjectDoesNotExist
from .models import User, ListingForm, Listing, Category_Choice, CommentForm, BidForm, Bid, Comment
from django.contrib.auth.decorators import login_required


def index(request):
    # Retrieve all running listings
    listings = Listing.objects.filter(finished__exact = False).values()

    # Retrieve Max bids for all listings and filter by ID
    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    max_bids = []

    # for all listings if there is no bids show start bid
    for i in range(0, len(listings)):

        if bids[i]['max_bid'] == None:
            max_bids.append(listings[i]['start_bid'])
        else:
            max_bids.append(bids[i]['max_bid'])

    # zip data from listings with max_bids
    zipped_list = zip(listings, max_bids)

    return render(request, "auctions/index.html", {
        "zipped_list": zipped_list
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


@login_required
def new_listing_view(request):
    if request.method == "POST":
        # Read form from the POST request
        listing_form = ListingForm(request.POST)

        # if form is valid update the database
        if listing_form.is_valid():
            new_listing = listing_form.save(commit=False)
            new_listing.owner = request.user
            new_listing.winner = None
            new_listing.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        # Read a form from the Models
        listing_form = ListingForm()
        return render(request, "auctions/new_listing.html", {'listing_form':listing_form})


def listing(request, listing_page):
    print(request.user)
    # Retrieve listing ID
    listing_id = request.GET.get('id')

    # Error if listing is not found
    if not Listing.objects.filter(id=listing_id).exists():
        return render(request, "auctions/error.html", {
            'message':'Listing not found'
        })

    # Retrieve all data about the listing
    listing = Listing.objects.get(id=listing_id)

    # Retrieve value of the current Bid
    current_bid = Bid.objects.filter(listing_id=listing_id)
    num_bids = current_bid.count()

    # check if there was bids
    if current_bid:
        max_bid = current_bid.latest('bid').bid
        date_bid = current_bid.latest('bid').date_time
        user_bid = current_bid.latest('bid').user_id
        print(user_bid)
    else:
        max_bid = listing.start_bid
        date_bid = None
        user_bid = None

    # Action with a 'Bid' button
    if request.method == 'POST' and 'btn_bid' in request.POST:
        bid_form = BidForm(request.POST)

        # Make bid if form is valid
        if bid_form.is_valid():
            new_bid = bid_form.save(commit=False)
            new_bid.user_id = request.user
            new_bid.listing_id = listing

            # Check if the bid is less than previous bid or start bid
            if current_bid:
                if new_bid.bid <= current_bid.latest('bid').bid:
                    return render(request, "auctions/error.html", {
                        'message':'Your bid is lower than the current price'
                    })
            else: 
                if new_bid.bid < listing.start_bid:        
                    return render(request, "auctions/error.html", {
                        'message':'Your bid is lower than the current price'
                    })

            new_bid.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Action with a 'Comment' button
    elif request.method == 'POST' and 'btn_comment' in request.POST:
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user_id = request.user
            new_comment.listing_id = listing
            new_comment.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Stop auction
    elif request.method == 'POST' and 'stop_auction' in request.POST:

        stop_auction = request.POST
        listing.finished = True

        if current_bid:
            listing.winner = current_bid.latest('bid').user_id
            current_bid.latest('bid').win = True
            current_bid.latest('bid').save()

        listing.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # retrieve data to generate listing information
    else:

        comment_form = CommentForm()
        bid_form = BidForm()
        comments = Comment.objects.filter(listing_id=listing_id).order_by('-date_time')
        current_user = request.user
        
        if request.user.is_anonymous:
            wtchlst = None
        else:
            print("not ananymous")
            wtchlst = Listing.objects.filter(id=listing_id, watchlist = current_user).exists()

        return render(request, "auctions/listing.html", {
            'listing': listing,
            'comment_form': comment_form,
            'bid_form': bid_form,
            'current_bid': max_bid,
            'comments': comments,
            'current_user': request.user,
            'date_bid': date_bid,
            'user_bid': user_bid,
            'listing_id':listing_id,
            'wtchlst': wtchlst,
            'num_bids': num_bids
        })

# Show Categories
def categories(request):
    return render(request, "auctions/categories.html",{
        "cat": Category_Choice.objects.all()
    })


# Show page with selected categories
def category(request, category_page):

    listings = Listing.objects.filter(listing_cat=category_page)

    # Retrieve Max bids for all listings and filter by ID
    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    max_bids = []

    # for all listings if there is no bids show start bid
    for i in range(0, len(listings)):
        if bids[i]['max_bid'] == None:
            max_bids.append(listings[i].start_bid)
        else:
            max_bids.append(bids[i]['max_bid'])

    # zip data from listings with max_bids
    zipped_list = zip(listings, max_bids)

    return render(request, "auctions/category.html",{
        "category": category_page,
        "zipped_list": zipped_list
    })


def archive(request):

    # Retrieve all finished listings
    listings = Listing.objects.filter(finished=True)

    # Retrieve Max bids for all listings and filter by ID
    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    max_bids = []

    # for all listings if there is no bids show start bid
    for i in range(0, len(listings)):
        if bids[i]['max_bid'] == None:
            max_bids.append(listings[i].start_bid)
        else:
            max_bids.append(bids[i]['max_bid'])

    zipped_list = zip(listings, max_bids)

    return render(request, "auctions/archive.html",{
        #"listings": listing
        "zipped_list": zipped_list
    })


# Show Watchlist
@login_required
def watchlists(request):

    user = request.user.id
    add_user = request.GET.get('add_user', 'empty')
    remove_user = request.GET.get('remove_user', 'empty')
    listing_title = request.GET.get('listing_title', 'empty')

    if listing_title != 'empty' and add_user != 'empty':
        # add user to the watchlist of the listing
        current_listing = Listing.objects.get(title = listing_title)
        watchlist_user = User.objects.get(username = add_user)
        current_listing.watchlist.add(watchlist_user)

    if listing_title != 'empty' and remove_user != 'empty':
        # remove user from the watchlist of the listing
        current_listing = Listing.objects.get(title = listing_title)
        watchlist_user = User.objects.get(username = remove_user)
        current_listing.watchlist.remove(watchlist_user)

    listings = Listing.objects.filter(watchlist = user)

    # Retrieve all listings added to the watchlist
    if not listings:
        zipped_list = None

    else:
        # Retrieve Max bids for all listings and filter by ID
        bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
        max_bids = []

        # for all listings if there is no bids show start bid
        for i in range(0, len(listings)):
            if bids[i]['max_bid'] == None:
                max_bids.append(listings[i].start_bid)
            else:
                max_bids.append(bids[i]['max_bid'])

        zipped_list = zip(listings, max_bids)

    return render(request, "auctions/watchlist.html",{
        #"listings": listing
        "zipped_list": zipped_list
    })


