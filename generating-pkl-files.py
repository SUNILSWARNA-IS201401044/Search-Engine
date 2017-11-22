import sys
import os
import re
from collections import OrderedDict
from math import log10
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from filereading import Total_Files
import pickle
ps = PorterStemmer()
#stop_words=set(stopwords.words('english'))
stop_words=set([])
stop_words.update(['.','-',',',"''", '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])

def findPosition(word,stemWords):
	frequency=[]
	for i in range(len(stemWords)):
		if word==stemWords[i]:
			frequency.append(i)
	return frequency


def wordPosi(stemWords,fileCount,text):

	stemWords=list(set(stemWords))
	for word in stemWords:
		if word not in wordsPosition:
			wordsPosition[word]={}
			positions=findPosition(word,text)
			wordsPosition[word][str(fileCount)]=positions
		else:
			positions=findPosition(word,text)
			wordsPosition[word][str(fileCount)]=positions


def formDict(wordsResult,stemWords,fileCount):

	zeroes1="0"*fileCount
	stemWords=list(set(stemWords))
	for word in stemWords:
		if word not in wordsResult:
			temp=zeroes1+str("1")	
			wordsResult[word]=temp
		else:
			rem=fileCount-len(wordsResult[word])
			zeroes2="0"*rem
			temp=zeroes2+str("1")
			wordsResult[word]=wordsResult[word]+temp
			
	return wordsResult


def tokenization(line):
	word_tokens=word_tokenize(line) 
	final_words=[]
	for w in word_tokens:
		if w not in stop_words:
			k=str(ps.stem(w))
			final_words.append(k)	
	return final_words

def querySearch(inp):
	
	search_query=tokenization(inp)
	tf_idf={}
	for query in search_query:
		if query in logFre:
			docid_key=logFre[query].keys()
			
			for docid in docid_key:
				if fileNames[int(docid)] in tf_idf:
					tf_idf[fileNames[int(docid)]]=tf_idf[fileNames[int(docid)]]+(logFre[query][docid]*invDocFre[query])
				if fileNames[int(docid)] not in tf_idf:
					tf_idf[fileNames[int(docid)]]=logFre[query][docid]*invDocFre[query]
	odlist=list()
	od = OrderedDict(sorted(tf_idf.items(), key=lambda(k,v):(v,k)  , reverse=True ) )
	if len(od)<=5:
		for i in od:
			print i ," -> " ,od[i]
	if len(od)>6:
		docidS=od.keys()
		for i in range(0,6):
			print docidS[i]," -> ",od[docidS[i]]

#folder=sys.argv[1]
data={}
wordsResult={}
wordsPosition={}
fileNames=[]
fileCount=0

for file1 in Total_Files:
	f=open(str(file1),"r")
	content=f.read()
	title=re.findall(r'(?<=<TITLE>).*?(?=</TITLE>)', content)
	text=re.findall('<TEXT>\n(.*?)</TEXT>\n', content,re.S)
	fileNames.append(str(file1))
	text=text[0][:-1]
	title=title[0][:-1]
	key=str(file1)+":::"+str(title)
	data[key]=text	
	stemWords=tokenization(str(text))
	# if file1=='en.13.1.5.2009.6.2':
	# 	print stemWords
	formDict(wordsResult,stemWords,fileCount)
	wordPosi(stemWords,fileCount,stemWords)
	fileCount+=1
	if fileCount%1000==0:
		print fileCount
	
print "-----------------"
print "-----------------"

logFre={}
invDocFre={}

for key in wordsPosition:
	value= wordsResult[key]
	logFre[key]={}
	docIds=[m.start() for m in re.finditer('1',value)]
	invDocFre[key]=float(log10(float(len(fileNames))/float(len(docIds))))
	for docId in docIds:
		logFre[key][str(docId)]=1+log10(len(wordsPosition[key][str(docId)]))

# for word in wordsPosition:
# 	wordsPosition[word].keys().sort()

# Binary_Text=open("Binary_Text.txt","w")

# for word in wordsPosition:
# 	Binary_Text.write(word)
# 	Binary_Text.write('\n')
# 	Binary_Text.write(wordsResult[word])
# 	Binary_Text.write('\n')

# Binary_Text.close()


output1=open('logFre.pkl','wb')
output2=open('inverseLogFre.pkl','wb')
output3=open('fileNames.pkl','wb')
output4=open('wordsPosition.pkl','wb')
output5=open('wordsResult,pkl','wb')
pickle.dump(logFre,output1)
pickle.dump(invDocFre,output2)
pickle.dump(fileNames,output3)
pickle.dump(wordsPosition,output4)
pickle.dump(wordsResult,output5)
output5.close()
output4.close()
output3.close()
output2.close()
output1.close()

# pklFile=open('inverseLogFre.pkl','rb')
# data1=pickle.load(pklFile)

# #inp=tokenization('skokie')
# #print wordsPosition[inp[0]]
# print "-----------------"
# print "-----------------"
# #print wordsPosition["illinois"]
# #Skokie, Illinois
inp=raw_input("Enter the input String : ")
querySearch(inp)





