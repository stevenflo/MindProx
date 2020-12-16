class CodeGenerator:

	memBlockSize = 256
	MAX_OFFSET = 32768

	def __init__(self):
		bblList = []
		insList = []
		insMix = None
		self.raw = None
		stride = None
		staticBbls = None
		dynamicBbls = None
		avrBblSize = None
		avrSuccBbls = None
		brTrans = None
		dataFootprint = None
		LocalStride = None
                array_used_list = []
                minArrOffset = []
		maxArrOffset = []
                numAvailableArrays = None

	def generateBbls(self):
		raise NotImplementedError("Please Implement this method")

	def generateBranchBehavior(self):
		raise NotImplementedError("Please Implement this method")

	def assignDependencies(self):
		raise NotImplementedError("Please Implement this method")

	def assignStrides(self):
		raise NotImplementedError("Please Implement this method")

	def generateCode(self):
		raise NotImplementedError("Please Implement this method")












