import os
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import OrderedDict
from math import sqrt
from nltk.corpus import stopwords
from copy import deepcopy
ps = PorterStemmer()

stop_words=set([])
stop_words = set(stopwords.words('english'))

stop_words.update(['.','-',',',"''", '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])


def findDocuments(queryWords,wordsResult,fileCount,fileNames):
	
	documents=[]
	flag=0
	files=[]
	files.extend(range(fileCount))
	for word in queryWords:
		try:
			uselessFiles=[]
			string = wordsResult[word]
			rem=fileCount-len(string)
			zeroes2="0"*rem
			files = [e for e in files if e <len(string)]

			for value in files:
				if(string[value]=='0'):				
					uselessFiles.append(value)
			files=list(set(files) - set(uselessFiles))
		except:
			print "Combinations of words not found"
			flag=1
			break
	if flag!=1:
		return files


def tokenization(line):
	word_tokens=word_tokenize(line) 
	final_words=[]
	for w in word_tokens:
		if w not in stop_words:
			k=str(ps.stem(w))
			final_words.append(k)	
	return final_words

def validate(queryWords,fileNum,wordsPosition):
	positionsData=[]
	final=[]
	for i  in range(len(queryWords)):
		tempData=deepcopy(wordsPosition[queryWords[i]][str(fileNum)])

		tempData[:] = [x - i for x in tempData]
		positionsData.append(tempData)
	finalResult=intersect(positionsData)
	if len(finalResult)==0:
		return [0]
	# print finalResult
	for value in finalResult:
		finalResult1=[]
		for i in range(len(queryWords)):
			finalResult1.append(value + i)
		final.append(finalResult1)
	return [1,final]

def intersect(d):
	return list(set.intersection(*map(set, d)))

def phraseQuery(queryWords,existingFiles,wordsPosition):
	word=queryWords[0]
	resultantFiles=[]
	for fileNum in existingFiles:
		exist=validate(queryWords,fileNum,wordsPosition)
		# print exist
		if exist[0]==1:
			resultantFiles.append(fileNum)
	return [resultantFiles]


def cosinesimilarity(inp,invDocFre,logFre,fileNames,outputFiles,tf_idf_qword_doc):
	# print "---------------------"
	search_query=tokenization(inp)
	tfidfwordQuery={}
	for i in set(search_query):
		
		if i in invDocFre:
		
			tfidfwordQuery[i] = ( float(search_query.count(i))/float(len(search_query)) ) * invDocFre[i]

		else:
		
			tfidfwordQuery[i] =0	
	
	tf_idf_cosine={}
	for i in outputFiles:
		sumq=0
		qweryd=0
		docd=0
		for word in search_query:
			# print word,tf_idf_qword_doc[i]
			sumq=sumq+tfidfwordQuery[word]*tf_idf_qword_doc[i][word]
			qweryd=qweryd+tfidfwordQuery[word]*tfidfwordQuery[word]
			docd=docd+tf_idf_qword_doc[i][word]*tf_idf_qword_doc[i][word]
		denom=float(sqrt(qweryd)*sqrt(docd))
		divi=float(float(sumq)/float(denom))
		tf_idf_cosine[i]=divi
	
	odlist=list()
	od = OrderedDict(sorted(tf_idf_cosine.items(), key=lambda(k,v):(v,k)  , reverse=True ) )
	
	

	return od

def querySearch(inp,invDocFre,logFre,fileNames):
	
	search_query=tokenization(inp)
	tf_idf={}
	tf_idf_qword_doc={}
	
	for query in search_query:
		# tf_idf_qword_doc[query]={}
		if query in logFre:
			docid_key=logFre[query].keys()
			# print query
			for docid in docid_key:
				
				if fileNames[int(docid)] in tf_idf:

					tf_idf[fileNames[int(docid)]]=tf_idf[fileNames[int(docid)]]+(logFre[query][docid]*invDocFre[query])
					tf_idf_qword_doc[fileNames[int(docid)]][query]=logFre[query][docid]*invDocFre[query]
					
				if fileNames[int(docid)] not in tf_idf:
					tf_idf[fileNames[int(docid)]]=logFre[query][docid]*invDocFre[query]
					tf_idf_qword_doc[fileNames[int(docid)]]={}

					tf_idf_qword_doc[fileNames[int(docid)]][query]=logFre[query][docid]*invDocFre[query]

					# if query=='nation':
					# 	print "something"
	for i in tf_idf_qword_doc:
		for query in search_query:
			if query not in tf_idf_qword_doc[i]:
				tf_idf_qword_doc[i][query]=0

	odlist=list()
	od = OrderedDict(sorted(tf_idf.items(), key=lambda(k,v):(v,k)  , reverse=True ) )
	
	# if len(od)<=5:
	# 	for i in od:
	# 		print i ," -> " ,od[i]
	# if len(od)>6:
	# 	docidS=od.keys()
	# 	for i in range(0,6):
	# 		print docidS[i]," -> ",od[docidS[i]]
	# print "-------------------"
	return od,tf_idf_qword_doc



ilf=open('inverseLogFre.pkl','rb')
invDocFre=pickle.load(ilf)

lf=open('logFre.pkl','rb')
logFre=pickle.load(lf)

fn=open('fileNames.pkl','rb')
fileNames=pickle.load(fn)

summ=open('summary.pkl','rb')
summarY=pickle.load(summ)

wp=open('wordsPosition.pkl','rb')
wordsPosition=pickle.load(wp)

# wr=open('wordsResult,pkl','rb')
# wordsResult=pickle.load(wr)

inp=raw_input("Enter the string : ")
outputFiles,tf_idf_qword_doc=querySearch(inp,invDocFre,logFre,fileNames)
finout=cosinesimilarity(inp,invDocFre,logFre,fileNames,outputFiles,tf_idf_qword_doc)

print '\n'

m=[]

if len(finout)<=5:
		docidS=finout.keys()
		for j in finout:
			print j ," -> " ,finout[j]
			print summarY[j]
			print "\n"

if len(finout)>6:
	docidS=finout.keys()
	for k in range(0,4):
		
		
		print summarY[docidS[k]]
		print docidS[k]
		print "\n"

if len(finout)==0:
	print "No documents were found"



queryWords=tokenization(inp)


for k in range(0,len(finout)):

	for word in queryWords:
		j=0
		# print fileNames.index(docidS[k]),wordsPosition[word]
		# print '\n'
		if word in wordsPosition:
				if str(fileNames.index(docidS[k])) not in wordsPosition[word]:
					j=1
					break
	if j==0:
		m.append(fileNames.index(docidS[k]))

phraseResults=phraseQuery(queryWords,m, wordsPosition)
phraseFiles=[]
for i in phraseResults[0]:
 	phraseFiles.append(fileNames[i])

count=0
pres=0.0
ite=1
print "Relavent Documents : ", len(phraseFiles)
print "Retrived Documents",len(finout)
for i in finout:

	if i in phraseFiles:

		count+=1
		pres=pres+(float(count)/float(ite))
		# print pres

	ite=ite+1
pres=pres/float(count)

print "average precision",pres