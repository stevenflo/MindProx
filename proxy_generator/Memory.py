import random
import operator
from VerbosePrint import *



class Memory:
        globalStrideRemoveDens = {-12: 1, 12: 1, 0: 3, 256: 2}
        localStrideRemoveDens = {0: 7}

        def removeStrides(self, dens, removeDens):
                """ remove strides is shared between all of the Memory versions

                Args:
                dens - the original dens as profiled
                removeDens - the densities that should be removed from the the dens
                
                Returns:
                nothing, dens is updated
                """
                for key in removeDens.keys():
                        if key == 0:
                                if dens.has_key(0):
                                        if dens[0] >= removeDens[key]:
                                                dens[0] -= removeDens[key]
                                                removeDens[key] = 0
                                        else:
                                                removeDens[key] -= dens[0]
                                                dens[0] = 0
                        else :
                                if dens.has_key(key):
                                        if dens[key] >= removeDens[key]:
                                                dens[key] -= removeDens[key]
                                                removeDens[key] = 0
                                        else:
                                                removeDens[key] -= dens[key]
                                                dens[key] = 0
                                if dens.has_key(-1 * key):
                                        if dens[-1 * key] >= removeDens[key]:
                                                dens[-1 * key] -= removeDens[key]
                                                removeDens[key] = 0
                                        else:
                                                removeDens[key] -= dens[-1 * key]
                                                dens[-1 * key] = 0
                return dens

        def updateGlobalDens(self, strideDens):
                init_stride = 12
                diff_stride = 8
                running_arr_ct = self.numAvailableArrays - 1;
                while running_arr_ct > 0:
                        if(strideDens.has_key(init_stride + (running_arr_ct * diff_stride))) :
                                strideDens[(init_stride + (running_arr_ct * diff_stride))] += 1
                        else :
                                strideDens[(init_stride + (running_arr_ct * diff_stride))] = 1

                        if(strideDens.has_key(-(init_stride + (running_arr_ct * diff_stride)))) :
                                strideDens[-(init_stride + (running_arr_ct * diff_stride))] += 1
                        else :
                                strideDens[-(init_stride + (running_arr_ct * diff_stride))] = 1

                        if(strideDens.has_key(diff_stride)):
                                strideDens[diff_stride] += 1
                        else :
                                strideDens[diff_stride] = 1
                        running_arr_ct -= 1

                if(strideDens.has_key(-(init_stride + ((self.numAvailableArrays - 1) * diff_stride)))):
                        strideDens[-(init_stride + ((self.numAvailableArrays - 1) * diff_stride))] += 1
                else :
                        strideDens[-(init_stride + ((self.numAvailableArrays - 1) * diff_stride))] = 1

                printV(3, "In updateGlobalDens, updated stride density for num arrays ", self.numAvailableArrays)
                printV(3, strideDens)


	def updateLocalDens(self, strideDens):
		printV(3, "In updateLocalDens", strideDens)
		running_arr_ct = self.numAvailableArrays - 1;

		while running_arr_ct > 0:
			if not (strideDens.has_key(0)) :
				strideDens[0] = 1
			else :
				strideDens[0] += 3 #TBD - Fixme
			running_arr_ct -= 1

		printV(3, "In updateLocalDens, updated local stride density for num arrays ", self.numAvailableArrays)
                printV(3, strideDens)

        def fixNumAvailArrays(self, numMemIns) :
                if(numMemIns < 10) :
                        return 2 #1
                elif(numMemIns < 70) : #Removed an available array to use for divide instructions (r15)
                        return int (numMemIns/10) + 1
                #The following elif is buggy and causes undesired behavior
                #TODO: Analyze effects of this function as opposed to always
                #      selecting 8
		#elif(numMemIns < 1600):
		#	return int (numMemIns/200) + 1 # 5arr = 300, 40; 4arr = 400, 50; 2arr = 
                else :
                        return 7

        def nextStride(self, strideDens):
                printV(3, strideDens.values())
                if sum(strideDens.values()) <= 0:
                        return self.memBlockSize
                i = random.randint(1,sum(strideDens.values()))
                printV(3, sum(strideDens.values()))
                printV(3, i)
                thisStride = None
                for strd in strideDens.items():
                        i -= strd[1]
                        if i <= 0:
                                printV(3, strd)
                                thisStride = strd[0]
                                if thisStride > abs(self.memBlockSize):
                                        return self.memBlockSize
                                else:
                                        return thisStride
        
        def prepGlobalDens(self):
	        strideRatio = float(len(self.insList)) / float(self.insMix["total"])
                printV(3, strideRatio)
                printV(3, self.stride)

                total_strides = 0
                for k, v in self.stride.items() :
                        total_strides += v

                total_mem_inst = 0
                for ins in self.insList:
                        for operand in ins.operands:
                                if operand.isMem():
                                        total_mem_inst += 1

                printV(3, "Total memory instructions = ", total_mem_inst)

                self.numAvailableArrays = self.fixNumAvailArrays(total_mem_inst) #8 TBD
                printV(3, "Num Available Arrays is ", self.numAvailableArrays)

                self.updateGlobalDens(self.globalStrideRemoveDens)
                printV(3, "Updated Before Total self.globalStrideRemoveDens values is ", sum(self.globalStrideRemoveDens.values()))

                relGlobalRemoveStrideNum = 0
                for key in self.globalStrideRemoveDens.keys():
                        #scaled_down_stride = int(float(self.stride[key] * (total_mem_inst + sum(self.globalStrideRemoveDens.values())) / float(total_strides)) + 0.5)
                        if self.stride.has_key(key) :
				scaled_down_stride = int(float(self.stride[key] * (total_mem_inst + sum(self.globalStrideRemoveDens.values())) / float(total_strides)) + 0.5)
                                if(scaled_down_stride >= self.globalStrideRemoveDens[key]) :
                                        relGlobalRemoveStrideNum += self.globalStrideRemoveDens[key]
                                else :
                                        relGlobalRemoveStrideNum += scaled_down_stride

                printV(3, "relGlobalRemoveStrideNum = ", relGlobalRemoveStrideNum)

                strideDens = {k: int(float(float(v * (total_mem_inst + relGlobalRemoveStrideNum)) / float(total_strides)) + 0.5) for k, v in self.stride.items()}
                printV(3, "After scaling Total stride density values is ", sum(strideDens.values()))
                strideDens[self.memBlockSize] += strideDens[-self.memBlockSize]
                del strideDens[-self.memBlockSize]

                printV(3, "Printing stride density before removing global strides")
                printV(3, strideDens)

                strideDens = self.removeStrides(strideDens, self.globalStrideRemoveDens)
                printV(3, "Printing stride density after removing global strides")
                printV(3, strideDens)
                printV(3, "Total sum of strideDens values = ", sum(strideDens.values()))
                return total_mem_inst, strideDens

        def prepLocalDens(self, total_mem_inst):
		printV(3, "Target local stride ratio:", self.localStride)

		total_local_strides = 0
                for k, v in self.localStride.items() :
                    total_local_strides += v
						
		self.updateLocalDens(self.localStrideRemoveDens)
		
		relLocalRemoveStrideNum = 0
		printV(3, self.localStrideRemoveDens)
		for key in self.localStrideRemoveDens.keys():
                    scaled_down_stride = int(float(self.localStride[key] * (total_mem_inst + sum(self.localStrideRemoveDens.values())) / float(total_local_strides)) + 0.5)
		    printV(3, "key is ", key)
		    printV(3, "scaled down stride is ", scaled_down_stride)
                    if self.localStride.has_key(key) :
			   printV(3, "self.localStrideRemoveDens key is ", self.localStrideRemoveDens[key])
                 	   if(scaled_down_stride >= self.localStrideRemoveDens[key]) :
                        	relLocalRemoveStrideNum += self.localStrideRemoveDens[key]
                           else :
                           	relLocalRemoveStrideNum += scaled_down_stride

                printV(3, "relLocalRemoveStrideNum = ", relLocalRemoveStrideNum)

		localStrideDens = {k: int(float(float(v * (total_mem_inst + relLocalRemoveStrideNum)) / float(total_local_strides)) + 0.5) for k, v in self.localStride.items()}
		printV(3, "Printing local stride dens before remove:", localStrideDens)
		localStrideDens = self.removeStrides(localStrideDens, self.localStrideRemoveDens)
		printV(3, "Printing local stride dens after remove:", localStrideDens)
		printV(3, "Total sum of localstrideDens values = ", sum(localStrideDens.values()))
		num_zero_strides = localStrideDens[0]
		printV(3, "num zero strides is ", num_zero_strides)

		sorted_localStrideDens = sorted(localStrideDens.items(), key=operator.itemgetter(1))
                printV(3, sorted_localStrideDens)
                
                return sorted_localStrideDens, num_zero_strides

        def prepArrays(self, sorted_localStrideDens):

		avail_arr_cnts = [0, 0, 0, 0, 0, 0, 0, 0]
		self.avail_arr_strides = [0, 0, 0, 0, 0, 0, 0, 0]
		printV(3, "Avail arr cts is ", avail_arr_cnts)
		adjusted_arr_cts = 0
		for arr_ct_act in range(0, len(sorted_localStrideDens)):
			arr_ct = len(sorted_localStrideDens) - arr_ct_act - 1
			printV(3, "arr_ct is ", arr_ct)
			if(arr_ct_act < self.numAvailableArrays):
				printV(3, "arr_ct is ", arr_ct)	
				printV(3, sorted_localStrideDens[arr_ct])
				avail_arr_cnts[arr_ct_act] = (sorted_localStrideDens[arr_ct])[1]
				self.avail_arr_strides[arr_ct_act] = (sorted_localStrideDens[arr_ct])[0]
			else:
				adjusted_arr_cts += (sorted_localStrideDens[arr_ct])[1]
		printV(3, "Extra array counts than available arrays are ", adjusted_arr_cts)

		for arr_ct in range(0, self.numAvailableArrays):
			avail_arr_cnts[arr_ct] = int(float(avail_arr_cnts[arr_ct] + (float(adjusted_arr_cts)/float(self.numAvailableArrays) + 0.5)))
			if self.avail_arr_strides[arr_ct] == 0:
				zero_stride_offset = arr_ct
                printV(3, "The avail_arr_strides are ", self.avail_arr_strides)
                printV(3, "The number of available arrays are: ", self.numAvailableArrays)
		printV(3, "Adjusted Avail arr cts is ", avail_arr_cnts)
                return avail_arr_cnts, zero_stride_offset

        def attemptAssignZero(self, ins, operand,
                             prevInsCategory, prevInsZeroStride,
                              strideDens, num_zero_strides,
                              avail_arr_cnts, zero_stride_offset):
                """ attemptAssignZero attempts to assign a local zero stride
                to an encountered memory operand based on a few criteria.

                Args:
                many
                Returns:
                many
                """
                cont_flag = 0
                if num_zero_strides > 0:
			printV(3, "\nnum zero strides is ", num_zero_strides)
			if "load" in ins.insType and prevInsCategory == None:
				printV(3, "none load case")
				prevInsCategory = "load"
				prevInsZeroStride = "False"
			elif "load" in ins.insType and prevInsCategory == "load":
				printV(3, "load load")
				prevInsCategory = "load"												
				operand.offset = 0
				operand.reg = self.registers.zeroStrideR[0]										
				if prevInsZeroStride == "True" and strideDens[0] > 0:
					printV(3, "load load case 1")
					strideDens[0] -= 1
					prevInsZeroStride = "True"
					num_zero_strides -= 1
					if(avail_arr_cnts[zero_stride_offset] > 0) :
						avail_arr_cnts[zero_stride_offset] -= 1
					printV(3, "Mem instruction: ", str(ins))
					cont_flag = 1
				elif prevInsZeroStride == "False" and strideDens[self.memBlockSize] > 0:
					printV(3, "load load case 2")
					strideDens[self.memBlockSize] -= 1
					prevInsZeroStride = "True"
					num_zero_strides -= 1
					if(avail_arr_cnts[zero_stride_offset] > 0) :
						avail_arr_cnts[zero_stride_offset] -= 1
					printV(3, "Mem instruction: ", str(ins))
					cont_flag = 1
				else :
					printV(3, strideDens)
					printV(3, "Num_zero_strides not zero, could not find a suitable placement though - Proceed to get a different assignment")
					#prevInsZeroStride = "False"
			elif "load" in ins.insType and prevInsCategory == "store":
				printV(3, "store load")
				prevInsCategory = "load"
				operand.reg = self.registers.zeroStrideR[0]
				operand.offset = 0																								
				if strideDens[self.memBlockSize] > 0:
					printV(3, "store load case 1")
					strideDens[self.memBlockSize] -= 1													
					num_zero_strides -= 1
					prevInsZeroStride = "True"
					if(avail_arr_cnts[zero_stride_offset] > 0) :
						avail_arr_cnts[zero_stride_offset] -= 1
					printV(3, "Mem instruction: ", str(ins))
					cont_flag = 1
			elif ins.insType == "store":
				printV(3, "store curr")
				prevInsCategory = "store"
				if prevInsZeroStride == "True":
					printV(3, "store curr case 1")
					if strideDens[self.memBlockSize] > 0:
						strideDens[self.memBlockSize] -= 1 #Why is this being decremented if it is being decremented later?
				#prevInsZeroStride = "False"
			else:
				printV(3, "Invalid case for mems, num_zero_strides = ", num_zero_strides)
				num_zero_strides = -1 #WHy is it being decremented?
                return (operand,
                       prevInsCategory, prevInsZeroStride,
                       strideDens, num_zero_strides, avail_arr_cnts,
                        cont_flag)



