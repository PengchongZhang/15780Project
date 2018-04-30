import copy as cp
from cvxpy import *
import numpy as np
from .Task import Task

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
		sorted(task_objects, key=lambda task: task.estVal)
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
			elif E_need < 0: # left task needed be partitioned
				dict[task_objects[left].index].append(avg)
				task_objects[left].estVal -= avg
			else: # need partition right
				if len(dict[task_objects[left].index]) == 0:
					dict[task_objects[left].index].append(task_objects[left].estVal)
				if task_objects[right].estVal >= E_need:  # right val can be remained
					dict[task_objects[right].index].append(E_need)
					task_objects[right].estVal -= E_need
					left += 1
				else: # left val can not be filled with right val
					dict[task_objects[right].index].append(task_objects[right].estVal)
					right -= 1
					task_objects[left].estVal += task_objects[right].estVal
		return dict
	
	
	# for the original tasks whose estimate value is not equal to avg
	# we partition the tasks into subtasks using greedy method
	# return a list of new sub task
	# [T1, T2, T31, T32, T41, T42]
	'''
	Deterministic method to partition original tasks into subtasks
	using greedy algorithm
	@Param:
	avg: the average value for E_mix
	E_mix: 1-D array, the mixed estimation value vector (M,)
	E_dev: 2-D array, the estimation for each developer: N x M
	'''
	# input should be modified to sorted task object
	# def partitionOld(self, avg, E_mix):
	# 	# key: originalTaskIndex, value: list of estimation value for subTasks
	# 	dict = {}
	# 	for i in range(len(E_mix)):  # M keys, list as value
	# 		dict[i] = []
	#
	# 	left = 0
	# 	right = len(E_mix) - 1
	#
	# 	# reserve the original E_mix
	# 	tmp = cp.deepcopy(E_mix)
	# 	E_mix.sort()
	# 	while left < right:
	# 		if len(dict[right]) == 0:
	# 			dict[right].append(avg)
	#
	# 		if E_mix[left] == avg:
	# 			dict[left].append(avg)
	# 			left += 1
	# 		else:
	# 			if len(dict[left]) == 0:
	# 				dict[left].append(E_mix[left])
	# 			E_need = avg - E_mix[left]
	# 			E_aval = E_mix[right] - avg
	#
	# 			if E_need <= E_aval:
	# 				dict[right].append(E_need)
	# 				E_mix[right] -= E_need
	# 				left += 1
	# 			else:
	# 				dict[right].append(E_aval)
	# 				E_mix[left] += E_aval
	# 				right -= 1
	# 	return dict, tmp
	
	'''
	Update the E_dev to E_dev_new, E_mix to E_mix_new
	E_mix: the estimation value for each original task => 1 x M
	dict: a hashmap: key: original task index   value: list of estimation value for sub tasks
	E_dev: the estimation value for each original task for each developer => N x M
	E_dev_new: the estimation value for partitioned tasks # N * subTasksNum
	'''
	
	def update(self, E_mix, E_dev, dict):
		N = len(E_dev)
		
		E_dev_new = []
		E_mix_new = []
		
		for i in range(N):
			E_dev_new.append([])  # N * numOfAllsubtasks
		
		for key in range(len(dict)):
			# value is a list corresponding to the key (taskIdx)
			value = dict[key]
			for e in value:
				E_mix_new.append(e)
				for i in range(N):
					val = E_dev[i][key] * (e / E_mix[key])
					E_dev_new[i].append(val)
		return E_mix_new, E_dev_new
	
	
	
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
		constraints = [0 <= x, x <= 1]# x == 0 || x == 1
		
		E_mix_new_arr = np.array(E_mix_new)
		E_mix_new_arr = E_mix_new_arr.reshape(subTask, 1)
		
		# guarantee each developer get the same estimated work based on E_mix_new
		constraints += [x * E_mix_new_arr == avg]
		
		# guarantee each col of x sum to 1
		col_sums = sum_entries(x, axis=0)  # Has size (1, subTask)
		constraints += [col_sums == 1]
		
		# convert E_dev_new to matrix
		E_dev_new_arr = np.array(E_dev_new)
		print(E_dev_new_arr.shape)
		
		
		
		target = mul_elemwise(E_dev_new_arr, x)
		row_sums = sum_entries(target, axis=1)
		obj = Minimize(sum_entries(row_sums))
		
		# Form and solve problem.
		prob = Problem(obj, constraints)
		prob.solve()
		print("status:", prob.status)
		print("optimal value", prob.value)
		

	'''
	Main function handling whole logic
	DevepolerNum: N
	TaskNum: M
	ExpertWeight: p
	devEstVal: 2D array, N x M
	devExpRank: 2D array, N x N
	'''
	
	def handler(self, developerNum, TaskNum, expertWeight, devEstVal, devExpRank):
		# Step 1: vote for expert
		expertIdx = self.bondaVote(devExpRank)
		
		# Step 2: calculate the E_mix
		E_mix = self.calEstimationMix(devEstVal, expertIdx, expertWeight)
		
		# Step 3: partition the M tasks into feasible subTasks for IP
		avg = self.calAverage(E_mix, developerNum)
		
		task_objects = self.sortTask(E_mix)
		
		
		self.partition(avg, task_objects)
		
		
		
		dict, E_mix = self.partition(avg, E_mix, developerNum)
		
		# Step 4: update the E_mix and E_dev to E_mix_new and E_dev_new based on the subTasks
		E_mix_new, E_dev_new = self.update(E_mix, devEstVal, dict)
		
		# for testing
		#return E_mix_new, E_dev_new
	
	
		self.test()
		# Step 5: Solve the IP and return the task assignment and task proportion
		self.IPsolver(E_dev_new, E_mix_new, avg)
	
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
	TaskNum = 3
	expertWeight = 0.8
	
	devEstVal = []
	for i in range(developerNum):
		devEstVal.append([])
	# devEstVal[0] = [6, 5, 2]
	# devEstVal[1] = [3, 4, 5]
	devEstVal[0] = [1, 1, 1]
	devEstVal[1] = [1, 1, 1]
	
	devExpRank = []
	for i in range(developerNum):
		devExpRank.append([])
	devExpRank[0] = [1, 0]
	devExpRank[1] = [1, 0]
	
	obj.handler(developerNum, TaskNum, expertWeight, devEstVal, devExpRank)