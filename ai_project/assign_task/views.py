from django.shortcuts import render
from django.http import HttpResponse
from django.http import QueryDict
from .partition import Partition
import json


# Create your views here.
# render the index page
def index(request):
    return render(request, 'index.html')


def check_valid_est(est):
    for i in range(len(est)):
        if est[i] < 0:
            return False
    return True


def check_valid_vote(vote):
    index = set()
    for i in range(len(vote)):
        if vote[i] < 1 or vote[i] > len(vote) or vote[i] in index:
            return False
        index.add(vote[i])
    return True


def extract_input(post_data):
    """
    extract input from the post data
    :param post_data:
    :return:
    """
    try:
        task_num = int(post_data['task-number'])
        developer_num = int(post_data['developer-number'])
        vote_order = []
        estimate = []
        for i in range(task_num):
            est_key = 'est-dev{}'.format(i)
            vote_key = 'vote-dev{}'.format(i)
            dev_est_str = post_data[est_key].strip().replace(' ', '').split(',')
            dev_vote_str = post_data[vote_key].strip().replace(' ', '').split(',')
            if len(dev_vote_str) != developer_num or len(dev_est_str) != task_num:
                return None
            dev_est = [float(dev_est_str[j]) for j in range(task_num)]
            if not check_valid_est(dev_est):
                return None
            estimate.append(dev_est)
            dev_vote = [int(dev_vote_str[j]) for j in range(developer_num)]
            if not check_valid_vote(dev_vote):
                return None
            vote_order.append(dev_vote)
        return task_num, developer_num, estimate, vote_order
    except ValueError:
        return None


def solve_assignment(request):
    """
    api for solving the task assignment problem
    :param request:
    :return:
    """
    if request.method == 'POST':
        input_data = extract_input(request.POST)
        return HttpResponse('solve partition problem')
