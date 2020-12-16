from math import ceil
from VerbosePrint import printV
import re
import random
import ast
import json

def mk_repeat_str(count):
	repeat_str = "REPEAT("
	repeat_str += str((count/10000000000)%10) + ","
	repeat_str += str((count/1000000000)%10) + ","
	repeat_str += str((count/100000000)%10) + ","
	repeat_str += str((count/10000000)%10) + ","
	repeat_str += str((count/1000000)%10) + ","
	repeat_str += str((count/100000)%10) + ","
	repeat_str += str((count/10000)%10) + ","
	repeat_str += str((count/1000)%10) + ","
	repeat_str += str((count/100)%10) + ","
	repeat_str += str((count/10)%10) + ","
	repeat_str += str((count/1)%10) + ","
	repeat_str += " 0,)"
	return repeat_str

class LL_Item:
	def set_stress(self):
		self.actual_stride = self.position - self.prev.position
		self.p_stress, self.s_stress = self.get_stress()

	def get_stress(self, new_position=None):
		if not new_position:
			new_position = self.position
		if self.id[1] == 0: # The first element always has 0 stress
			return (0, 0)
		new_actual_stride = new_position - self.prev.position
		if new_actual_stride < self.min_stride:
			new_p_stress = (self.min_stride - new_actual_stride) ** 2
		elif new_actual_stride > self.max_stride:
			new_p_stress = -((new_actual_stride - self.max_stride) ** 2)
		else:
			new_p_stress = 0
		new_s_stress = self.target_stride - new_actual_stride
		return (new_p_stress, new_s_stress)

	def set_position(self, new_position):
		self.position = new_position
		self.set_stress()
		self.next.set_stress()

	def get_position(self):
		return self.position

	def get_target_position(self):
		if self.id[1] == 0:
			return self.position
		if self.p_stress != 0:
			if self.actual_stride < self.min_stride:
				return self.position + self.min_stride - self.actual_stride
			elif self.actual_stride > self.max_stride:
				return self.position + self.max_stride - self.actual_stride
		else:
			return self.position + self.target_stride - self.actual_stride

	def update_target_strides(self):
		if self.id[1] == 0:
			self.min_stride = None
			self.max_stride = None
			self.target_stride = None
			return
		if self.prev.stride_forward:
			self.min_stride = 2**self.prev.log_stride
			self.max_stride = (2**(self.prev.log_stride+1))-1
			self.target_stride = int((2**self.prev.log_stride) + (2**(self.prev.log_stride-1)))
		else:
			self.min_stride = -((2**(self.prev.log_stride+1))-1)
			self.max_stride = -(2**self.prev.log_stride)
			self.target_stride = -(int((2**self.prev.log_stride) + (2**(self.prev.log_stride-1))))

	def __init__(self, trace_idx, entry_idx, stride, position, prev_item=None, next_item=None):
		if not prev_item:
			prev_item = self
		if not next_item:
			next_item = self
		self.id = (trace_idx, entry_idx)
		self.prev = prev_item
		self.next = next_item
		self.prev.next = self
		self.next.prev = self
		self.stride_forward = stride[0]
		self.log_stride = stride[1]
		self.update_target_strides()
		self.next.update_target_strides()
		self.set_position(position)

	def __hash__(self):
		return hash(self.id)


