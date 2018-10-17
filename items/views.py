from django.shortcuts import render, redirect
from items.models import Item,FavoriteItem 
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q

# Create your views here.
def item_favorite(request, item_id):
    item_obj = Item.objects.get(id= item_id)
    
    print("logged in")

    favorited, created = FavoriteItem.objects.get_or_create(item=item_obj, user=request.user)

    if created:
        action = "favorite"
    else:
        action = "unfavorite"
        favorited.delete()

    print(action)
    data = {
    "action": action
    }
    
    return JsonResponse(data)

def wishlist(request):
    wishlist = []
    items=Item.objects.all()
    query = request.GET.get('q')
    if query:
       items = items.filter(Q(name__contains=query)|
                                           Q(description__contains=query)).distinct()
    if request.user.is_authenticated:
        for item in items:
            for favorite in FavoriteItem.objects.filter(user=request.user):
                if item.id==favorite.item.id:
                    wishlist.append(item)
    
    context = {
        "wishlist": wishlist
    }
    return render(request, 'wishlist.html', context)

def item_list(request):
    items= Item.objects.all()
    query = request.GET.get("q")
    if query:
        items = items.filter(Q(name__contains=query)|
                                           Q(description__contains=query)).distinct()
    my_favorites = []
    if not request.user.is_anonymous:
        for favorite in FavoriteItem.objects.filter(user = request.user):
            my_favorites.append(favorite.item.id)
    context = {
        "items": items,
        'favorites': my_favorites,
    }
    return render(request, 'item_list.html', context)

def item_detail(request, item_id):
    context = {
        "item": Item.objects.get(id=item_id)
    }
    return render(request, 'item_detail.html', context)

def user_register(request):
    register_form = UserRegisterForm()
    if request.method == "POST":
        register_form = UserRegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect('item-list')
    context = {
        "register_form": register_form
    }
    return render(request, 'user_register.html', context)

def user_login(request):
    login_form = UserLoginForm()
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect('item-list')
    context = {
        "login_form": login_form
    }
    return render(request, 'user_login.html', context)

def user_logout(request):
    logout(request)

    return redirect('item-list')