class Memory_MA (Memory):

        def assignStrides_MA(self):
                """We use the profile information to assign global and local strides 
	
		    Args:
		No arguments are needed 

		    Returns:
		No return arguments

		"""

                #Global Stride Calculation
                total_mem_inst, strideDens = self.prepGlobalDens()

                #Local Stride Calculations
                sorted_localStrideDens, num_zero_strides = self.prepLocalDens(total_mem_inst)

                #Array Steam Calcutations
                avail_arr_cnts, zero_stride_offset = self.prepArrays(sorted_localStrideDens)

		#Prepping for main loop
		#prevInsCategory = None
                prevOffset = None
		#prevInsZeroStride = "False"
	
                array_offset_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.array_used_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.minArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
		self.maxArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]

                prevArr = 0
                running_arr_ct = 0

                #Main for loop
                for ins in self.insList:
                        for operand in ins.operands:
                                if operand.isMem():
                                        printV(3, "here")
                                        if prevOffset == None:
                                                printV(3, "prevOffset none case")
                                                prevOffset = 0
                                                operand.reg = self.registers.strideR[0]
                                                operand.offset = 0
                                                prevArr = 0
                                                array_offset_list[prevArr] = 0
                                                self.array_used_list[prevArr] = 1
						avail_arr_cnts[prevArr] -= 1
                                                running_arr_ct += 1
					
					elif avail_arr_cnts[prevArr] <= 0:
						printV(3, "I have run out of the local stride array, pick a new one")
						tempArr = -1
						for arrs in range(0, self.numAvailableArrays-1):
							if avail_arr_cnts[arrs] > 0:
								tempArr = arrs
						if tempArr == -1:
							printV(3, "Warning, run out of all local arrays but still have mem instructions")
							tempArr = random.randint(0, (self.numAvailableArrays-1))
						if(self.array_used_list[tempArr] == 0) :
	                                                running_arr_ct += 1
						self.array_used_list[tempArr] = 1
						tempOffset = (array_offset_list[tempArr] + self.memBlockSize)
						if(abs(tempOffset) >= self.MAX_OFFSET) :
         	                                	modtempOffset = abs(tempOffset) % self.MAX_OFFSET
	                                                if(tempOffset < 0) :
                                                        	tempOffset = -modtempOffset
                                                        else :
                                                        	tempOffset = modtempOffset
						prevArr = tempArr
						prevOffset = tempOffset
						operand.reg = self.registers.strideR[prevArr]
						operand.offset = tempOffset
						self.maxArrOffset[prevArr] = max([tempOffset, self.maxArrOffset[prevArr]])
						array_offset_list[prevArr] = operand.offset
						if avail_arr_cnts[prevArr] > 0:
							avail_arr_cnts[prevArr] -= 1	
						if strideDens[self.memBlockSize] > 0 :
							strideDens[self.memBlockSize] -= 1
                                        else:
                                                tempOffset = self.nextStride(strideDens)
                                                printV(3, "prevoffset not none, tempoffset = ", tempOffset)
                                                if(abs(tempOffset) >= self.memBlockSize) :
                                                        printV(3, "case 1")
							trials = 0
							while trials < 10:
                                                        	tempArr = random.randint(0, (self.numAvailableArrays-1))
								if(avail_arr_cnts[tempArr] > 0) :
									break
								if trials == 9:
									tempArr = prevArr
                                                        if(self.array_used_list[tempArr] == 0) :
                                                                running_arr_ct += 1
                                                        self.array_used_list[tempArr] = 1
                                                        tempOffset = (array_offset_list[tempArr] + self.memBlockSize)
                                                        if(abs(tempOffset) >= self.MAX_OFFSET) :
                                                                modtempOffset = abs(tempOffset) % self.MAX_OFFSET
                                                                if(tempOffset < 0) :
                                                                        tempOffset = -modtempOffset
                                                                else :
                                                                        tempOffset = modtempOffset

                                                        prevArr = tempArr
							prevOffset = tempOffset
                                                        operand.reg = self.registers.strideR[prevArr]
                                                        operand.offset = tempOffset
							self.maxArrOffset[prevArr] = max([tempOffset, self.maxArrOffset[prevArr]])
                                                        array_offset_list[prevArr] = operand.offset
							avail_arr_cnts[prevArr] -= 1
                                                        if strideDens[self.memBlockSize] > 0 :
                                                                strideDens[self.memBlockSize] -= 1
                                                else :
                                                        printV(3, "case 2")
                                                        prevOffset = array_offset_list[prevArr]
                                                        printV(3, "prevOffset = ", prevOffset)
                                                        if(tempOffset + prevOffset) < 0:
                                                                self.minArrOffset[prevArr] = min([(prevOffset + tempOffset), self.minArrOffset[prevArr]])
                                                                printV(3, "minArrOffset[prevArr] is ", self.minArrOffset[prevArr])

                                                        if(abs(tempOffset + prevOffset) > self.MAX_OFFSET) :
                                                                printV(3, "abs of tempOffset and prevOffset is greater than self.MAX_OFFSET, ", (tempOffset + prevOffset))
                                                                if strideDens[self.memBlockSize] > 0 :
                                                                        strideDens[self.memBlockSize] -= 1
                                                                modtempOffset = abs(tempOffset + prevOffset) % self.MAX_OFFSET
                                                                if((prevOffset + tempOffset) < 0) :
                                                                        prevOffset = -modtempOffset
                                                                else :
                                                                        prevOffset = modtempOffset
                                                        else:
                                                                if strideDens[tempOffset] > 0:
                                                                        strideDens[tempOffset] -= 1
                                                                prevOffset += tempOffset

							self.maxArrOffset[prevArr] = max([prevOffset, self.maxArrOffset[prevArr]])
                                                        operand.offset = prevOffset
                                                        operand.reg = self.registers.strideR[prevArr]
                                                        array_offset_list[prevArr] = prevOffset
							avail_arr_cnts[prevArr] -= 1

                                        printV(3, "Mem instruction: ", str(ins))
                                        printV(3, array_offset_list)
					printV(3, avail_arr_cnts)
                                        printV(3, "\n")
                return False




