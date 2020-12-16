import sys
import random
import operator
import numpy as np
from VerbosePrint import setVerbosity, printV
from branch_v5 import branch_v5
from copy import copy
from operator import itemgetter
from collections import deque

# helper function for v3 gen
def nearest_idx(array, value):
	array = np.asarray(array)
	return (np.abs(array - value)).argmin()

# helper function for v4 gen
def makeBranchVector(target_taken_rate, target_trans_rate):
	orig_target_trans_rate = target_trans_rate
	slow_vector = False
	if (target_trans_rate < 1/21.0): # Generate a "slow vector", which only advances once every 32 iterations
		slow_vector = True
		target_trans_rate = min(target_trans_rate * 32, 1)

	target_transitions = 2 * int((target_trans_rate * 16) + 0.5) # Even integer between 0 and 32
	target_ones = int((target_taken_rate * 32) + 0.5)

	### Phase 1: Generate bit vector to match target transition rate

	bit_values = [1] # Bit vectors will normally start with 1
	trans_distance = 0 # Bits assigned since previous transition
	remaining_transitions = target_transitions - 1 # Non-constant vectors normally end in 0, causing a transition when they restart (since the first bit is 1)

	for bit in range(1, 32): # Iterate over remaining bits
		trans_distance += 1
		if ((remaining_transitions > 0) and (trans_distance >= ((32 - bit) / float(remaining_transitions)))): # Transition for next bit
			bit_values.append(1 - bit_values[-1])
			trans_distance = 0;
			remaining_transitions -= 1;
		else: # Don't transition
			bit_values.append(bit_values[-1])
		bit += 1
	printV(4, "Before taken rate refiniment: " + str(bit_values))

	### Phase 2: Refine bit vector to match target taken rate, without affecting transition rate

	initial_taken_rate = bit_values.count(1) / float(32)
	if (initial_taken_rate - 0.5 > target_taken_rate): # Can give a better approximation, especially for extremely low transition rates
		for bit in range(0, 32):
			bit_values[bit] = 1 - bit_values[bit]

	running_ones_count = bit_values.count(1)
	for count in range(0, 320): # This needs to run through the whole vector several times - 320 is probably overkill, though
		if (running_ones_count == target_ones):
			break
		bit = (count * 17) % 32 # Reduces clustering of 0s or 1s vs. traversing the list linearly
		if bit == 0 or bit == 31: # Don't change the value of the first or last bit, maintaining a transition where the vector restarts
			continue
		if bit_values[bit-1] != bit_values[(bit+1)%32]: # Bit lies on a transition, and toggling its value will not add or remove any transitions
			if ((running_ones_count < target_ones) and (bit_values[bit] == 0)):
				bit_values[bit] = 1
				running_ones_count += 1
			elif ((running_ones_count > target_ones) and (bit_values[bit] == 1)):
				bit_values[bit] = 0
				running_ones_count -= 1
	printV(4, "After taken rate refinement: " + str(bit_values))

	### Phase 3: Interleave "transition groups" (string of 1s followed by string of 0s, or vice-versa) to improve distribution of transitions

	split_val = bit_values[0] # Value that indicates a transition group boundary
	split_next = False # Start a new group when split_val is next encountered
	transition_groups = []
	group = [bit_values[0]]
	for bit_pos in range(1, 32):
		if (bit_values[bit_pos] == split_val):
			if split_next:
				transition_groups.append(copy(group))
				group = [bit_values[bit_pos]]
				split_next = False
			else:
				group.append(bit_values[bit_pos])
		else:
			group.append(bit_values[bit_pos])
			split_next = True
	transition_groups.append(copy(group)) # Last group
	del group
	printV(4, "Isolated transition groups: " + str(transition_groups))

	bit_pos = 0
	while(len(transition_groups) >= 2): # Interleave groups
		for element in transition_groups[0]:
			bit_values[bit_pos] = element
			bit_pos += 1
		for element in transition_groups[-1]:
			bit_values[bit_pos] = element
			bit_pos += 1
		del transition_groups[0]
		del transition_groups[-1]
	if (len(transition_groups) == 1): # Last group if odd number of groups
		for element in transition_groups[0]:
			bit_values[bit_pos] = element
			bit_pos += 1
	del transition_groups
	printV(4, "Final (interleaved) array: " + str(bit_values))

	transition_count = 0
	for i in range(0, 32):
		if (bit_values[i-1] != bit_values[i]):
			transition_count += 1

	if slow_vector:
		printV(4, "SLOW VECTOR")
		printV(4, "Target transition rate: " + str(orig_target_trans_rate))
		actual_trans_rate = transition_count / float(32*32)
		printV(4, "Actual transiton rate: " + str(actual_trans_rate))
	else:
		printV(4, "FAST VECTOR")
		printV(4, "Target transition rate: " + str(orig_target_trans_rate))
		actual_trans_rate = transition_count / float(32)
		printV(4, "Actual transiton rate: " + str(actual_trans_rate))
	if (orig_target_trans_rate != 0.0):
		printV(4, "Absoulte percent error: " + str(abs(orig_target_trans_rate - actual_trans_rate) * 100 / orig_target_trans_rate) + "%")
	else:
		printV(4, "Absolute percent error: NaN%")
	printV(4, "Target taken rate: " + str(target_taken_rate))
	actual_taken_rate = bit_values.count(1) / float(32)
	printV(4, "Actual taken rate: " + str(actual_taken_rate))
	if (target_taken_rate != 0.0):
		printV(4, "Absolute percent error: " + str(abs(target_taken_rate - actual_taken_rate) * 100 / target_taken_rate) + "%")
	else:
		printV(4, "Absolute percent error: NaN%")

	### Phase 4: Convert list to bit vector

	if slow_vector:
		bit_vector_list = bit_values + [0]*32
	else:
		bit_vector_list = [0]*32 + bit_values

	bit_vector = 0
	for bit in bit_vector_list:
		bit_vector = (bit_vector << 1) | bit

	printV(3, "Bit vector for branch: " + "{0:#0{1}x}".format(bit_vector,18))
	return bit_vector


