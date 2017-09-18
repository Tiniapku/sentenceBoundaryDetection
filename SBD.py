import sys
from sklearn import tree
from collections import defaultdict
class sentenceBoundaryDetection(object):
	def __init__(self):
		self.featureList = []
		self.category = []
		self.clf = tree.DecisionTreeClassifier()
		self.total = 0
		self.right = 0
		self.precision = 0.0
		self.output = []
		self.true = 0
		self.truepositive = 0
		self.alltrue = 0
		self.address = ["Mr", "Ms", "Dr", "Mrs", "Jr","Messrs", "Prof"]
		self.leftSet = defaultdict(int)
		self.rightSet = defaultdict(int)


	def processTrainData(self, trainData):
		"""
		Features:
		- Word to the left of .(L) type: String
		- Word to the right of .(R) type: String
		- Length of L < 3. Type: Bool
		- Is L capitalized. Type: Bool
		- Is R Capicalized. Type: Bool
		self-chosen:
		- occur as ... Type: Bool
		- R is left quote Type: Bool
		- if it is address. Bool

		"""
		waitingForRight = False
		feature = []
		lasttag = ""
		for entry in trainData.readlines():
			entry = entry.strip()
			num, word, tag = entry.split(' ')
			if waitingForRight and feature:
				if lasttag != "EOS":
					self.rightSet[word] += 1
				self.setRightFeature(feature, word)
				waitingForRight = False
			if tag != "TOK":
				if tag == "EOS":
					self.category.append(True)
				else:
					Lword = word.replace(".", "")
					self.leftSet[Lword] += 1
					self.category.append(False)
				waitingForRight = True
				if feature:
					self.featureList.append(feature)
				feature = self.getFeature(word)
				lasttag = tag
		if feature:
			self.featureList.append(feature)
		self.refineFeature(self.featureList, False, False)

	def refineFeature(self, featureList, test5, test3):
		for i in xrange(len(featureList)):
			Lword = featureList[i][0]
			Rword = featureList[i][1]
			a = self.leftSet[Lword]
			b = self.rightSet[Rword]
			featureList[i][0] = a
			featureList[i][1] = 0
			if test5:
				featureList[i] = featureList[i][:5]
			elif test3:
				featureList[i] = featureList[i][5:]

	def processTestData(self, testData):
		testList = []
		answer = []
		waitingForRight = False
		feature = []
		for entry in testData.readlines():
			entry = entry.strip()
			num, word, tag = entry.split(' ')
			if waitingForRight and feature:
				self.setRightFeature(feature, word)
				waitingForRight = False
			if self.finddot(word):
				answer.append(True if tag == "EOS" else False)
				waitingForRight = True
				if feature:
					testList.append(feature)
				feature = self.getFeature(word)
		if feature:
			testList.append(feature)
		self.refineFeature(testList, False, False)
		return testList, answer


	def finddot(self, word):
		
		return word[-1] == "."

	def classify(self, feature, answer):
		tagList = self.clf.predict(feature)
		self.total = len(feature)
		cur = 0
		for tag in tagList:
			if tag == answer[cur]:
				self.right += 1
			#else:
				#print feature[cur], "mytag: ", tag, "rightanswer: ", answer[cur]
			cur += 1
			self.output.append(tag)
		#print self.output

	def getPrecision(self):

		return "Correct %: ", self.right * 1.0 / self.total,"Precision: ", self.truepositive * 1.0/ self.true, "Recall: ", self.truepositive * 1.0 / self.alltrue

	def getFeature(self, word):
		Lword = word.replace(".", "")
		#return [Lword, "", L < 3, Lword[0].isupper(), False, R, word[-3:] == '...', False]
		return [Lword, 0.0, len(Lword) < 3, len(Lword) > 0 and Lword[0].isupper(), False, len(word) > 1 and self.finddot(word[:-1]), False, True if Lword in self.address else False]

	def setRightFeature(self, feature, word):
		feature[1] = word
		feature[4] = word[0].isupper()
		feature[6] = word[0] == '"'

	def training(self):
		self.clf = self.clf.fit(self.featureList, self.category)

	def out(self, test, f):
		cur = 0
		outList = ""
		di = {"EOS": True, "NEOS": False}
		for entry in test.readlines():
			num, word, tag = entry.split(' ')
			if self.finddot(word):
				if di[tag.strip()]:
					self.alltrue += 1
				if self.output[cur]:
					self.true += 1
					if di[tag.strip()]:
						self.truepositive += 1
				outList += " ".join([num, word, "EOS" if self.output[cur] else "NEOS"]) + '\n'
				#if self.output[cur] != di[tag.strip()]:
					#print num, word, tag.strip(), self.output[cur]
				cur += 1
			else:
				outList += entry
		f.write(outList)

	def debug(self, test):
		cur = 0
		di = {"EOS": True, "NEOS": False}
		for entry in test.readlines():
			num, word, tag = entry.split(' ')
			if self.finddot(word):
				if di[tag.strip()]:
					self.alltrue += 1
				if self.output[cur]:
					self.true += 1
					if di[tag.strip()]:
						self.truepositive += 1
				if self.output[cur] != di[tag.strip()]:
					Lword = word.replace(".","")
					print num, word, tag.strip(), self.output[cur], self.leftSet[Lword]
				cur += 1
if __name__ == '__main__':
	train = open(sys.argv[1], 'r')
	mySBD = sentenceBoundaryDetection()
	mySBD.processTrainData(train)
	train.close()
	mySBD.training()
	test = open(sys.argv[2], 'r')
	testList, answer = mySBD.processTestData(test)
	mySBD.classify(testList, answer)
	test.close()
	test = open(sys.argv[2], 'r')
	f = open('SBD.test.out', 'w')
	mySBD.out(test, f)
	#mySBD.debug(test)
	test.close()
	f.close()
	print mySBD.getPrecision()