class Memory_ZL (Memory):

        def assignStrides_ZL(self):
                """We use the profile information to assign global and local strides 
	
		    Args:
		No arguments are needed 

		    Returns:
		No return arguments

		"""

                #Global Stride Calculation
                total_mem_inst, strideDens = self.prepGlobalDens()

		#Local Stride Calculations
                sorted_localStrideDens, num_zero_strides = self.prepLocalDens(total_mem_inst)


		#Prepping for main loop
		prevInsCategory = None
                prevOffset = None
		prevInsZeroStride = "False"
				
                array_offset_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.array_used_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.minArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
		self.maxArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
				
                prevArr = 0
                running_arr_ct = 0

                #Main for loop
                for ins in self.insList:
                        for operand in ins.operands:
                                if operand.isMem():
                                        #avail_arr_cnts is not used by ZL
                                        #however, the function is identical
                                        #Therefore we declare a dummy here
                                        avail_arr_cnts = [0, 0, 0, 0, 0, 0, 0, 0]
                                        zero_stride_offset = 0
                                        operand, prevInsCategory, prevInsZeroStride, strideDens, num_zero_strides, avail_arr_cnts, cont_flag = self.attemptAssignZero(ins, operand, prevInsCategory, prevInsZeroStride, strideDens, num_zero_strides, avail_arr_cnts, zero_stride_offset)
                                        if(cont_flag == 1):
                                                continue
                                        printV(3, "here")
                                        if prevOffset == None:
                                                printV(3, "prevOffset none case")
                                                prevOffset = 0
                                                operand.reg = self.registers.strideR[0]
                                                operand.offset = 0
                                                prevArr = 0
                                                array_offset_list[prevArr] = 0
                                                self.array_used_list[prevArr] = 1
                                                
						running_arr_ct += 1
						prevInsZeroStride = "False"
                                        else:
						for x in range(10):	
							printV(3, "x is ", x)
                                                	tempOffset = self.nextStride(strideDens)
							#if(num_zero_strides > 0) and (x != 9):
							#	continue

                                                	printV(3, "prevoffset not none, tempoffset = ", tempOffset)
                                                	if(abs(tempOffset) >= self.memBlockSize) :
                                                        	if(num_zero_strides > 0) and (x != 9):
                                                                	continue

                                                        	printV(3, "case 1")
                                                        	tempArr = random.randint(0, (self.numAvailableArrays-1))
                                                        	if(self.array_used_list[tempArr] == 0) :
                                                                	running_arr_ct += 1
                                                        	self.array_used_list[tempArr] = 1
                                                        	tempOffset = (array_offset_list[tempArr] + self.memBlockSize)
                                                        	if(abs(tempOffset) >= self.MAX_OFFSET) :
                                                                	modtempOffset = abs(tempOffset) % self.MAX_OFFSET
                                                                	if(tempOffset < 0) :
                                                                        	tempOffset = -modtempOffset
                                                                	else :
                                                                        	tempOffset = modtempOffset

                                                        	prevArr = tempArr
								prevOffset = tempOffset
                                                        	operand.reg = self.registers.strideR[prevArr]
                                                        	operand.offset = tempOffset
								self.maxArrOffset[prevArr] = max([tempOffset, self.maxArrOffset[prevArr]])
                                                        	array_offset_list[prevArr] = operand.offset
                                                        	if strideDens[self.memBlockSize] > 0 :
                                                                	strideDens[self.memBlockSize] -= 1
								prevInsZeroStride = "False"
								break
                                                	else :
                                                        	printV(3, "case 2")
                                                        	prevOffset = array_offset_list[prevArr]
                                                        	printV(3, "prevOffset = ", prevOffset)
                                                        	if(tempOffset + prevOffset) < 0:
                                                                	self.minArrOffset[prevArr] = min([(prevOffset + tempOffset), self.minArrOffset[prevArr]])
                                                                	printV(3, "minArrOffset[prevArr] is ", self.minArrOffset[prevArr])

                                                        	if(abs(tempOffset + prevOffset) > self.MAX_OFFSET) :
                                                                	printV(3, "abs of tempOffset and prevOffset is greater than self.MAX_OFFSET, ", (tempOffset + prevOffset))
                                                                	if strideDens[self.memBlockSize] > 0 :
                                                                        	strideDens[self.memBlockSize] -= 1
                                                                	modtempOffset = abs(tempOffset + prevOffset) % self.MAX_OFFSET
                                                                	if((prevOffset + tempOffset) < 0) :
                                                                        	prevOffset = -modtempOffset
                                                                	else :
                                                                        	prevOffset = modtempOffset
                                                        	else:
									if prevInsZeroStride == "True":
										if strideDens[self.memBlockSize] > 0 :
                                                                                	strideDens[self.memBlockSize] -= 1
                                                                	else:
										if strideDens[tempOffset] > 0:
                                                                        		strideDens[tempOffset] -= 1
                                                                	prevOffset += tempOffset

								self.maxArrOffset[prevArr] = max([prevOffset, self.maxArrOffset[prevArr]])
                                                        	operand.offset = prevOffset
                                                        	operand.reg = self.registers.strideR[prevArr]
                                                        	array_offset_list[prevArr] = prevOffset
								prevInsZeroStride = "False"
								break
						if x == 9:
							printV(3, "I am here, moving on to next instruction")
                                        printV(3, "Mem instruction: ", str(ins))
                                        printV(3, array_offset_list)
                                        printV(3, "\n")
                return False

