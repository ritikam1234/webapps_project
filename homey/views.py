from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from homey.models import Recipe, Review, Profile, GroceryItem, CreateEvent, IngredientItem, FeedEvent
from homey.forms import RecipeForm, ReviewForm, ProfileForm, GroceryForm, CreateEventForm
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from oauth2_provider.views.generic import ProtectedResourceView
from oauth2client.service_account import ServiceAccountCredentials

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from .models import Event
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import pytz
import httplib2
from google_auth_oauthlib.flow import InstalledAppFlow
from django.conf import settings
import json


def showpubliccalendar(request):
    return render(request, 'homey/calendar.html')
    
# #added
class CalendarView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("This is your calendar view")
    

# def credentials_to_dict(credentials):
#     return {'token': credentials.token,
#             'refresh_token': credentials.refresh_token,
#             'token_uri': credentials.token_uri,
#             'client_id': credentials.client_id,
#             'client_secret': credentials.client_secret,
#             'scopes': credentials.scopes}

# from social.apps.django_app.utils import load_strategy



from django.contrib.auth import views as auth_views
@login_required
def other_profile_action(request, id):
    context = {}
    other_user = get_object_or_404(User,id = id)
    if (request.user.id == id):
        context = {'form': ProfileForm({'bio':request.user.profile.bio}), 'bookmarked_recipes':request.user.profile.bookmarked_recipes.all(), 'profile': other_user.profile}
        recipes = Recipe.objects.filter(user= request.user)
        context['recipes'] = recipes
        return render(request, 'homey/dashboard.html', context)
    context = {'profile': other_user.profile, 'recipes': other_user.created_recipes.all()}
    return render(request, 'homey/other_profile.html', context)

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)

#adding an add recipe logging to calendar 
from django.utils import dateformat
def addtocalendar(request,id):
    recipe = get_object_or_404(Recipe, id=id)
    createdevent = CreateEvent(user=request.user)
    date = dateformat.format(timezone.now(), 'Y-m-d')
    newtitle = "I cooked " + recipe.title + "!"
    form = CreateEventForm(instance=createdevent, initial={'title': newtitle, 'summary':recipe.steps, 'date':date,'location': 'Home :)'})

    if not form.is_valid():
        event = CreateEvent.objects.filter(user=request.user)
        context = { 'form': form, 'newevents': event }
        return render(request, 'homey/calendar_events.html', context)
    
    event = CreateEvent.objects.filter(user=request.user)
    context = {'form': form, 'recipe': recipe, 'newevents': event }

    return render(request, 'homey/calendar_events.html', context)

def parse_grocery(grocery_list):
    parsed_grocery_list = ""
    for i in range(len(grocery_list)):
        parsed_grocery_list += (grocery_list[i].text + ": " + str(grocery_list[i].quantity) + " " + grocery_list[i].units)
        parsed_grocery_list += " \n"
    return parsed_grocery_list

def addgrocerytocalendar(request):
    grocery_list = GroceryItem.objects.filter(user=request.user)
    parsed_grocery_list = parse_grocery(grocery_list)
    createdevent = CreateEvent(user=request.user)
    newtitle = "Grocery Run"
    form = CreateEventForm(instance=createdevent, initial={'title': newtitle, 'summary':parsed_grocery_list})

    if not form.is_valid():
        event = CreateEvent.objects.filter(user=request.user)
        context = { 'form': form, 'newevents': event }
        return render(request, 'homey/calendar_events.html', context)
    
    event = CreateEvent.objects.filter(user=request.user)
    context = {'form': form, 'title': newtitle, 'summary':parsed_grocery_list, 'newevents': event}
    return render(request, 'homey/calendar_events.html', context)




def logout(request):
     # message user or whatever
    auth_views.logout_then_login(request)
    return render(request, 'homey/home.html', {})


from pathlib import Path
from configparser import ConfigParser

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")


