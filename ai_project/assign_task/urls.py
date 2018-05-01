from django.urls import path

from .views import *

urlpatterns = [
    # index view
    path('', index, name='index'),
    # api for solving task assignment
    path('assignment/input', solve_assignment, name='solve'),
]