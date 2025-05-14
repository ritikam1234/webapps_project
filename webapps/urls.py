"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from homey import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.profile_action, name='my-profile'),
    path('', views.home, name='home'),
    path('update-dashboard', views.profile_action, name='update-dashboard'),
    path('dashboard', views.display_dashboard, name='dashboard'),
    path('new-recipe', views.post_recipe, name="new-recipe"),
    path('edit-recipe/<int:id>', views.edit_recipe, name="edit-recipe"),
    path('update-recipe/<int:id>', views.update_recipe, name="update-recipe"),
    path('new-review/<int:id>', views.post_review, name="new-review"),
    path('homey/get-recipes', views.get_recipes),
    path('homey/get-events', views.get_feed_events, name="get-events"),
    path('homey/get-reviews/<int:recipeid>', views.get_reviews),
    path('recipebook', views.recipe_stream, name='recipe-stream'),
    path('recipe/<int:id>', views.display_recipe, name='recipe'),
    path('bookmark/<int:id>', views.bookmark_recipe, name='bookmark'),
    path('unbookmark/<int:id>', views.remove_bookmark_recipe, name='unbookmark'),
    path('reviewpicture/<int:id>', views.get_review_picture, name='review-picture'),
    path('recipepicture/<int:id>', views.get_recipe_picture, name='recipe-picture'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout', views.logout, name='logout'),
    path('calendar', views.fetch_events, name = "calendar_events"), #added
    path('calendar', views.CalendarView.as_view(), name = "calendar_events"), #added
    path('pubcal', views.showpubliccalendar, name = "pubcal"),
    path('my_profile', views.my_profile, name = 'my_profile'),
    path('grocery-list/', views.grocery_list_view, name="grocery-list"),  # Main view for list and form handling
    path('delete-item/<int:id>/', views.deleteItem, name="deleteitem"),    # Delete specific item
    path('complete-item/<int:id>/', views.completeItem, name="complete"),  # Mark specific item as complete
    path('clear-list/', views.clearList, name="clearlist"),  
    path('edit-grocery-item/<int:id>', views.edit_item, name="edititem"),
    path('otherprofile/<int:id>', views.other_profile_action, name = 'other_profile'),
    path('add-to-calendar/<int:id>', views.addtocalendar, name="add-to-calendar"),
    path('addgrocerytocalendar', views.addgrocerytocalendar, name = "addgrocerytocalendar"),
    path('grocery-item/create/', views.create_grocery_item, name='create_grocery_item'),
]