#non-shuffling helper function for v4 gen
def populate_branch_vectors(bit_vector,count):
        populated_vectors = []
        for v in range(count):
                populated_vectors.append(bit_vector)
        return populated_vectors


# helper function for v4 gen
def makeVectorShuffles(bit_vector, count):	
	if bit_vector == 0:
		return [0]*count

	bit_values = []
	for bit_idx in range(64):
		bit_values.insert(0, bit_vector & 0x1)
		bit_vector >>= 1

	if all(bit == 0 for bit in bit_values[0:32]):
		slow_vector = False
		bit_values = bit_values[32:64]
	elif all(bit == 0 for bit in bit_values[32:64]):
		slow_vector = True
		bit_values = bit_values[0:32]
	else:
		sys.error("Malformed bit vector in makeVectorShuffles")
		exit()

	base_trans_count = 0
	for bit_idx in range(32):
		if bit_values[bit_idx-1] != bit_values[bit_idx]:
			base_trans_count += 1
	base_ones_count = bit_values.count(1)
	printV(4, "Vector transition count:", base_trans_count)
	printV(4, "Vector taken count:", base_ones_count)

	split_val = bit_values[0] # Value that indicates a transition group boundary
	split_next = False # Start a new group when split_val is next encountered
	transition_groups = []
	group = [bit_values[0]]
	for bit_pos in range(1, 32):
		if (bit_values[bit_pos] == split_val):
			if split_next:
				transition_groups.append(copy(group))
				group = [bit_values[bit_pos]]
				split_next = False
			else:
				group.append(bit_values[bit_pos])
		else:
			group.append(bit_values[bit_pos])
			split_next = True
	transition_groups.append(copy(group)) # Last group
	del group

	shuffled_vectors = []
	for v in range(count):
		random.shuffle(transition_groups)
		shuffled_bit_values = [bit for group in transition_groups for bit in group]
		shift_idx = random.randint(0, 32)
		shifted_bit_values = shuffled_bit_values[shift_idx:] + shuffled_bit_values[:shift_idx]
		new_trans_count = 0
		for bit_idx in range(32):
			if shifted_bit_values[bit_idx-1] != shifted_bit_values[bit_idx]:
				new_trans_count += 1
		new_ones_count = shifted_bit_values.count(1)
		if (new_trans_count != base_trans_count) or (new_ones_count != base_ones_count):
			sys.error("Branch vector shuffling changed taken/transition rates")
			exit()

		printV(4, shifted_bit_values)
		if slow_vector:
			bit_vector_list = shifted_bit_values + [0]*32
		else:
			bit_vector_list = [0]*32 + shifted_bit_values
		#print bit_vector_list
		bit_vector = 0
		for bit in bit_vector_list:
			bit_vector = (bit_vector << 1) | bit

		printV(4, "{0:#0{1}x}".format(bit_vector,18))
		shuffled_vectors.append(bit_vector)

	return shuffled_vectors

