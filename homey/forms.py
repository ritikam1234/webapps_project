from django import forms
from django.contrib.auth.models import User
from homey.models import Recipe, Review, Profile, GroceryItem, CreateEvent, IngredientItem
from django.contrib.auth import authenticate
from django.forms import modelformset_factory
MAX_UPLOAD_SIZE = 2500000
import datetime

class RecipeForm(forms.ModelForm):
    TAG_CHOICES = (("tree nuts", "tree nuts"), 
                   ( "peanuts",  "peanuts"), 
                   ("eggs", "eggs"),("soy", "soy"), 
                   ("fish/shellfish", "fish/shellfish"), 
                   ("wheat", "wheat"), 
                   ("vegetarian", "vegetarian"),
                   ("vegan","vegan"),
                   ("gluten-free", "gluten-free"),
                   ("kosher", "kosher"),
                   ("keto", "keto"))
    tags = forms.MultipleChoiceField(choices=TAG_CHOICES, required=False, widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = Recipe
        exclude = (
            'user',
            'creation_time',
            'average_rating',
            'content_type'
        )
        widgets = {
            'steps': forms.Textarea()
        }
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tag_string = ",".join(tags)
        return tag_string
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if Recipe.objects.filter(id=self.instance.id).exists():
            if picture == self.instance.picture:
                return self.instance.picture
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'picture')
    def clean(self):
        cleaned_data = super().clean()
        recipe = cleaned_data.get('recipe')
        user = cleaned_data.get('user')
        try:
            Review.objects.get(recipe=recipe, user=user)
            raise forms.ValidationError("You can only review each recipe once.")
        except Review.DoesNotExist:
                return cleaned_data

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio',)
        widgets = {
            'bio': forms.Textarea(attrs={'id': 'id_bio_input_text', 'rows': '3', 'text-align': 'center'}),
        }

        labels = {
            'bio': "",
        }
    
class CreateEventForm(forms.ModelForm):
    class Meta:
        model = CreateEvent
        fields = ['title', 'summary', 'date', 'start', 'end', 'attendees', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                "id": "title",
                "placeholder": "Title",
                "align": "center"
            }),
            'summary': forms.Textarea(attrs={
                "id": "summary",
                "placeholder": "Description",
                "align": "center",
                "cols":19,
                "rows":5
            }),
            'date': forms.TextInput(attrs={
                "id": "date",
                "placeholder": "YYYY-MM-DD",
                "align": "center"
            }),
            'start': forms.TextInput(attrs={
                "id": "start",
                "placeholder": "Start time ",
                "align": "center"
            }),
            'end': forms.TextInput(attrs={
                "id": "end",
                "placeholder": "End time ",
                "align": "center"
            }),
            'location': forms.TextInput(attrs={
                "id": "location",
                "placeholder": "Location",
                "align": "center"
            }),
            'attendees': forms.TextInput(attrs={
                "id": "attendees",
                "placeholder": "Your homey's email ID",
                "align": "center"
            }),
            'eventType': forms.TextInput(attrs={
                "id": "eventType",
                "placeholder": "default",
                "align": "center"
            }),
        }
        labels = {
            'title': "",
            'summary':"",
            'date': "",
            'end' : "",
            'start' : "",
            'attendees': "",
            'location':"",
            'eventlink':""
        }
    def clean_date(self):
        date =  self.cleaned_data['date']
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except:
            raise forms.ValidationError('Enter a valid date! Eg. 2024-11-23')
        return date

    def clean_start(self):
        start = self.cleaned_data['start']
        try:
            datetime.datetime.strptime(start, '%H:%M%p')
        except:
            raise forms.ValidationError('Enter a valid time: Eg. 5:00PM')
        return start
    
    def clean_end(self):
        end = self.cleaned_data['end']
        try:
            datetime.datetime.strptime(end, '%H:%M%p')
        except:
            raise forms.ValidationError('Enter a valid time! Eg. 5:00PM')
        return end



class GroceryForm(forms.ModelForm):
    class Meta:
        model = GroceryItem
        fields = ['text', 'quantity', 'units']
        widgets = {
            'text': forms.TextInput(attrs={
                "id": "myInput",
                "placeholder": "Add an item to your grocery list...",
                "align": "center"
            }),
            'quantity': forms.NumberInput(attrs = {
                "align": "center",
                "placeholder": "Add quantity for your item"
            }),
            'units': forms.TextInput(attrs = {
                "align": "center",
                "placeholder": "Add units"
            })
        }
        labels = {
            'text': "",
            'quantity': 0,
            'units' : ""
        }