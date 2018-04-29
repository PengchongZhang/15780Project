from django.shortcuts import render
from django.http import HttpResponse
from .partition import Partition


# Create your views here.
def index(request):
    return HttpResponse('This is the index page.')


def get_result(request):
    return HttpResponse('get result for partition problem')


def solve_partition(request):
    if request.method == 'POST':
        return HttpResponse('solve partition problem')