class BranchBehaviors():
	"""
	Use the profile data to generate branch behavior
	
	    Args:
	No arguments are needed 

	    Returns:
	No return arguments

	"""

	def generateBranchBehavior_v2(self):
		pBrTrans = int(self.brTrans * 100)
		BrBucketIds = deque()
		br = self.staticBbls
		tempBrCt = self.staticBbls
		nActualBranches = self.staticBbls
		currBrTrans = 0
		tempcurrBrTrans = 0
		last_bucket_id = 0

		while (tempBrCt > 0) :
				nTrials = 10
				thisBrTr = 0
				br_bucket_id = 0
				while (nTrials > 0):
						temp_bucket_id = 0
						temp_br_tr = 0
						tempcurrBrTrans = 0

						temp_bucket_id = random.randint (0, 9)
						if(temp_bucket_id == 0) :
								temp_br_tr = 0
						else:
								temp_br_tr = int(( 100) / temp_bucket_id)

						tempcurrBrTrans = (((currBrTrans * (nActualBranches - tempBrCt)) + temp_br_tr))/(nActualBranches - tempBrCt + 1)

						if((tempcurrBrTrans >= (pBrTrans * 1)) and (tempcurrBrTrans <= (pBrTrans * 2))):
								if(temp_bucket_id != last_bucket_id):
										thisBrTr = temp_br_tr
										br_bucket_id = temp_bucket_id
										break
						nTrials = nTrials - 1
						if(nTrials == 0):
								if(tempcurrBrTrans <= pBrTrans) :
										br_bucket_id = 1
										thisBrTr = int((100) / br_bucket_id)
								else :
										br_bucket_id = 2;
										thisBrTr = 50;
				last_bucket_id = br_bucket_id
				if(br_bucket_id != 0) :
						br_bucket_id = pow(2, (br_bucket_id - 1)        )
				tempBrCt = tempBrCt - 1
				currBrTrans = ( ( (currBrTrans * (nActualBranches - tempBrCt - 1)) + thisBrTr))/(nActualBranches - tempBrCt);
				BrBucketIds.append(br_bucket_id)
		printV(3, "Current Branch Transition is ", currBrTrans)

		for ins in self.insList:
				if(ins.getType() == "branch_test"):
						for operand in ins.operands:
								if operand.isImmediate():
										operand.imm = BrBucketIds.popleft()
		return False

	def generateBranchBehavior_v3(self):
		num_bins = 10
		bin_trans_rates = np.array([0] + [1/float(pow(2, branch_bin-1)) for branch_bin in range(1, num_bins)])

		running_trans_rate = 0
		selected_bins = []

		target_trans_rate = self.brTrans
		target_taken_rate = 0.5 # TODO - determine whether this matters
		target_num_branches = self.staticBbls

		# The convergence rate determines how aggressively the envelope of allowable values converges
		# Increasing this may improve how well the results approach the target transition rate
		# Decreasing this may increase the variety of branch instructions
		convergence_rate = 3.0

		# Increase this to make the initial envelope wider (and vice-versa)
		envelope_size = 4.0

		# These functions help define the general shape of the envelope - an exponential curve
		# Upper bound = envelope_scalar * (envelope_base ^ ((branch #) ^ 1/convergence_rate))
		envelope_scalar = pow(target_trans_rate, 1/float(envelope_size))
		envelope_base = pow(pow(target_trans_rate, (envelope_size-1)/float(envelope_size*target_num_branches)), pow(target_num_branches, ((convergence_rate-1)/float(convergence_rate))))

		for bin_idx in range(0, target_num_branches):
			rate_upper_bound = envelope_scalar * pow(envelope_base, pow(bin_idx, 1/float(convergence_rate)))
			rate_lower_bound = (2*target_trans_rate)-rate_upper_bound
			# Choose bins at random, narrowing the scope when results are out of range
			min_bin = 0
			max_bin = num_bins-1
			assigned = False
			while not assigned:
				branch_bin = random.randint(min_bin, max_bin)
				new_trans_rate = ((running_trans_rate * bin_idx) + bin_trans_rates[branch_bin]) / (bin_idx + 1) # hypothetical new transition rate
				if (new_trans_rate < rate_lower_bound):
					max_bin = branch_bin - 1
				elif (new_trans_rate > rate_upper_bound):
					min_bin = branch_bin + 1
				else:
					running_trans_rate = new_trans_rate
					selected_bins.append(branch_bin)
					#bin_counts[branch_bin] += 1
					assigned = True
				if (min_bin > max_bin):
					# No bin brings the transition rate within the envelope - but we'll get as close as we can
					ideal_rate = (target_trans_rate * (bin_idx + 1)) - (running_trans_rate * bin_idx)
					best_bin = nearest_idx(bin_trans_rates, ideal_rate)
					running_trans_rate = ((running_trans_rate * bin_idx) + bin_trans_rates[best_bin]) / (bin_idx + 1)
					selected_bins.append(best_bin)
					#bin_counts[best_bin] += 1
					assigned = True
			printV(3, "Current Branch Transition is ", running_trans_rate)

		random.shuffle(selected_bins)
		branch_immediates = []
		for branch_bin in selected_bins:
			if branch_bin != 0:
				branch_immediates.append(pow(2, branch_bin-1))
			else:
				if random.random() < target_taken_rate:
					branch_immediates.append(-1)
				else:
					branch_immediates.append(0)

		for ins in self.insList:
			if(ins.getType() == "branch_test"):
				for operand in ins.operands:
					if operand.isImmediate():
						operand.imm = branch_immediates.pop(0)
		return False
			
	def generateBranchBehavior_v4(self):
		if not self.has_local_branch_info:
			sys.error("v4 branch behavior function requires local branch info, but no local branch info is present")
			exit()
		branches = self.local_branches
		target_num_branches = self.staticBbls
		unique_branches = len(branches)
		branches.sort(key=itemgetter(0), reverse=True)

		if len(branches) > target_num_branches: # Discard branches that could not possibly survive scaling
			branches = branches[0:target_num_branches]
		printV(4, "Raw branch counts: " + str([br[0] for br in branches]))

		total_branches = sum([br[0] for br in branches])


		### Determine count of each branch

		branches_assigned = 0
		for branch in branches:
			branch[0] = max(int((branch[0]*target_num_branches/float(total_branches)) + 0.5), 1)
			#print branch[0]
			branches_assigned += branch[0]
		printV(4, "Scaled branch counts: " + str([br[0] for br in branches]))

		#print branches_assigned
		#print target_num_branches
		while branches_assigned > target_num_branches:
			for br in range(len(branches)-1, -1, -1):
				branches[br][0] -= 1
				branches_assigned -= 1
				if branches[br][0] == 0:
					del branches[br]
				if branches_assigned == target_num_branches:
					break

		while branches_assigned < target_num_branches:
			for br in range(0, len(branches)):
				branches[br][0] += 1
				branches_assigned += 1
				if branches_assigned == target_num_branches:
					break

		printV(4, "Target branch counts: " + str([br[0] for br in branches]))

		### Generate list of bit vectors
		branch_vectors = []
		for branch in branches:
			branch_vector = makeBranchVector(branch[1], branch[2])
			branch_vectors = branch_vectors + populate_branch_vectors(branch_vector, branch[0])
                        #branch_vectors = branch_vectors + makeVectorShuffles(branch_vector, branch[0])

		#random.shuffle(branch_vectors)

                #Experiment looking at branch correlation
                #Shuffling every other bit vector so that roughly 50% of the branches are highly correlated
                odds = branch_vectors[1::3]
                random.shuffle(odds)
                branch_vectors[1::3] = odds
                

                

                
		printV(3, "Uniques in output (" + str(len(branches)) + "/" + str(unique_branches) + " bins; " + str(len(set(branch_vectors))) + " vectors): " + str(["{0:#0{1}x}".format(v,18) for v in set(branch_vectors)]))
		printV(3, ["{0:#0{1}x}".format(v,18) for v in branch_vectors])
		printV(3, "Generated " + str(len(set(branch_vectors))) + "/" + str(len(branch_vectors)) + " unique vectors, using " + str(len(branches)) + "/" + str(unique_branches) + " bins")
		
		for ins in self.insList:
			if(ins.getType() == "branch_test"):
				for operand in ins.operands:
					if operand.isImmediate():
						if branch_vectors[0] >= 1 << 32:
							operand.imm = branch_vectors[0] >> 32
						else:
							operand.imm = branch_vectors[0]
					elif operand.isRegRead():
						if branch_vectors[0] >= 1 << 32:
							operand.reg = "%%esi"
				del branch_vectors[0]
		return False

	def generateBranchBehavior_v5(self):
		if not self.has_local_branch_info:
			sys.error("v5 branch behavior function requires local branch info, but no local branch info is present")
			exit()
		if not self.has_branch_correlation_info:
			sys.error("v5 branch behavior function requires branch correlation data")
			exit()
		branches = self.local_branches
		correlations = self.branch_correlations
		target_num_branches = self.staticBbls
		global_taken_rate = self.global_taken_rate
		# This is a hefty enough function that it gets its own separate file
		#branch_vectors = branch_v5(branches, correlations, target_num_branches, global_taken_rate)
		branch_vectors = branch_v5(branches, correlations, target_num_branches)

		for ins in self.insList:
			if(ins.getType() == "branch_test"):
				for operand in ins.operands:
					if operand.isImmediate():
						if branch_vectors[0] >= 1 << 32:
							operand.imm = branch_vectors[0] >> 32
						else:
							operand.imm = branch_vectors[0]
					elif operand.isRegRead():
						if branch_vectors[0] >= 1 << 32:
							operand.reg = "%%esi" # There's probably a cleaner way to do this
				del branch_vectors[0]
		return False