class Stride_List:
	def add_item(self, trace_idx, entry_idx, stride):
		while self.insert_pos in self.lookup:
			self.insert_pos += 1
		if (trace_idx, entry_idx) in self.item_idxs:
			print "ERROR: Duplicate item (" + str(trace_idx) + ", " + str(entry_idx) + ")"
			exit()
		if entry_idx == 0:
			new_item = LL_Item(trace_idx, entry_idx, stride, self.insert_pos)
		else:
			if (trace_idx, entry_idx-1) not in self.item_idxs:
				print "ERROR: Missing expected previous item (" + str(trace_idx) + ", " + str(entry_idx-1) + ")"
				exit()
			new_item = LL_Item(trace_idx, entry_idx, stride, self.insert_pos, self.items[self.item_idxs[(trace_idx, entry_idx-1)]], self.items[self.item_idxs[(trace_idx, 0)]])
		self.lookup.update({self.insert_pos : new_item})
		self.items.append(new_item)
		self.item_idxs.update({(trace_idx, entry_idx) : len(self.items)-1})
		self.insert_pos += 1

	def move_item(self, item, new_pos):
		if new_pos == item.get_position():
			return True
		if new_pos in self.lookup:
			return False
		del self.lookup[item.get_position()]
		item.set_position(new_pos)
		self.lookup.update({new_pos : item})
		return True

	def swap_items(self, first_item, second_item):
		first_item_pos = first_item.get_position()
		second_item_pos = second_item.get_position()
		self.move_item(second_item, float("nan"))
		self.move_item(first_item, second_item_pos)
		self.move_item(second_item, first_item_pos)

	def generate_array(self):
		start_offsets = []
		out_arr = []
		sorted_positions = sorted(self.lookup.keys())
		for pos_idx in range(len(sorted_positions)):
			item = self.lookup[sorted_positions[pos_idx]]
			if item.id[1] == 0:
				start_offsets.append((item.id[0], (sorted_positions[pos_idx]-sorted_positions[0])))
			out_arr.append((item.next.get_position() - sorted_positions[0]))
			if pos_idx != len(sorted_positions)-1:
				out_arr += [0] * (sorted_positions[pos_idx+1] - sorted_positions[pos_idx] - 1)
		start_offsets = sorted(start_offsets, key=lambda x: x[0])
		cleaned_start_offsets = [x[1] for x in start_offsets]
		return (out_arr, cleaned_start_offsets)

		
	def __init__(self):
		self.insert_pos = 0
		self.lookup = {}
		self.items = []
		self.item_idxs = {}

	
def traces2ll(traces, anneal_factor=1.00, max_iterations=1000):
	stride_ll = Stride_List()
	for trace_idx, trace in enumerate(traces):
		for entry_idx, entry in enumerate(trace):
			stride_ll.add_item(trace_idx, entry_idx, entry)
	last_tot_abs_p_stress = sum(abs(i.p_stress) for i in stride_ll.items)
	last_tot_abs_s_stress = sum(abs(i.s_stress) for i in stride_ll.items)
	print "\nRun with anneal factor " + str(anneal_factor)
	print "At start of iteration 0: Total abs primary stress: " + str(last_tot_abs_p_stress) + ", total abs secondary stress: " + str(last_tot_abs_s_stress)
	marginal_improvement_count = 0
	loop_idx = 0
	while marginal_improvement_count < 10:
		anneal = anneal_factor ** max(200-loop_idx, 0)
		for item in stride_ll.items:
			if item.get_target_position() == item.get_position():
				continue
			elif item.get_target_position() not in stride_ll.lookup:
				current_abs_p_stress = abs(item.get_stress()[0]) + abs(item.next.get_stress()[0])
				current_abs_s_stress = abs(item.get_stress()[1]) + abs(item.next.get_stress()[1])
				old_position = item.get_position()
				stride_ll.move_item(item, item.get_target_position())
				moved_abs_p_stress = abs(item.get_stress()[0]) + abs(item.next.get_stress()[0])
				moved_abs_s_stress = abs(item.get_stress()[1]) + abs(item.next.get_stress()[1])
				if (moved_abs_p_stress > (current_abs_p_stress * anneal)) or ((moved_abs_p_stress == (current_abs_p_stress * anneal)) and (moved_abs_s_stress >= current_abs_s_stress * anneal)):
					stride_ll.move_item(item, old_position)
			else:
				conflicting_item = stride_ll.lookup[item.get_target_position()]
				current_abs_p_stress = abs(item.get_stress()[0]) + abs(conflicting_item.get_stress()[0]) + abs(item.next.get_stress()[0]) + abs(conflicting_item.next.get_stress()[0])
				current_abs_s_stress = abs(item.get_stress()[1]) + abs(conflicting_item.get_stress()[1]) + abs(item.next.get_stress()[1]) + abs(conflicting_item.next.get_stress()[1])
				stride_ll.swap_items(item, conflicting_item)
				swapped_abs_p_stress = abs(item.get_stress()[0]) + abs(conflicting_item.get_stress()[0]) + abs(item.next.get_stress()[0]) + abs(conflicting_item.next.get_stress()[0])
				swapped_abs_s_stress = abs(item.get_stress()[1]) + abs(conflicting_item.get_stress()[1]) + abs(item.next.get_stress()[1]) + abs(conflicting_item.next.get_stress()[1])
				if (swapped_abs_p_stress > (current_abs_p_stress * anneal)) or ((swapped_abs_p_stress == (current_abs_p_stress * anneal)) and (swapped_abs_s_stress >= current_abs_s_stress * anneal)):
					stride_ll.swap_items(item, conflicting_item)
		tot_abs_p_stress = sum(abs(i.p_stress) for i in stride_ll.items)
		tot_abs_s_stress = sum(abs(i.s_stress) for i in stride_ll.items)
		print "At end of iteration " + str(loop_idx) + ": Total abs primary stress: " + str(tot_abs_p_stress) + ", total abs secondary stress: " + str(tot_abs_s_stress)
		if ((last_tot_abs_p_stress == 0) or (abs((last_tot_abs_p_stress - tot_abs_p_stress)/float(last_tot_abs_p_stress)) < 1e-6)) \
		and (abs((last_tot_abs_s_stress - tot_abs_s_stress)/float(last_tot_abs_s_stress)) < 1e-6):
			marginal_improvement_count += 1
		else:
			marginal_improvement_count = 0
		last_tot_abs_p_stress = tot_abs_p_stress
		last_tot_abs_s_stress = tot_abs_s_stress
		loop_idx += 1
		if last_tot_abs_s_stress == 0: # Perfect arrangement! - no point in continuing further
			print "Trace can not be improved; stopping early"
			break
		if loop_idx == max_iterations:
			print "max_iterations reached; aborting"
			break
	return stride_ll.generate_array(), last_tot_abs_p_stress, last_tot_abs_s_stress

					
