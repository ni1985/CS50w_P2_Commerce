from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing_view, name="new_listing"),
    path("listings/<str:listing_page>", views.listing, name="listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_page>", views.category, name="category"),
    path("watchlist", views.watchlists, name="watchlist"),
    path("archive", views.archive, name="finished"),
]
