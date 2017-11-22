from filereading import Total_Files
import numpy as np
import math
import pickle
from nltk.corpus import stopwords
import sys
import os
import re
import nltk.data
from nltk.tokenize import RegexpTokenizer,sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
ps = PorterStemmer()

def load(file1,file2):
	output1=open(file1,'rb')
	output2=open(file2,'rb')
	data1=pickle.load(output1)
	data2=pickle.load(output2)
	return [data1,data2]

def readData(fileName):
	f=open(fileName,"r")
	content=f.read()
	title=re.findall(r'(?<=<TITLE>).*?(?=</TITLE>)', content)
	text=re.findall('<TEXT>\n(.*?)</TEXT>\n', content,re.S)
	text=text[0][:-1]
	title=title[0][:-1]
	return [title,text]

def tokenization(line):
	stopWords=set(stopwords.words('english'))
	word_tokens=word_tokenize(line) 
	final_words=[]
	for w in word_tokens:
		if w not in stopWords:
			k=str(ps.stem(w))
			final_words.append(k)	
	return final_words

def idfModifiedCosine(str1,str2,inverseLogFre):

	stopWords=set(stopwords.words('english'))
	unwantedChars= (['`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '=', '-', '{', '}', '[', ']', '|', '"', ':', ';', '<', '>', '?', ',', '.', '/'])
	
	dic1 = {}
	dic2 = {}
	str1=tokenization(str1)
	str2=tokenization(str2)

	for i in set(tuple(str1)):
		if i not in stopWords and i not in unwantedChars:
			dic1[i] = str1.count(i)

	for i in set(tuple(str2)):
		if i not in stopWords and i not in unwantedChars:
			dic2[i] = str2.count(i)
	
	intersection = set(dic1.keys()) & set(dic2.keys())

	
	#intersection=" ".join(intersection)
	#print intersection
	#intersection1 = tokenization(intersection)
	#print intersection1
	#print "--------------------------------------------------------"
	#print intersection
	
	ans = sum([ (dic1[i]*dic2[i]*(float(inverseLogFre[str(i)])**2) )    for i in intersection  if i in inverseLogFre])
	
	mod_A = math.sqrt( sum([ i**2 for i in dic1.values() ]) )
	mod_B = math.sqrt( sum([ i**2 for i in dic2.values() ]) )

	if mod_A*mod_B != 0:
		ans = float(ans)/(mod_A*mod_B) 
	else:
		ans = 0

	return ans


def summarize(text,data):
	sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
	actualSentences = sentenceDetector.tokenize(text)
	
	workingSentences = [sentence.lower() for sentence in actualSentences]
	
	modifiedCosine=[]
	logFre=data[0]
	inverseLogFre=data[1]
	for i in range(len(workingSentences)):
		temp=[]
		for j in range(len(workingSentences)):
			temp.append(idfModifiedCosine(workingSentences[i],workingSentences[j],inverseLogFre))
		modifiedCosine.append(temp)
	return modifiedCosine
	
def process(inputFileName,data):
	content=readData(inputFileName)
	title=content[0]
	text=content[1]
	return [text,summarize(text,data)]
	

def calDenominator(modifiedCosine,i):
	return sum(modifiedCosine[i])

def calculate(modifiedCosine,n,i,p):
	value=0
	for j in range(n):
		if float(modifiedCosine[i][j])!=0:
			value+= (modifiedCosine[i][j]/float( calDenominator(modifiedCosine,j)))*p[j]
	return value

def lex(modifiedCosine):
	
	numOfSentences=len(modifiedCosine[0])
	p=np.full(numOfSentences,1/float(numOfSentences))
	dampingFactor=0.7

	for i in range(numOfSentences):
		value=calculate(modifiedCosine,numOfSentences,i,p)
		p[i]=(dampingFactor/float(numOfSentences))+ ((1 - dampingFactor)* value)
	
	return np.argmax(p)

def reorderSentences(outputSentences,text):
	outputSentences.sort(lambda s1,s2 : text.find(s1) - text.find(s2))
	return outputSentences

def showSummarizedText(matrix,content,result,file):
	sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
	actualSentences = sentenceDetector.tokenize(content)
	workingSentences = [sentence.lower() for sentence in actualSentences]
	sentenceNum=lex(matrix)

	#print workingSentences[sentenceNum]
	result[file]=workingSentences[sentenceNum]
	

def main(Total_Files):
	data=load('logFre.pkl','inverseLogFre.pkl')
	fileNames=[]
	modifiedCosine=[]
	result={}
	count=0
	#for file1 in os.listdir(inputFolder):
	
	
	#fileNames.append(inputFileName)
	filecount=0
	for file in Total_Files:
		print filecount
		content,matrix=process(file,data)
		showSummarizedText(matrix,content,result,file)
		filecount+=1

	output=open('summary.pkl','wb')
	pickle.dump(result,output)
	output.close()



	print "Finished"

	#modifiedCosine.append( matrix)
	
	
	
	"""for i in range(len(modifiedCosine)):
		summary[i]=lex(modifiedCosine[i])
	print summary"""

	print "Finished Processing"

if __name__ == '__main__':
	main(Total_Files)