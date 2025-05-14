from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# class RecipeTag(models.Model):
#     tag = models.CharField()

#     def __str__(self):
#         return self.tag



class CreateEvent(models.Model):
    title = models.CharField(max_length = 255, default = '')
    summary = models.TextField(blank = True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_event")
    location = models.CharField(max_length = 30)
    date = models.CharField(max_length = 255)
    start = models.CharField(max_length = 10)
    end = models.CharField(max_length = 10)
    attendees = models.CharField(max_length = 30, blank = True)
    eventlink = models.CharField(max_length = 30, default = "https://calendar.google.com")
    eventType = models.CharField(max_length = 30, default = 'default')

class IngredientItem(models.Model):
    ingredient = models.CharField(max_length = 40)
    quantity = models.FloatField(default=1, validators=[MinValueValidator(0)])
    units = models.CharField(max_length=40, default="items")
    

    def __str__(self):
        return self.ingredient

class Recipe(models.Model):
    title =  models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_recipes")
    list_ingredient = models.ManyToManyField(IngredientItem, blank=True)
    average_rating = models.FloatField(default=0.0)
    creation_time = models.DateTimeField()
    steps = models.TextField()
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, blank=True)

    

    # ingredients = models.JSONField(default=list)
    #need to figure out how to clean the ingredients to convert to jsonfield of list of strings from the form?

    # tags = models.ManyToManyField(RecipeTag, default=None)
    tags = models.CharField(max_length=10000, default="")
    # TAG_CHOICES = {"tree nuts", "peanuts", "eggs", "soy", "fish/shellfish", "wheat", "vegetarian", "vegan", "gluten-free", "kosher", "keto"}
    # tags = MultiSelectField(choices=TAG_CHOICES)

    def get_ingredients(self):
        return [
            {
                "name": ingredient.ingredient,
                "quantity": ingredient.quantity,
                "units": ingredient.units,
            }
            for ingredient in self.list_ingredient.all()
        ]



class GroceryItem(models.Model):
    text = models.CharField(max_length = 40)
    quantity = models.FloatField(default=1, validators=[MinValueValidator(0)])
    units = models.CharField(max_length=40, default="items")
    complete = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grocery_items")

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="review_creators")
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, related_name="reviews")
    RATING_CHOICES = [
        (1, '1 star'),
        (2, '2 star'),
        (3, '3 star'),
        (4, '4 star'),
        (5, '5 star'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)

class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    user_since = models.DateTimeField()
    bookmarked_recipes = models.ManyToManyField(Recipe)
#added

# Create your models here.
class Event(models.Model):
    summary = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class FeedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time = models.DateTimeField()
    text = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    temp_id = models.IntegerField()
    #recipe = models.OneToOneField(Recipe, on_delete=models.PROTECT, related_name="recipe_link", blank=True)