import dateutil.parser as parser
@login_required
def fetch_events(request):
 
    client_id = CONFIG.get("GoogleOAuth2", "client_id")
    client_secret = CONFIG.get("GoogleOAuth2", "client_secret")
    token = request.user.social_auth.get(provider='google-oauth2').extra_data['access_token']
    refresh_token =  request.user.social_auth.get(provider='google-oauth2').extra_data['refresh_token']
    if (refresh_token is None):
        return redirect('logout')
    token_uri = "https://oauth2.googleapis.com/token"
    creds = Credentials(token = token, token_uri=token_uri, client_id =client_id, client_secret=client_secret, refresh_token = refresh_token)
    service = build('calendar', 'v3', credentials=creds)


    if request.method == 'GET':
        c = CreateEventForm()
        event = CreateEvent.objects.filter(user=request.user)
        context = { 'form': c, 'newevents': event}
        return render(request, 'homey/calendar_events.html', context)

    createdevent = CreateEvent(user=request.user)
    eventform = CreateEventForm(request.POST, instance=createdevent)
    if not eventform.is_valid() or 'date' not in request.POST or 'start' not in request.POST or 'end' not in request.POST or 'location' not in request.POST or 'title' not in request.POST:
        event = CreateEvent.objects.filter(user=request.user)
        context = { 'form': eventform, 'newevents': event}
        return render(request, 'homey/calendar_events.html', context)
    eventform.save()


    startdate = eventform.cleaned_data['date']

    starttime = eventform.cleaned_data['start']

    endtime = eventform.cleaned_data['end']

    neweventinfo = {
        'title': request.POST['title'],
        'location': request.POST['location'],
        'start': starttime,
        'end':endtime,
        'date': startdate
    }
    enddatetime = startdate + " " + endtime  
    startdatetime = startdate + " " + starttime
    newtime = parser.parse(startdatetime)
    newendtime = parser.parse(enddatetime)
    event1 = {
        'summary': request.POST['title'],
        'location': request.POST['location'],
        'description': request.POST['summary'],
        'start': {
        'dateTime': newtime.isoformat() + "-05:00",
        'timeZone': 'America/New_York'
        },
        'end': {
        'dateTime': newendtime.isoformat() + "-05:00",
        'timeZone': 'America/New_York'
        },  
        'eventType': 'default'
    };
    if request.POST['attendees'] != "":
        event1['attendees']= [
        {'email': request.POST['attendees']}
        ]
    event = service.events().insert(calendarId='primary', body=event1).execute()
    eventlink = event.get('htmlLink')
    neweventinfo['eventlink'] = eventlink

    newevents = CreateEvent.objects.filter(user=request.user)
    new_feed_event = FeedEvent(time=timezone.now(), user=request.user, title=createdevent.title, temp_id=-1, text="scheduled a new event: ")
    new_feed_event.save()
    context = { 'form': eventform, 'event': neweventinfo, 'eventlink':eventlink, 'newevents': newevents}
    return render(request, 'homey/calendar_events.html', context)
    
@login_required
def post_recipe(request):
    if request.method == 'GET':
        r = RecipeForm()
        context = { 'form': r, 'ingredients': []}
        return render(request, 'homey/recipeform.html', context)

    recipe = Recipe()

    recipe.user=request.user
    recipe.creation_time=timezone.now()

    recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
    try:
        ingredients_data = json.loads(request.POST.get('ingredients', '[]'))
    except json.JSONDecodeError:
        ingredients_data = []

    # Check if ingredients data is empty
    if not ingredients_data:
        # Handle empty ingredients case
        recipe_form.add_error('list_ingredient', 'Please add at least one ingredient.')
    if not recipe_form.is_valid():
        context = { 'form': recipe_form, 'ingredients': ingredients_data}
        return render(request, 'homey/recipeform.html', context)

    pic = recipe_form.cleaned_data['picture']
    print('Uploaded picture: {} (type={})'.format(pic, type(pic)))

    recipe.picture = recipe_form.cleaned_data['picture']
    recipe.content_type = recipe_form.cleaned_data['picture'].content_type
    recipe_form.save()
    for ing in ingredients_data:
        ingredient = IngredientItem(
            ingredient=ing['name'], quantity=float(ing['quantity']),
            units=ing['units']
        )
        ingredient.save()
        recipe.list_ingredient.add(ingredient)

    
    new_feed_event = FeedEvent(time=recipe.creation_time, user=request.user, title=recipe.title, temp_id=recipe.id, text="posted a new recipe")
    new_feed_event.save()
    recipes = Recipe.objects.all()

    
    context = { 'recipes': recipes}
    return display_recipe(request, recipe.id)

