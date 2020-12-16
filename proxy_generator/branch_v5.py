import math
from operator import itemgetter
from copy import copy
from VerbosePrint import printV

Bit_Vector_Len = 32

"""
Wrapper class for branch bit vectors
"""
class Bit_Vector:
    # Correlation between two bit_vectors
    def correlation(self, other):
        if not (self.is_slow ^ other.is_slow): # Either both are fast or both are slow
            covariance = sum(1 if self.bits[i] == other.bits[i] else -1 for i in range(Bit_Vector_Len))
            return covariance / float(Bit_Vector_Len)
        else: # One is slow and the other is fast
            # No need for element-wise comparison here; can compare ratios instead
            self_zero_ratio = self.bits.count(0) / float(Bit_Vector_Len)
            other_zero_ratio = other.bits.count(0) / float(Bit_Vector_Len)
            return (2*self_zero_ratio - 1) * (2*other_zero_ratio - 1)

    def __int__(self):
        int_val = sum(x << i for i, x in enumerate(self.bits))
        if self.is_slow:
            int_val <<= Bit_Vector_Len
        return int_val

    def __repr__(self):
        string = "s" if self.is_slow else "f"
        string += "".join(str(b) for b in reversed(self.bits))
        return string

    def __eq__(self, other):
        return self.bits == other.bits and self.is_slow == other.is_slow

    def __hash__(self):
        return hash(self.bits, self.is_slow)

    def __init__(self, bits, is_slow):
        assert(len(bits) == Bit_Vector_Len)
        self.bits = copy(bits)
        self.is_slow = is_slow