def traces2ll_opt(traces):
	anneal = 1.00
	incr = 0.02
	best = traces2ll(traces, 1.00)
	results = {"1.00" : best}
	while incr > 0.0001:
		new_anneal = anneal + incr
		if str(new_anneal) not in results.keys():
			#print str(new_anneal) + " not in " + str(results.keys())
			new = traces2ll(traces, new_anneal)
			results.update({str(new_anneal) : new})
			#print results.keys()
		else:
			print "\nRetrieved results for annealing factor " + str(new_anneal) + " from cached data"
			new = results[str(new_anneal)]
		if new[1] > best[1] or (new[1] == best[1] and new[2] >= best[2]):
			incr /= 2
			continue
		best = new
		anneal += incr
	print "\nRan with " + str(len(results)) + " different annealing factors"
	print "Best annealing factor: " + str(anneal)
	print "p_stress = " + str(best[1]) + ", s_stress = " + str(best[2])
	return best[0]


class Memory_HALO:
	def mkLinkedLists_HALO(self):
		printV(1, "Make linked lists")
		regions = []
		traces = {}
                try:
                        linked_list = open(self.linked_list, "r")
                        #Steven 6/8: Write ratios no longer included in file
                        #self.write_ratios = linked_list.readline()
                        #self.write_ratios = self.write_ratios[14:]
                        #self.write_ratios = ast.literal_eval(self.write_ratios)
                        #print(self.ll_starts)
                        #print(self.write_ratios)
                        lines = linked_list.readlines()
                        #No longer needed now that linked list is stored in .h file
                        #self.llstr = lines[1]
                        #self.llstr = self.llstr[23:]
                        #self.ll_starts = lines[-1][38:-2]
                        
                        #self.ll_starts = ast.literal_eval(self.ll_starts)

                        #print(self.llstr[:300])
                        #print(self.ll_starts)
                        #, 0, 0, 0, 0] #Steven 2/3/20: Hijacking old code to give us pointers
                except IOError:
                        print("Linked list not found")
                        exit(1)

        def assignStrides_HALO(self, ll_info):
                self.array_used_list = [1, 1, 1, 0, 0, 0, 0, 0]
                with open(self.multi_region, "r") as multi_region_info:
                        info = multi_region_info.readline()
                        info = multi_region_info.readline()
                        info = info[24:-1]
                        info = info.replace("[","{")
                        info = info.replace("]","}")

                        printV(3, info)

                        info_dict = ast.literal_eval(info)
                        write_strides =  multi_region_info.readline()
                        printV(3, info_dict)
                        count_dict = {}
                        index = 0
                        total = 0
                        for value in info_dict.values():
                                #value = info_dict[key]
                                if index < 6:
                                        total = total + value
                                        count_dict[index] = value
                                        index = index + 1
                        count_dict['total'] = total
                        max = 0
                        dom_reg = 0

                        for key in count_dict:
                                count_dict[key] = float(count_dict[key])/count_dict['total']
                                if count_dict[key] > max and key != 'total':
                                        max = count_dict[key]
                                        dom_reg = key
                        del count_dict['total']
                        printV(3, count_dict)

                        #stores what % of memory acceses for a linked list are strided
                        st_ratio_dict = {}
                        for x in range(0,6):
                                st_ratio_dict[x] = ll_info["region" + str(x)]["array_load_ratio"] + ll_info["region" + str(x)]["array_store_ratio"]
                        printV(3, st_ratio_dict)
 
                #Getting offset data
                offset_dict = {}
                for x in range(0,6):
                        offset_dict[x] = ll_info["region" + str(x)]["array_stride_ratios"]

                #making data structure for running totals
                run_count = {}
                dom_offsets = {}
                for x in range(0,6):
                        run_count[x] = {"arr":0, "ll":0, "tot":0, "prev_offset":0, "offsets":{},"dom_offset":"0"}
                        max = 0
                        max_key = "0"
                        for key in offset_dict[x]:
                                if offset_dict[x][key] > max:
                                        max = offset_dict[x][key]
                                        max_key = key
                                run_count[x]["offsets"][key] = 0
                        run_count[x]["dom_offset"] = max_key
                run_count["total"] = 0
                print(run_count)

                for ins in self.insList:
                        if ins.memAccess == True:
                                #selecting which linked list to use based on distribution of linked lists
                                region = None
                                for x in range(0,6):
                                        if(float(run_count[x]["tot"]+1)/(run_count["total"]+1) < count_dict[x]):
                                                region = x
                                                break
                                if region == None:
                                        region = dom_reg

                                #Selecting strided read vs linked list read
                                x = float(run_count[region]["arr"]+1)
                                y = run_count[region]["tot"]+1
                                if(x/y < st_ratio_dict[region]):
                                        ins.ll = False


                                #selecting what offset to use
                                offset = None
                                #print(region)
                                #print(run_count[region])
                                for key in run_count[region]["offsets"]:
                                        x = float(run_count[region]["offsets"][key]+1) 
                                        y = run_count[region]["tot"]+1
                                        if(x/y < offset_dict[region][key]):
                                           offset = key
                                           print("Selected offset of {} for region {}".format(offset, region))
                                           break
                                if offset == None:
                                        offset = run_count[region]["dom_offset"]
                                        print("Selected dominant offset of {} for region {}".format(offset, region))
                                
                                #Code for assigning operand info for all memory accesses
                                for operand in ins.operands:
                                        if operand.isMem() and operand.rw == "r":
                                                #Both linked list reads and strided reads
                                                #printV(3, "Read base is: ", self.registers.readBase[0])
                                                operand.reg = self.registers.readBase[0]
                                                
                                                operand.offset_reg = self.registers.index[region]
                                                operand.offset_scale = 8

                                                #Strided read case
                                                if ins.ll == False:
                                                        print("Strided read")
                                                        effective_offset = run_count[region]["prev_offset"] + int(offset) * 8
                                                        operand.offset = int(offset) * 8
                                                        run_count["total"] = run_count["total"] + 1
                                                        run_count[region]["tot"] = run_count[region]["tot"] +1
                                                        run_count[region]["arr"] = run_count[region]["arr"] + 1
                                                        run_count[region]["offsets"][offset] = run_count[region]["offsets"][offset] + 1
                                                        run_count[region]["prev_offset"] = effective_offset
                                                else:
                                                        run_count["total"] = run_count["total"] + 1
                                                        run_count[region]["tot"] = run_count[region]["tot"] +1
                                                        run_count[region]["ll"] = run_count[region]["ll"] + 1
                                                        run_count[region]["prev_offset"] = 0

                                        elif operand.isMem():
                                                #All write instructions
                                                effective_offset = run_count[region]["prev_offset"] + int(offset) * 8
                                                operand.reg = self.registers.readBase[0]
                                                operand.offset_reg = self.registers.index[region]
                                                operand.offset_scale = 8
                                                operand.offset = int(offset) * 8 + 4
                                                run_count["total"] = run_count["total"] + 1
                                                run_count[region]["tot"] = run_count[region]["tot"] +1
                                                run_count[region]["arr"] = run_count[region]["arr"] + 1
                                                run_count[region]["offsets"][offset] = run_count[region]["offsets"][offset] + 1
                                                run_count[region]["prev_offset"] = effective_offset
                                                #operand.offset = 4
                                        elif ins.ll == True:
                                                operand.reg = self.registers.index[region]
                                printV(3, "New instruction is: ", str(ins))

                printV(3, "Memory assignments complete")
                #print(json.dumps(st_ratio_dict, sort_keys=True, indent=4))
                print(json.dumps(offset_dict, sort_keys=True, indent=4))
                print(json.dumps(run_count, sort_keys=True, indent=4))

                                        
