import copy as cp
from cvxpy import *
import numpy as np
# from .task import *
from heapdict import heapdict


class Task:
    index = 0
    estVal = 0
    need_save = True

    def __init__(self, index, estVal):
        self.index = index
        self.estVal = estVal


#
# Create obj for Partition
# Run the hander(xx) function
class Partition:
    '''
    Calculate the index of the expert based on Bonda vote algorithm
    Pass
    '''

    def bondaVote(self, twoDList):
        result = [0 for i in range(len(twoDList[0]))]
        for oneDList in twoDList:
            vote = len(oneDList)
            for num in oneDList:
                result[num] += vote
                vote -= 1
        return result.index(max(result))

    '''
    Calculate the average workload for each developer
    Pass
    '''

    def calAverage(self, E_mix, N):
        return sum(E_mix) / N

    '''
    Calculate E_mix based on all the dev and expert estimation value
    @Param:
    E_dev: 2-D array N x M
    expertIdx, expertWeight
    Pass
    '''

    def calEstimationMix(self, E_dev, expertIdx, expertWeight):
        result = [0] * len(E_dev[0])

        N = len(E_dev)
        otherWeight = (1 - expertWeight) / (N - 1)

        for i in range(N):
            if i == expertIdx:
                zipped = zip(result, [x * expertWeight for x in E_dev[i]])
                result = [sum(x) for x in zipped]
            else:
                zipped = zip(result, [x * otherWeight for x in E_dev[i]])
                result = [sum(x) for x in zipped]
        return result

    '''
    task object: index(original), estimate value E_mix[index]
    put all task objects into a list, sorted by E_mix[index]
    @:return: a list of task objects (sorted)
    Pass
    '''

    def sortTask(self, E_mix):
        task_objects = []
        M = len(E_mix)
        for i in range(M):
            task_objects.append(Task(i, E_mix[i]))
        task_objects = sorted(task_objects, key=lambda task: task.estVal)
        return task_objects

    '''
    Partition the original tasks into subtasks based on avg
    @:param: sorted task_object list based on estimation value
    @:return: a dict: key: original task index, value: a list of subTasks est
    checking
    '''

    def partition(self, avg, task_objects):
        M = len(task_objects)
        dict = {}
        for i in range(M):  # M keys, list as value
            dict[i] = []

        left = 0
        right = M - 1
        while left < right:
            E_need = avg - task_objects[left].estVal
            if E_need == 0:
                dict[task_objects[left].index].append(avg)
                left += 1
            elif E_need < 0:  # left task needed be partitioned
                dict[task_objects[left].index].append(avg)
                task_objects[left].estVal -= avg
            else:
                if task_objects[left].need_save:
                    dict[task_objects[left].index].append(task_objects[left].estVal)
                    task_objects[left].need_save = False
                if task_objects[right].estVal >= E_need:  # right val can be remained
                    dict[task_objects[right].index].append(E_need)
                    task_objects[right].estVal -= E_need
                    left += 1
                else:  # left val can not be filled with right val
                    dict[task_objects[right].index].append(task_objects[right].estVal)
                    right -= 1
                    task_objects[left].estVal += task_objects[right].estVal
        return dict

    '''
    Update the E_dev to E_dev_new, E_mix to E_mix_new
    @:param: E_mix: the estimation value for each original task => 1 x M
    @:param: dict: key: original task index   value: list of estimation value for sub tasks
    @:param: E_dev: the estimation value for each original task for each developer => N x M
    @:return:E_dev_new: the estimation value for partitioned tasks # N * subTasksNum
    @:return: E_mix_new: the estimation value for partioned tasks
    @:return: Task_prop: a list of subTask size, each element: [subTask id, subTask Proportion]
    '''

    def update(self, E_mix, E_dev, dict):
        N = len(E_dev)
        M = len(E_mix)

        E_dev_new = []
        E_mix_new = []
        Task_prop = []  # size subTask, each is a list [taskId, prop to this taskId]

        for i in range(N):
            E_dev_new.append([])  # N * numOfAllsubtasks

        for key in range(len(dict)):
            # value is a list corresponding to the key (taskIdx)
            value = dict[key]
            for e in value:
                E_mix_new.append(e)
                Task_prop.append([key, e / E_mix[key]])
                for i in range(N):
                    val = E_dev[i][key] * (e / E_mix[key])
                    E_dev_new[i].append(val)

        return E_mix_new, E_dev_new, Task_prop

    '''
    Calculate the result based on Integer Programming
    @:param: E_dev_new (the dev estimation value for each subTasks) N x subTasks Size
    @:param: E_mix_new
    @:return assigned tasks for each user
    '''

    def IPsolver(self, E_dev_new, E_mix_new, avg):
        N = len(E_dev_new)
        subTask = len(E_dev_new[0])

        x = Variable(N, subTask)
        # Create two constraints.
        constraints = [0 <= x, x <= 1]  # x == 0 || x == 1

        E_mix_new_arr = np.array(E_mix_new)
        E_mix_new_arr = E_mix_new_arr.reshape(subTask, 1)

        # guarantee each developer get the same estimated work based on E_mix_new
        constraints += [x * E_mix_new_arr == avg]

        # guarantee each col of x sum to 1
        col_sums = sum_entries(x, axis=0)  # Has size (1, subTask)
        constraints += [col_sums == 1]

        # convert E_dev_new to matrix
        E_dev_new_arr = np.array(E_dev_new)

        target = mul_elemwise(E_dev_new_arr, x)
        row_sums = sum_entries(target, axis=1)
        obj = Minimize(sum_entries(row_sums))

        # Form and solve problem.
        prob = Problem(obj, constraints)
        result = prob.solve()

        # Integer Programming
        # push the original solution to the frontier
        frontier = heapdict()
        frontier[tuple(constraints)] = result

        while len(frontier) > 0:
            # step 1: pop the item with minimum f_value
            constraints, value = frontier.popitem()

            # avoid None value, reassign x by solving the same problem
            target = mul_elemwise(E_dev_new_arr, x)
            row_sums = sum_entries(target, axis=1)
            obj = Minimize(sum_entries(row_sums))

            # Form and solve problem.
            prob = Problem(obj, list(constraints))
            prob.solve()

            # step 2: check: find the first index in matrix that is not an integer
            # print('top: x value is ', x.value)
            r, c = self.helper(N, subTask, x)
            if r == -1:
                return self.transferX(N, subTask, x), value
            else:
                # step 3: add the constraint and do dfs
                new_constraints_zero = list(constraints)
                new_constraints_zero += [x[r, c] == 0]
                target = mul_elemwise(E_dev_new_arr, x)
                row_sums = sum_entries(target, axis=1)
                obj = Minimize(sum_entries(row_sums))

                # Form and solve problem.
                prob = Problem(obj, new_constraints_zero)
                result = prob.solve()
                if prob.status == "optimal":
                    frontier[tuple(new_constraints_zero)] = result

                new_constraints_one = list(constraints)
                new_constraints_one += [x[r, c] == 1]
                target = mul_elemwise(E_dev_new_arr, x)
                row_sums = sum_entries(target, axis=1)
                obj = Minimize(sum_entries(row_sums))

                # Form and solve problem.
                prob = Problem(obj, new_constraints_one)
                result = prob.solve()
                if prob.status == "optimal":
                    frontier[tuple(new_constraints_one)] = result
        return self.twoDArray(N, subTask), 0

    '''
    helper function: find the smallest index whose value is not an integer
    '''

    def helper(self, row, col, x):
        for r in range(row):
            for c in range(col):
                if 0.005 <= x.value[r, c] <= 0.995:  # not an integer
                    return r, c
        return -1, -1

    '''
    Transfer x variable to 2d array
    '''

    def transferX(self, row, col, x):
        array = []
        for r in range(row):
            array.append([])
            for c in range(col):
                array[r].append(x.value[r, c])
        return array

    '''
    Main function handling whole logic
    DevepolerNum: N
    TaskNum: M
    ExpertWeight: p
    devEstVal: 2D array, N x M
    devExpRank: 2D array, N x N
    '''

    def handler(self, developerNum, TaskNum, expertWeight, devEstVal, devExpRank):
        # corner case:
        if developerNum == 1:
            return devEstVal, devEstVal

        # Step 1: vote for expert
        expertIdx = self.bondaVote(devExpRank)

        # Step 2: calculate the E_mix
        E_mix = self.calEstimationMix(devEstVal, expertIdx, expertWeight)

        # Step 3: partition the M tasks into feasible subTasks for IP
        avg = self.calAverage(E_mix, developerNum)
        task_objects = self.sortTask(E_mix)
        dict = self.partition(avg, task_objects)

        # Step 4: update the E_mix and E_dev to E_mix_new and E_dev_new based on the subTasks
        E_mix_new, E_dev_new, Task_prop = self.update(E_mix, devEstVal, dict)

        # return E_dev_new, E_mix_new

        # Step 5: Solve the IP and return the task assignment and task proportion

        result_twoDarray, optimal_value = self.IPsolver(E_dev_new, E_mix_new, avg)
        result = self.cal_assignment(developerNum, TaskNum, result_twoDarray, Task_prop)
        print('result is ', result)
        return expertIdx, E_mix, result

    '''
    Test use: print each value in a two d array
    '''

    def cal_assignment(self, N, M, twoDarray, Task_prop):
        dev_assignament = [[0 for y in range(M)] for x in range(N)]

        row = len(twoDarray)  # developer idx
        col = len(twoDarray[0])  # subTask

        for devIdx in range(row):
            for subTask in range(col):
                if twoDarray[devIdx][subTask] > 0.995:  # do this subTask for this devIdx
                    dev_assignament[devIdx][Task_prop[subTask][0]] += Task_prop[subTask][1]
        return dev_assignament

    '''
    Helper function for testing
    '''

    def twoDArray(self, userNum, taskNum):
        # w, h = 8, 5
        row, col = userNum, taskNum
        matrix = [[0 for y in range(col)] for x in range(row)]
        return matrix


if __name__ == '__main__':
    obj = Partition()
    developerNum = 2
    TaskNum = 4
    expertWeight = 0.8

    devEstVal = []
    for i in range(developerNum):
        devEstVal.append([])

    devEstVal[0] = [1, 12, 1, 3]
    devEstVal[1] = [1, 15, 1, 5]

    devExpRank = []
    for i in range(developerNum):
        devExpRank.append([])
    devExpRank[0] = [0, 1]
    devExpRank[1] = [0, 1]

    obj.handler(developerNum, TaskNum, expertWeight, devEstVal, devExpRank)