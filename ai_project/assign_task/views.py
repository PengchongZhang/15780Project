from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
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
    dev_set = set()
    for i in range(len(vote)):
        if vote[i] < 0 or vote[i] >= len(vote) or vote[i] in dev_set:
            return False
        dev_set.add(vote[i])
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
        expert_weight = float(post_data['expert-weight'])
        vote_order = []
        estimate = []
        for i in range(developer_num):
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
            dev_vote = [int(dev_vote_str[j])-1 for j in range(developer_num)]
            if not check_valid_vote(dev_vote):
                return None
            vote_order.append(dev_vote)
        return developer_num, task_num, expert_weight, estimate, vote_order
    except ValueError:
        return None


def format_output(mix_est, dev_workload):
    for i in range(len(mix_est)):
        mix_est[i] = round(mix_est[i], 2)
    assignment = []
    for i in range(len(dev_workload)):
        tasks = []
        for j in range(len(dev_workload[i])):
            if dev_workload[i][j] > 1e-12:
                task = {'task_id': j+1, 'proportion': round(dev_workload[i][j], 2)}
                tasks.append(task)
        dev_assign = {'dev_id': i + 1, 'tasks': tasks}
        assignment.append(dev_assign)
    context = {'estimate': mix_est, 'assignment': assignment}
    return context


def solve_assignment(request):
    """
    api for solving the task assignment problem
    :param request:
    :return:
    """
    if request.method == 'POST':
        input_data = extract_input(request.POST)
        if input_data is None:
            return JsonResponse({'valid': False})
        else:
            solver = Partition()
            print(input_data)
            expert, est, workload = solver.handler(input_data[0], input_data[1],
                                                   input_data[2], input_data[3], input_data[4])
            context = format_output(est, workload)
            context['expert'] = expert + 1
            context['valid'] = True
            context['developer_number'] = input_data[0]
            context['task_number'] = input_data[1]
            context['expert_weight'] = input_data[2]
            return JsonResponse(context)