"""
Represents an individual branch with corresponding vectors
"""
class Branch:
    branch_id = 0

    # Here's the clever bit: it doesn't matter which vector we eventually choose for the other branch; the result is the same
    # Why? Well, the final vector is a shifted and/or reversed vector from the first vector; but this branch has shifted/reversed vectors as well
    # So there will still be a branch vector with the same correlation, it just might not be the same vector
    def min_error_after(self, other_branch):
        if other_branch in self.corr_error_cache:
            return self.corr_error_cache[other_branch]
        err = min(abs(self.bit_vectors[0].correlation(v) - self.target_corr) for v in other_branch.bit_vectors)
        self.corr_error_cache.update({other_branch : err})
        return err

    def match_correlation(self, other_vector, target_correlation=None):
        if target_correlation is None:
            target_correlation = self.target_corr
        correlations = [v.correlation(other_vector) for v in self.bit_vectors]
        closest_correlation = sorted(correlations, key=lambda x: abs(x-target_correlation))[0]
        closest_vector = self.bit_vectors[correlations.index(closest_correlation)]
        return closest_vector

    def __hash__(self):
        return hash(self.branch_id) # IDs are guaranteed to be unique

    def __init__(self, taken_rate, transition_rate, target_corr):
        self.branch_id = Branch.branch_id
        Branch.branch_id += 1
        self.corr_bound_cache = {}
        self.corr_error_cache = {}
        self.target_corr = target_corr

        # Generate a "base" branch vector from which all others are derived

        # Step 1: Generate a bit vector representation of the branch matching only the target transition rate

        # The minimum (non-zero) fast vector transition rate is 1/16, and the maximum slow vector transition rate is 1/32 (assuming 32b branch vector)
        # We use the average of these to decide which type of vector to generate for a branch
        slow_rate = 1.5 / Bit_Vector_Len
        slow_vector = transition_rate < slow_rate
        if slow_vector:
            transition_rate = min(transition_rate * Bit_Vector_Len, 1) 

        target_transitions = 2 * int(transition_rate * (Bit_Vector_Len/2) + 0.5) # Vectors can only have even numbers of transitions, so our target must be even

        bit_vector = [1] # We arbitrarily choose the first entry in the vector to be a 1 ("taken"); we can change this later if needed
        trans_distance = 0 # Bits assigned since previous transition
        remaining_transitions = target_transitions - 1 # Non-constant vectors normally end in 0, causing a transition when they restart (since the first bit is 1) 
        for bit in range(1, Bit_Vector_Len): # Iterate over remaining bits
            trans_distance += 1
            if ((remaining_transitions > 0) and (trans_distance >= ((Bit_Vector_Len - bit) / float(remaining_transitions)))): # Transition for next bit
                bit_vector.append(1 - bit_vector[-1])
                trans_distance = 0;
                remaining_transitions -= 1;
            else: # Don't transition
                bit_vector.append(bit_vector[-1])
    
        # Step 2: Adjust the taken rate of the branch by flipping bits at transition boundaries (which does not affect the transition rate)
        initial_taken_rate = bit_vector.count(1) / float(Bit_Vector_Len)
        if (initial_taken_rate - 0.5 > taken_rate): # Beginning by flipping all the bits can help to match low taken rates
            for bit in range(Bit_Vector_Len):
                bit_vector[bit] = 1 - bit_vector[bit]

        target_ones = int((taken_rate * Bit_Vector_Len) + 0.5)
        running_ones_count = bit_vector.count(1)
        while True: # The bit flipping process needs to run a worst-case quadratic number of times w.r.t the vector length, but vectors are pretty short
            starting_vector = copy(bit_vector)
            for count in range(Bit_Vector_Len): 
                if running_ones_count == target_ones:
                    break
                bit = (count * ((Bit_Vector_Len/2)+1)) % Bit_Vector_Len # Accessing in a staggered pattern gives more even results (e.g. 0 17 2 19 4 21 6 23 ... 30 15 0)
                # Get if bit lies on a transition boundary, meaning toggling its value will not add or remove any transitions
                if bit_vector[(bit+Bit_Vector_Len-1)%Bit_Vector_Len] != bit_vector[(bit+1)%Bit_Vector_Len]:
                    if ((running_ones_count < target_ones) and (bit_vector[bit] == 0)):
                        bit_vector[bit] = 1
                        running_ones_count += 1
                    elif ((running_ones_count > target_ones) and (bit_vector[bit] == 1)):
                        bit_vector[bit] = 0
                        running_ones_count -= 1
            if (running_ones_count == target_ones) or starting_vector == bit_vector: # We've either reached our target or stopped making progress
                break
        
        # Align the vector so the first and last bits are different, if possible; this is important for forming "transition groups"
        if 0 < bit_vector.count(1) < Bit_Vector_Len:
            while bit_vector[0] == bit_vector[-1]:
                bit_vector = bit_vector[1:] + bit_vector[0:1]

        # Step 3: Shuffle "transition groups" (complete block of 0s followed by complete block of 1s, or vice versa)
        # This helps "even out" the branch vector
        split_val = bit_vector[0] # First value in the group; when re-encountered after seeing the other bit value, this indicates a transition group boundary
        split_next = False # Whether we should start a new group when split_val is next encountered
        transition_groups = []
        group = [bit_vector[0]]
        for bit_pos in range(1, 32):
            if (bit_vector[bit_pos] == split_val):
                if split_next:
                    transition_groups.append(copy(group))
                    group = [bit_vector[bit_pos]]
                    split_next = False
                else:
                    group.append(bit_vector[bit_pos])
            else:
                group.append(bit_vector[bit_pos])
                split_next = True
        transition_groups.append(copy(group)) # Last group
        del group

        bit_pos = 0
        while(len(transition_groups) >= 2): # Interleave groups
            for element in transition_groups[0]:
                bit_vector[bit_pos] = element
                bit_pos += 1
            for element in transition_groups[-1]:
                bit_vector[bit_pos] = element
                bit_pos += 1
            del transition_groups[0]
            del transition_groups[-1]
        if (len(transition_groups) == 1): # Last group if odd number of groups
            for element in transition_groups[0]:
                bit_vector[bit_pos] = element
                bit_pos += 1
        del transition_groups

        # Step 4: Generate variants of the branch vector
        # TODO: Can we generate more vectors here? Tried several approaches, but they actually seem to make results worse
        self.bit_vectors = []
        for _ in range(Bit_Vector_Len):
            self.bit_vectors.append(Bit_Vector(bit_vector, slow_vector))
            bit_vector = bit_vector[1:] + bit_vector[0:1]
        bit_vector.reverse()
        for _ in range(Bit_Vector_Len):
            self.bit_vectors.append(Bit_Vector(bit_vector, slow_vector))
            bit_vector = bit_vector[1:] + bit_vector[0:1]
        self.bit_vectors = [v for i, v in enumerate(self.bit_vectors) if self.bit_vectors[:i+1].count(v) == 1] # Deduplicate

