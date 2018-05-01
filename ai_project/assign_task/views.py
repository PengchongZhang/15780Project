from django.shortcuts import render
from django.http import HttpResponse
from .partition import Partition
import json


# Create your views here.
# render the index page
def index(request):
    return HttpResponse('This is the index page.')


# api for solving the task assignment problem
def solve_assignment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(int(data['data']['tasks'][0]['index']))
        return HttpResponse('solve partition problem')
