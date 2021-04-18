from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max, Count
from django.core.exceptions import ObjectDoesNotExist

from .models import User, ListingForm, Listing, Category_Choice, Watchlist, CommentForm, BidForm, Bid, Comment


def index(request):
    # Retrieve all unfinished listings
    listings = Listing.objects.filter(finished__exact = False).values()
    
    # Retrieve Max bids for all listings and filter by ID
    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    max_bids = []
    print(max_bids)

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
    
    print(f"request POST: {request.POST}")
    # retrieve listing ID
    listing_id = request.GET.get('id')

    # Retrieve all data about the listing
    listing = Listing.objects.get(id=listing_id)

    # Retrieve value of teh current Bid
    current_bid = Bid.objects.filter(listing_id=listing_id)
    
    # check if there was bids
    if current_bid:
        max_bid = current_bid.latest('bid').bid
        date_bid = current_bid.latest('bid').date_time
    else:
        max_bid = listing.start_bid
        date_bid = None


    print(f"bid: {current_bid}")
    #print(f"bidder: {current_bid.latest('bid').user_id}")
    #.latest('bid')

    # If there is no bids current bid = start bid 
    #if current_bid == None:
    #    max_bid = listing.start_bid
    #else:
    #    max_bid = current_bid.bid
    
    print(f"Max bid: {max_bid}")

    # button bid
    if request.method == 'POST' and 'btn_bid' in request.POST:
        bid_form = BidForm(request.POST)

        if bid_form.is_valid():
     
            new_bid = bid_form.save(commit=False)
            new_bid.user_id = request.user
            new_bid.listing_id = listing
            print(f"BidForm: {new_bid}")
            if new_bid.bid < max_bid:
                print(f"Error")
                return render(request, "auctions/error.html", {
                    'message':'Your bid is lower than the current price'
                })
            print(f"New bid{new_bid}")
            new_bid.save() 

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # add a comment
    elif request.method == 'POST' and 'btn_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user_id = request.user
            new_comment.listing_id = listing
            print(new_comment)
            new_comment.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # button add to watchlist
    #elif request.method == 'GET' and 'btn_wtchlst' in request.POST:
        
        #print('123456')
        #watchlist = Watchlist(user_id=user_id, listing_id=listing_id)
        # Watchlist.objects.get(user_id).entry_set.add(listing_id)
        #print(Watchlist.objects.get(listing_id = listing_id))
        #watchlist.save()

        #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # stop auction
    elif request.method == 'POST' and 'stop_auction' in request.POST:
        
        stop_auction = request.POST
        print(f"stop auction: {stop_auction}")
        listing.finished = True
        
        if current_bid:
            listing.winner = current_bid.latest('bid').user_id
            current_bid.latest('bid').win = True
            current_bid.latest('bid').save()
        
        listing.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))        

    else:
        
        comment_form = CommentForm()
        bid_form = BidForm()
        comments = Comment.objects.filter(listing_id=listing_id).order_by('-date_time')
        print(listing)
        print(f"listing_id {listing_id}")
        return render(request, "auctions/listing.html", {
            'listing': listing,
            'comment_form': comment_form,
            'bid_form': bid_form,
            'current_bid': max_bid,
            'comments': comments,
            'current_user': request.user,
            'date_bid': date_bid,
            'listing_id':listing_id
        })

# Add finished listings
#def finished_listing(request):
#    return render(request, "auctions/comments.html",{
#        "comment": "test name for comment"
#    })

# Show Categories
def categories(request):
    return render(request, "auctions/categories.html",{
        "cat": Category_Choice.objects.all()    
    })

# Show page with selected categories
def category(request, category_page):
    
    listings = Listing.objects.filter(listing_cat=category_page)
    print(listings)

    # Retrieve Max bids for all listings and filter by ID
    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    max_bids = []
    print(max_bids)

    # for all listings if there is no bids show start bid
    for i in range(0, len(listings)):
        
        if bids[i]['max_bid'] == None:
            max_bids.append(listings[i]['start_bid'])
        else:
            max_bids.append(bids[i]['max_bid'])
    
    # zip data from listings with max_bids
    zipped_list = zip(listings, max_bids)
    
    return render(request, "auctions/category.html",{
        "category": category_page,
        #"listings": listings
        "zipped_list": zipped_list
    })

def archive(request):
    
    # Retrieve all listings added to the watchlist
    listings = Listing.objects.filter(finished=True)
    print(listings)

    # Retrieve Max bids for all listings and filter by ID
    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    max_bids = []
    print(bids)
    print(f"max bids: {bids}")
    
    print(f"listing number 1: {listings[0]}")
    print(len(listings))
    print(listings[0].start_bid)
    
    # for all listings if there is no bids show start bid
    for i in range(0, len(listings)):
        if bids[i]['max_bid'] == None:
            max_bids.append(listings[i].start_bid)
        else:
            max_bids.append(bids[i]['max_bid'])

    zipped_list = zip(listings, max_bids)
    print(max_bids)

    return render(request, "auctions/archive.html",{
        #"listings": listing
        "zipped_list": zipped_list
    })

# Show Watchlist
def watchlists(request):
    
    user = request.user.id
    user2 = request.user
    print(user2)
    #add_user = request.GET.get('add_user', 'empty')
    listing_id = request.GET.get('listing_id')

    print(f"listing_id {listing_id}")

    if listing_id == 'empty':
        print("no user")
    else:
        # add listing to the watchlist of the current user
        
        wtchl = Watchlist.objects.create(user_id=user2)
        print(f"WATCHLIST {wtchl}")
        wtchl.save()
        wtchl.listing_id.add(listing_id)



    # Retrieve all listings added to the watchlist
    #listings = Listing.objects.filter(watchlist__user_id=user)
    #print(listings)
    #if not listings:
    #    print("None")
    #    return render(request, "auctions/watchlist.html",{
            ##"listings": listing
    #        "zipped_list": None
    #    })

    #else:  
    #    # Retrieve Max bids for all listings and filter by ID
    #    bids = listings.values('title').annotate(max_bid=Max('bid__bid')).extra(order_by = ['id'])
    #    max_bids = []
    #    print(bids)
    #    print(f"max bids: {bids}")
        
    #    print(f"listing number 1: {listings[0]}")
    #    print(len(listings))
    #    print(listings[0].start_bid)
        
    ##    # for all listings if there is no bids show start bid
    #    for i in range(0, len(listings)):
    #        if bids[i]['max_bid'] == None:
    #            max_bids.append(listings[i].start_bid)
    #        else:
    #            max_bids.append(bids[i]['max_bid'])

    #    zipped_list = zip(listings, max_bids)
    #    print(max_bids)

        return render(request, "auctions/watchlist.html",{
            #"listings": listing
        #    "zipped_list": zipped_list
            "zipped_list": None
        })