@login_required
def post_review(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    profile = get_object_or_404(Profile, user=request.user)
    reviews = Review.objects.filter(recipe=recipe)

    if (recipe.user == request.user):
        context = {'recipe': recipe, 'reviews': reviews, 'myrecipe': True, 'error': "You cannot review your own recipe."}
     
        return render(request, 'homey/display_recipe.html', context)

    bookmarked = profile.bookmarked_recipes.filter(id=id).exists()
    
    context = {'recipe': recipe, 'bookmarked': bookmarked, 'reviews': reviews}

    # redirect to displaying recipe if get request
    if request.method == 'GET':
        return redirect('recipe', id=id)
    
    review = Review(user=request.user, recipe=recipe)
    form = ReviewForm(request.POST, request.FILES, instance=review)
    if not form.is_valid():
        context['reviewform'] = form
        return render(request, 'homey/display_recipe.html', context)

    pic = form.cleaned_data['picture']
    # print('Uploaded picture: {} (type={})'.format(pic, type(pic)))
    review.picture = form.cleaned_data['picture']
    review.content_type = form.cleaned_data['picture'].content_type
    form.save()
    new_feed_event = FeedEvent(time=timezone.now(), user=request.user, text="reviewed this recipe", recipe=recipe)
    new_feed_event.save()
        
    reviews = Review.objects.filter(recipe=recipe)
    update_avg_rating(request, id)

    context['reviews'] = reviews
    context['recipe'] = get_object_or_404(Recipe, id=id)

    return render(request, 'homey/display_recipe.html', context)

@login_required 
def get_review_picture(request, id):
    review = get_object_or_404(Review, id=id)
    # print('Picture #{} fetched from db: {} (type={})'.format(id, review.picture, type(review.picture)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not review.picture:
        raise Http404

    return HttpResponse(review.picture, content_type=review.content_type)

@login_required
def get_recipe_picture(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    # print('Picture #{} fetched from db: {} (type={})'.format(id, recipe.picture, type(recipe.picture)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not recipe.picture:
        raise Http404

    return HttpResponse(recipe.picture, content_type=recipe.content_type)


def get_recipes(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    recipes = []
    for recipe in Recipe.objects.all():
        my_recipe = {
            'id': recipe.id,
            'title': recipe.title,
            'ingredients': recipe.get_ingredients(),
            'steps': recipe.steps,
            'avg_rating': recipe.average_rating,
            'tags': recipe.tags,
            'username': recipe.user.username,
            'fname': recipe.user.first_name,
            'lname': recipe.user.last_name,
        }
        recipes.append(my_recipe)

    response_json = json.dumps(recipes)

    return HttpResponse(response_json, content_type='application/json')

def get_reviews(request, recipeid):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    reviews = []
    recipe = get_object_or_404(Recipe, id=recipeid)
    allreviews = Review.objects.filter(recipe=recipe)
    for review in allreviews:
        my_review = {
            'id': review.id,
            'rating': review.rating,
            'username': review.user.username,
            'fname': review.user.first_name,
            'lname': review.user.last_name,
            'user_id':review.user.id
        }
        reviews.append(my_review)
    response_json = json.dumps(reviews)

    return HttpResponse(response_json, content_type='application/json')



@login_required
def recipe_stream(request):
    recipes = Recipe.objects.all()
    context = { 'recipes': recipes}

    return render(request, 'homey/recipestream.html', context) 

@login_required
def update_avg_rating(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    sum=0
    num_reviews=0
    for review in recipe.reviews.all():
        sum += review.rating
        num_reviews+=1

    if num_reviews > 0:
        recipe.average_rating = sum/num_reviews
        recipe.save()

@login_required
def edit_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    #redirect to displaying recipe if user is trying to edit someone else's recipe
    ingredient_data = list(recipe.list_ingredient.all())
    ingredients = [{"name": ingredient.ingredient, "quantity": ingredient.quantity, "units":ingredient.units} for ingredient in ingredient_data]
    if (recipe.user != request.user):
        return redirect('recipe', id=id)
    
    tags = recipe.tags
    tag_list = tags.split(",")
    form = RecipeForm(instance=recipe, initial={"tags":tag_list})
    context = {'form': form, 'recipe': recipe, 'ingredients':ingredients}

    return render(request, 'homey/editrecipe.html', context)

@login_required
def update_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    #redirect to displaying recipe if user is trying to edit someone else's recipe
    if (recipe.user != request.user):
        return redirect('recipe', id=id)

    tags = recipe.tags
    tag_list = tags.split(",")
    ingredient_data = list(recipe.list_ingredient.all())
    ingredients = [{"name": ingredient.ingredient, "quantity": ingredient.quantity, "units":ingredient.units} for ingredient in ingredient_data]
    if request.method == 'GET':
        context = { 'recipe': recipe, 'form': RecipeForm(instance=recipe, initial={'tags': tag_list}), 'ingredients':ingredients }
        return render(request, 'homey/editrecipe.html', context)

    recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe, initial={'tags': tag_list})
    try:
        ingredients_data = json.loads(request.POST.get('ingredients', '[]'))
    except json.JSONDecodeError:
        ingredients_data = []
    
    if not ingredients_data:
        recipe_form.add_error('list_ingredient', 'Please add at least one ingredient.')

    ingredients = [{"name": ingredient['name'], "quantity": ingredient['quantity'], "units":ingredient['units']} for ingredient in ingredients_data]
    if not recipe_form.is_valid():
        context = { 'recipe': recipe, 'form': recipe_form, 'ingredients':ingredients}
        return render(request, 'homey/editrecipe.html', context)

    if (len(request.FILES) > 0):
        pic = recipe_form.cleaned_data['picture']
        # print('Uploaded picture: {} (type={})'.format(pic, type(pic)))

        recipe.picture = recipe_form.cleaned_data['picture']
        recipe.content_type = recipe_form.cleaned_data['picture'].content_type
    recipe.save()
    recipe.list_ingredient.clear()

    for ing in ingredients_data:
        ingredient = IngredientItem(
            ingredient=ing['name'], quantity=float(ing['quantity']),
            units=ing['units']
        )
        ingredient.save()
        recipe.list_ingredient.add(ingredient)
    

    return display_recipe(request, id)
    
@login_required
def display_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    reviews = Review.objects.filter(recipe=recipe)
    profile = get_object_or_404(Profile, user=request.user)
    ingredient_data = list(recipe.list_ingredient.all())
    ingredients = [{"name": ingredient.ingredient, "quantity": ingredient.quantity, "units":ingredient.units} for ingredient in ingredient_data]


    #if user's own recipe, don't show bookmark button or review option, add edit button
    if (recipe.user == request.user):
        context = {'recipe': recipe, 'reviews': reviews, 'myrecipe': True, 'ingredients': ingredients}
        return render(request, 'homey/display_recipe.html', context)

    bookmarked = profile.bookmarked_recipes.filter(id=id).exists()

    try:
        Review.objects.get(recipe=recipe, user=request.user)
        context = { 'recipe': recipe, 'reviews': reviews, 'bookmarked': bookmarked, 'ingredients': ingredients}
        
        return render(request, 'homey/display_recipe.html', context)
    except Review.DoesNotExist:
        r = ReviewForm()
        context = { 'recipe': recipe, 'reviews': reviews, 'reviewform': r, 'bookmarked': bookmarked, 'ingredients': ingredients}

        return render(request, 'homey/display_recipe.html', context)

@login_required
def bookmark_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if (recipe.user == request.user):
        reviews = Review.objects.filter(recipe=recipe)
        context = {'recipe': recipe, 'reviews': reviews, 'myrecipe': True, 'error': "You cannot bookmark your own recipe."}
        return render(request, 'homey/display_recipe.html', context)
    profile = get_object_or_404(Profile, user=request.user)
    profile.bookmarked_recipes.add(recipe)
    profile.save()
    return display_recipe(request,id)


@login_required
def remove_bookmark_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if (recipe.user == request.user):
        reviews = Review.objects.filter(recipe=recipe)
        context = {'recipe': recipe, 'reviews': reviews, 'myrecipe': True, 'error': "You cannot bookmark/remove bookmarks of your own recipe."}
        return render(request, 'homey/display_recipe.html', context)
    profile = get_object_or_404(Profile, user=request.user)
    profile.bookmarked_recipes.remove(recipe)
    profile.save()
    return display_recipe(request,id)
    
@login_required
def profile_action(request):
    context={}
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'GET':
        context = { 'profile': profile, 'form': ProfileForm(instance=profile) }
        recipes = Recipe.objects.filter(user= request.user)
        context['recipes'] = recipes
        return render(request, 'homey/dashboard.html', context)
    
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context = { 'profile': profile, 'form': form }
        return render(request, 'homey/dashboard.html', context)


    profile.bio = form.cleaned_data['bio']
    profile.save()

    bookmarked_recipes = profile.bookmarked_recipes.all()

    context = {
        'profile': profile,
        'bookmarked_recipes': bookmarked_recipes,
        'form': ProfileForm(instance=profile),
        'message': 'Profile updated.'
    }
    recipes = Recipe.objects.filter(user= request.user)
    context['recipes'] = recipes

    return render(request, 'homey/dashboard.html', context)

@login_required
def grocery_list_view(request):
    if request.method == 'GET':
        g = GroceryForm()
        grocery_list = GroceryItem.objects.filter(user=request.user)
        context = { 'form': g, 'list': grocery_list }
        return render(request, 'homey/groceryList.html', context)

    grocery = GroceryItem(user=request.user)
    grocery_form = GroceryForm(request.POST, instance=grocery)
    if not grocery_form.is_valid():
        context = { 'form': grocery_form }
        return render(request, 'homey/groceryList.html', context)
    grocery_form.save()

    grocery_list = GroceryItem.objects.filter(user=request.user)
    context = { 'form': grocery_form, 'list': grocery_list}
    
    return render(request, 'homey/groceryList.html', context)

def create_grocery_item(request):
    if request.method == "GET":

        name = request.GET.get('name')
        quantity = request.GET.get('quantity', 1)
        units = request.GET.get('units', "items")

        initial_data = {
            'text': name,
            'quantity': float(quantity),
            'units': units,
        }
        form = GroceryForm(initial=initial_data)
        grocery_list = GroceryItem.objects.filter(user=request.user)
        return render(request, 'homey/groceryList.html', {'form': form, 'list': grocery_list})
    
    form = GroceryForm(request.POST)
    if form.is_valid():
        grocery_item = form.save()
        grocery_item.user = request.user  
        grocery_item.save()  

    grocery_list = GroceryItem.objects.filter(user=request.user)
    context = { 'form': form, 'list': grocery_list}
    return render(request, 'homey/groceryList.html', context)

@login_required
def completeItem(request, id):
    item = get_object_or_404(GroceryItem, id=id, user=request.user)
    item.complete = True
    item.save()
    return redirect('grocery-list') 

@login_required
def edit_item(request, id):
    # Get the grocery item to edit
    item = get_object_or_404(GroceryItem, id=id, user=request.user)

    if request.method == 'POST':
        form = GroceryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('grocery-list')  
    else:
        form = GroceryForm(instance=item)

    context = {'form': form, 'item': item}
    
    return render(request, 'homey/edit_grocerylist.html', context)

@login_required
def deleteItem(request, id):
    item = get_object_or_404(GroceryItem, id=id, user=request.user)
    item.delete()
    return redirect('grocery-list') 

@login_required
def clearList(request):
    GroceryItem.objects.filter(user=request.user).delete()
    return redirect('grocery-list')  


@login_required
def display_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    bookmarked_recipes = profile.bookmarked_recipes.all()
    context = { 'profile': profile,'form': ProfileForm(instance=profile), 'bookmarked_recipes': bookmarked_recipes }
    recipes = Recipe.objects.filter(user= request.user)
    context['recipes'] = recipes
    return render(request, 'homey/dashboard.html', context)


@login_required
def home(request):
    if 'picture' not in request.session:
            request.session['picture'] = request.user.social_auth.get(provider='google-oauth2').extra_data['picture']
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user, bio="", user_since=timezone.now())
        profile.save()  # Save profile to associate it with the user
    context = {}
    return render(request, 'homey/home.html', context)

def get_feed_events(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    events = []
    for event in FeedEvent.objects.all():
        events_info = {
            "time":event.time.isoformat(),
            "text":event.text,
            "temp_id":event.temp_id,
            "title":event.title,
            "user_first_name":event.user.first_name,
            "user_last_name":event.user.last_name,
            "event_id":event.id
        }
        events.append(events_info)

    response_json = json.dumps(events)

    return HttpResponse(response_json, content_type='application/json')

@login_required
def my_profile(request):
    print("in my profile", request)
    context = {}
    if 'picture' not in request.session:
            request.session['picture'] = request.user.social_auth.get(provider='google-oauth2').extra_data['picture']
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user, bio="", user_since=timezone.now())
        profile.save()  # Save profile to associate it with the user
    return render(request, 'homey/my_profile.html', context)

def home(request):
    return render(request, 'homey/home.html', {})
    