def get_vector_error(first_vector, second_vector, target_corr):
    corr = first_vector.correlation(second_vector)
    return abs(corr-target_corr)
            
def branch_v5(local_branches, branch_correlations, target_branch_count):
    printV(1, "Run correlation-based branch generator",)
    printV(2, "Phase 0: Data preprocessing",)
    input_dynamic_branches = sum(b[0] for b in local_branches) # Total count
    branches = []
    branch_counts = {}
    for branch_idx, branch_data in enumerate(local_branches):
        taken_rate = branch_data[1]
        trans_rate = branch_data[2]
        new_branch = Branch(taken_rate, trans_rate, branch_correlations[branch_idx][0]["correlation"])
        branches.append(new_branch)
        branch_counts.update({new_branch : branch_data[0]})
    branches.sort(key = lambda x: branch_counts[x], reverse=True) # Sort branches descending by number of occurences
    printV(2, str(len(branches)) + " static branches in input, comprising " + str(input_dynamic_branches) + " total dynamic branches")
    
    # The runtime and memory footprint of branch assignment scales quadratically with the number of different branches
    # If we have a vast number of different branches, we cull the rare ones to keep runtime reasonable
    max_unique_branches = 512
    if len(branches) > max_unique_branches:
        branches = branches[0:max_unique_branches] # Recall that branches were sorted descending by occurences previously
        branch_counts = {b: branch_counts[b] for b in branches}
    total_branch_count = sum(branch_counts[b] for b in branches)

    overrepresentations = []
    for branch in branches:
        scaled_branch_count = (target_branch_count * branch_counts[branch]) / float(total_branch_count)
        branch_counts[branch] = int(math.ceil(scaled_branch_count))
        overrepresentations.append((branch, math.ceil(scaled_branch_count) - scaled_branch_count))
    overrepresentations.sort(key=itemgetter(1), reverse=True)

    total_branch_count = sum(branch_counts[b] for b in branches)
    assert(0 <= total_branch_count - target_branch_count <= len(branches))
    while total_branch_count > target_branch_count:
        branch = overrepresentations.pop(0)[0] # Most overrepresented branch
        assert(branch_counts[branch] > 0)
        branch_counts[branch] -= 1
        total_branch_count -= 1
    branches = [b for b in branches if b if branch_counts[b] > 0]
    branch_counts = {b: c for b, c in branch_counts.iteritems() if c > 0}
    
    assert(all(branch_counts[b] > 0 for b in branches))
    assert(all(b in branch_counts for b in branches))
    total_branch_count = sum(branch_counts[b] for b in branches)
    assert(total_branch_count == target_branch_count)

    printV(4, "After refinement: " + str(len(branches)) + " types of static branch in proxy")

    printV(2, "\nPhase 1: Initial branch assignment")
    est_global_error = 0.0
    reversed_branch_list = []
    while len(reversed_branch_list) < target_branch_count:
        if len(reversed_branch_list) == 0:
            error = 0.0
            branch = branches[0]
        else:
            # Get the "best" branch: pick the most numerous branch that falls in bounds, else pick the closest branch
            last_branch = reversed_branch_list[-1]
            branch_corr_errors = []
            for branch in branches:
                corr_error = last_branch.min_error_after(branch)
                branch_corr_errors.append(corr_error)
            zero_error_branches = [branches[i] for i, e in enumerate(branch_corr_errors) if e == 0]
            if len(zero_error_branches) > 0: # Take most numerous branch with zero error
                error = 0.0
                branch = max(zero_error_branches, key=lambda b: branch_counts[b])
            else: # Take branch with least error
                error = min(branch_corr_errors)
                branch = branches[branch_corr_errors.index(error)]
       
        printV(4, "Appending branch " + str(branch.branch_id) + " to list, contributing error of (at least) " + str(error))
        est_global_error += error
        reversed_branch_list.append(branch)
        branch_counts[branch] -= 1
        if branch_counts[branch] == 0:
            printV(4, "Assigned all instances of branch " + str(branch.branch_id))
            del branch_counts[branch]
            branches.remove(branch)
    branch_list = list(reversed(reversed_branch_list))
    assert(0.95 < (sum(branch_list[i].min_error_after(branch_list[i-1]) for i in range(1, len(branch_list))) / est_global_error) < 1.05)
    printV(2, "Finished initial branch assignment; estimated error is " + str(est_global_error) + " (per branch: " + str(est_global_error/target_branch_count) + ")")

    printV(2, "\nPhase 2: Branch Rearrangement")
    old_est_global_error = est_global_error
    swaps = 0
    for first_idx in range(1, len(branch_list)):
        best_idx = None
        best_improvement = 0.0
        first_branch = branch_list[first_idx]
        for second_idx in range(first_idx):
            second_branch = branch_list[second_idx]
            current_error = branch_list[first_idx].min_error_after(branch_list[first_idx-1])
            if second_idx < first_idx - 1:
                current_error += branch_list[second_idx+1].min_error_after(branch_list[second_idx])
            if first_idx < len(branch_list) - 1:
                current_error += branch_list[first_idx+1].min_error_after(branch_list[first_idx])
            if second_idx > 0:
                current_error += branch_list[second_idx].min_error_after(branch_list[second_idx-1])
            branch_list[first_idx] = second_branch
            branch_list[second_idx] = first_branch
            swapped_error = branch_list[first_idx].min_error_after(branch_list[first_idx-1])
            if second_idx < first_idx - 1:
                swapped_error += branch_list[second_idx+1].min_error_after(branch_list[second_idx])
            if first_idx < len(branch_list) - 1:
                swapped_error += branch_list[first_idx+1].min_error_after(branch_list[first_idx])
            if second_idx > 0:
                swapped_error += branch_list[second_idx].min_error_after(branch_list[second_idx-1])
            if current_error - swapped_error > best_improvement:
                best_idx = second_idx
                best_improvement = current_error - swapped_error
            branch_list[first_idx] = first_branch
            branch_list[second_idx] = second_branch
        if best_idx is not None:
            printV(4, "Swapping branches at locations " + str(best_idx) + " and " + str(first_idx) + ", reducing estimated error by " + str(best_improvement))
            second_branch = branch_list[best_idx]
            branch_list[first_idx] = second_branch
            branch_list[best_idx] = first_branch
            est_global_error -= best_improvement
            swaps += 1

    est_global_error = sum(branch_list[i].min_error_after(branch_list[i-1]) for i in range(1, len(branch_list)))

    printV(2, "Finished branch rearrangement; swapped " + str(swaps) + " times; new estimated error is " + str(est_global_error))
    printV(3, "  Swapped " + str((100*swaps)/float(len(branch_list))) + "% of the time; estimated error was reduced by " + \
        str(old_est_global_error - est_global_error) + ", or " + str((100*(old_est_global_error-est_global_error))/old_est_global_error) + "%")

    printV(2, "\nPhase 3: Specify branch vectors")
    branch_vectors = [branch_list[0].bit_vectors[0]]
    for branch_idx in range(1, len(branch_list)):
        best_vector = branch_list[branch_idx].match_correlation(branch_vectors[-1])
        assert(abs(best_vector.correlation(branch_vectors[-1]) - branch_list[branch_idx].target_corr) == branch_list[branch_idx].min_error_after(branch_list[branch_idx-1]))
        branch_vectors.append(best_vector)
    signed_global_error = sum(branch_vectors[i].correlation(branch_vectors[i-1]) - branch_list[i].target_corr for i in range(1, len(branch_list)))
    global_error = sum(abs(branch_vectors[i].correlation(branch_vectors[i-1]) - branch_list[i].target_corr) for i in range(1, len(branch_list)))
    assert(global_error >= est_global_error)
    printV(2, "Finished vector specification, achieving an actual error of " + str(global_error) + " vs. the estimate of " + str(est_global_error))
    printV(3, "  This is " + str((100*(global_error-est_global_error))/est_global_error) + "% greater than the estimate")
    printV(3, "  Signed global error is " + str(signed_global_error) + ", for an asymmetry factor of " + str(signed_global_error/global_error))
    
    printV(2, "\nPhase 4: Late Vector Rearrangement")
    old_global_error = global_error
    swaps = 0
    for first_idx in range(1, len(branch_list)):
        best_idx = None
        best_improvement = 0.0
        first_branch = branch_list[first_idx]
        first_vector = branch_vectors[first_idx]
        for second_idx in range(first_idx):
            second_branch = branch_list[second_idx]
            second_vector = branch_vectors[second_idx]
            current_error = get_vector_error(branch_vectors[first_idx], branch_vectors[first_idx-1], branch_list[first_idx].target_corr)
            if second_idx < first_idx - 1:
                current_error += get_vector_error(branch_vectors[second_idx+1], branch_vectors[second_idx], branch_list[second_idx+1].target_corr)
            if first_idx < len(branch_list) - 1:
                current_error += get_vector_error(branch_vectors[first_idx+1], branch_vectors[first_idx], branch_list[first_idx+1].target_corr)
            if second_idx > 0:
                current_error += get_vector_error(branch_vectors[second_idx], branch_vectors[second_idx-1], branch_list[second_idx].target_corr)
            branch_list[first_idx] = second_branch
            branch_vectors[first_idx] = second_vector
            branch_list[second_idx] = first_branch
            branch_vectors[second_idx] = first_vector
            swapped_error = get_vector_error(branch_vectors[first_idx], branch_vectors[first_idx-1], branch_list[first_idx].target_corr)
            if second_idx < first_idx - 1:
                swapped_error += get_vector_error(branch_vectors[second_idx+1], branch_vectors[second_idx], branch_list[second_idx+1].target_corr)
            if first_idx < len(branch_list) - 1:
                swapped_error += get_vector_error(branch_vectors[first_idx+1], branch_vectors[first_idx], branch_list[first_idx+1].target_corr)
            if second_idx > 0:
                swapped_error += get_vector_error(branch_vectors[second_idx], branch_vectors[second_idx-1], branch_list[second_idx].target_corr)
            if current_error - swapped_error > best_improvement:
                best_idx = second_idx
                best_improvement = current_error - swapped_error
            branch_list[first_idx] = first_branch
            branch_vectors[first_idx] = first_vector
            branch_list[second_idx] = second_branch
            branch_vectors[second_idx] = second_vector
        if best_idx is not None:
            printV(4, "Swapping vectors at locations " + str(best_idx) + " and " + str(first_idx) + ", reducing error by " + str(best_improvement))
            second_branch = branch_list[best_idx]
            second_vector = branch_vectors[best_idx]
            branch_list[first_idx] = second_branch
            branch_vectors[first_idx] = second_vector
            branch_list[best_idx] = first_branch
            branch_vectors[best_idx] = first_vector
            swaps += 1
   
    signed_global_error = sum(branch_vectors[i].correlation(branch_vectors[i-1]) - branch_list[i].target_corr for i in range(1, len(branch_list)))
    global_error = sum(abs(branch_vectors[i].correlation(branch_vectors[i-1]) - branch_list[i].target_corr) for i in range(1, len(branch_list)))
    printV(2, "Finished late swapping, achieving an actual error of " + str(global_error) + " vs. the estimate of " + str(est_global_error))
    printV(3, "  This is " + str((100*(global_error-est_global_error))/est_global_error) + "% greater than the estimate")
    printV(3, "  Signed global error is " + str(signed_global_error) + ", for an asymmetry factor of " + str(signed_global_error/global_error))
    printV(3, "  Swapped " + str(swaps) + " times, or " + str((100*swaps)/float(len(branch_list))) + "% of the time; error was reduced by " + \
        str(old_global_error - global_error) + ", or " + str((100*(old_global_error-global_error))/old_global_error) + "%")

    worst_indices = sorted(range(1,len(branch_list)), key=lambda x: get_vector_error(branch_vectors[x], branch_vectors[x-1], branch_list[x].target_corr), reverse=True)[0:5]
    printV(3, "\nReport top 5 worst errors:")
    for list_idx, idx in enumerate(worst_indices):
        err = get_vector_error(branch_vectors[idx], branch_vectors[idx-1], branch_list[idx].target_corr)
        printV(3, "  #" + str(list_idx+1) + ": At index " + str(idx) + ", error of " + str(err))
    printV(2, "Average abs error is " + str(global_error/len(branch_list)) + "; average signed error is " + str(signed_global_error/len(branch_list)))

    printV(2, "\nPhase 5: Generate final list")
    bit_vectors = [int(v) for v in branch_vectors]
    printV(1, "Branch generation complete!")
    return bit_vectors