class Memory_ZS (Memory):

        def assignStrides_ZS(self):
                """We use the profile information to assign global and local strides 
	
		    Args:
		No arguments are needed 

		    Returns:
		No return arguments

		"""

                #Global Stride Calculation
                total_mem_inst, strideDens = self.prepGlobalDens()

		#Local Stride Calculations
                sorted_localStrideDens, num_zero_strides = self.prepLocalDens(total_mem_inst)

                #Local Array Calculations
                avail_arr_cnts, zero_stride_offset = self.prepArrays(sorted_localStrideDens)

		#Prepping for main loop
		prevInsCategory = None
                prevOffset = None
		prevInsZeroStride = "False"
				
                array_offset_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.array_used_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.minArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
		self.maxArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
				
                prevArr = 0
                running_arr_ct = 0

                #Main for loop
                for ins in self.insList:
                        for operand in ins.operands:
                                if operand.isMem():
                                        operand, prevInsCategory, prevInsZeroStride, strideDens, num_zero_strides, avail_arr_cnts, cont_flag = self.attemptAssignZero(ins, operand, prevInsCategory, prevInsZeroStride, strideDens, num_zero_strides, avail_arr_cnts, zero_stride_offset)
                                        if(cont_flag == 1):
                                                continue
                                        printV(3, "here")
                                        if prevOffset == None:
                                                printV(3, "prevOffset none case")
                                                prevOffset = 0
                                                operand.reg = self.registers.strideR[0]
                                                operand.offset = 0
                                                prevArr = 0
                                                array_offset_list[prevArr] = 0
                                                self.array_used_list[prevArr] = 1
						avail_arr_cnts[prevArr] -= 1
                                                running_arr_ct += 1
						prevInsZeroStride = "False"
					elif avail_arr_cnts[prevArr] <= 0:
						printV(3, "I have run out of the local stride array, pick a new one")
						tempArr = -1
						for arrs in range(0, self.numAvailableArrays):
							if avail_arr_cnts[arrs] > 0:
								tempArr = arrs
						if tempArr == -1:
							printV(3, "Warning, run out of all local arrays but still have mem instructions")

						if(self.array_used_list[tempArr] == 0) :
							running_arr_ct += 1
						self.array_used_list[tempArr] = 1
						tempOffset = (array_offset_list[tempArr] + self.memBlockSize)
						if(abs(tempOffset) >= self.MAX_OFFSET) :
							modtempOffset = abs(tempOffset) % self.MAX_OFFSET
							if(tempOffset < 0) :
								tempOffset = -modtempOffset
							else :
								tempOffset = modtempOffset
						prevArr = tempArr
						prevOffset = tempOffset
						operand.reg = self.registers.strideR[prevArr]
						operand.offset = tempOffset
						self.maxArrOffset[prevArr] = max([tempOffset, self.maxArrOffset[prevArr]])
						array_offset_list[prevArr] = operand.offset
						avail_arr_cnts[prevArr] -= 1
						if strideDens[self.memBlockSize] > 0 :
							 strideDens[self.memBlockSize] -= 1
                                        else:
						for x in range(10):	
							printV(3, "x is ", x)
                                                	tempOffset = self.nextStride(strideDens)
							#if(num_zero_strides > 0) and (x != 9):
							#	continue

                                                	printV(3, "prevoffset not none, tempoffset = ", tempOffset)
                                                	if(abs(tempOffset) >= self.memBlockSize) :
                                                        	if(num_zero_strides > 0) and (x != 9):
                                                                	continue

                                                        	printV(3, "case 1")
                                                        	#tempArr = random.randint(0, (self.numAvailableArrays-1))
								trials = 0
								while trials < 10:
									tempArr = random.randint(0, (self.numAvailableArrays - 1))
									if(avail_arr_cnts[tempArr] > 0) :
										break
									if trials == 9:
										tempArr = prevArr
                                                        	if(self.array_used_list[tempArr] == 0) :
                                                                	running_arr_ct += 1
                                                        	self.array_used_list[tempArr] = 1
                                                        	tempOffset = (array_offset_list[tempArr] + self.memBlockSize)
                                                        	if(abs(tempOffset) >= self.MAX_OFFSET) :
                                                                	modtempOffset = abs(tempOffset) % self.MAX_OFFSET
                                                                	if(tempOffset < 0) :
                                                                        	tempOffset = -modtempOffset
                                                                	else :
                                                                        	tempOffset = modtempOffset

                                                        	prevArr = tempArr
								prevOffset = tempOffset
                                                        	operand.reg = self.registers.strideR[prevArr]
                                                        	operand.offset = tempOffset
								self.maxArrOffset[prevArr] = max([tempOffset, self.maxArrOffset[prevArr]])
                                                        	array_offset_list[prevArr] = operand.offset
								avail_arr_cnts[prevArr] -= 1
                                                        	if strideDens[self.memBlockSize] > 0 :
                                                                	strideDens[self.memBlockSize] -= 1
								prevInsZeroStride = "False"
								break
                                                	else :
                                                        	printV(3, "case 2")
                                                        	prevOffset = array_offset_list[prevArr]
                                                        	printV(3, "prevOffset = ", prevOffset)
                                                        	if(tempOffset + prevOffset) < 0:
                                                                	self.minArrOffset[prevArr] = min([(prevOffset + tempOffset), self.minArrOffset[prevArr]])
                                                                	printV(3, "minArrOffset[prevArr] is ", self.minArrOffset[prevArr])

                                                        	if(abs(tempOffset + prevOffset) > self.MAX_OFFSET):
                                                                	printV(3, "abs of tempOffset and prevOffset is greater than self.MAX_OFFSET, ", (tempOffset + prevOffset))
                                                                	if strideDens[self.memBlockSize] > 0 :
                                                                        	strideDens[self.memBlockSize] -= 1
                                                                	modtempOffset = abs(tempOffset + prevOffset) % self.MAX_OFFSET
                                                                	if((prevOffset + tempOffset) < 0) :
                                                                        	prevOffset = -modtempOffset
                                                                	else :
                                                                        	prevOffset = modtempOffset
                                                        	else:
									if prevInsZeroStride == "True":
										if strideDens[self.memBlockSize] > 0 :
                                                                                	strideDens[self.memBlockSize] -= 1
                                                                	else:
										if strideDens[tempOffset] > 0:
                                                                        		strideDens[tempOffset] -= 1
                                                                	prevOffset += tempOffset

								self.maxArrOffset[prevArr] = max([prevOffset, self.maxArrOffset[prevArr]])
                                                        	operand.offset = prevOffset
                                                        	operand.reg = self.registers.strideR[prevArr]
                                                        	array_offset_list[prevArr] = prevOffset
								prevInsZeroStride = "False"
								avail_arr_cnts[prevArr] -= 1
								break
						if x == 9:
							printV(3, "I am here, moving on to next instruction")
                                        #printV(3, "Mem instruction: ", str(ins))
                                        printV(3, array_offset_list)
					printV(3, avail_arr_cnts)
                                        printV(3, "\n")
                return False

