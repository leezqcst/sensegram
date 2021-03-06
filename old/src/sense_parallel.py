#!/usr/bin/env python
#
# Author: Jonas Molina Ramirez, Kai Steinert
# Version: 0.1
# Date: 12/11/2015
#
import time
from datetime import datetime
from gensim import corpora, models, similarities
import logging as logger	
import gensim as gs
import multiprocessing as mp
import os

path = '../resrc/GoogleNews-vectors-negative300.bin'

logger.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',filename='logs/sense.log',filemode='w', level=logger.INFO)
# This function initiates the parallel computation, tracks the processes 
# and provides some numbers via logging
def run_parallel(knn,model,numberOfFiles,folder,end_idx,start_idx=0,with_range=False):
	
	# create a list of locks. each lock is reserved for a file
	# and identified by the dictionary's key 
	locks = dict([(id,mp.Lock()) for id in range(0,numberOfFiles)])

	# auxiliary counter for assigning locks to processes
	counter = 0

	# counter the number of instantiated processes
	processCounter = 0
	start = time.time()
	logger.info("Start computation of KNN: \n" + str(datetime.fromtimestamp(start)))
	processes = []
	# start processes that compute knn of some ranges
	if(with_range):
		# number of words per process
		sliceSize = len(model.index2word[start_idx:end_idx])/numberOfFiles
		
		myRange = range(start_idx,end_idx,sliceSize)
		for x in range(0,(len(myRange) - 1)):
			if(x == len(myRange) - 1):
				if((end_idx - myRange[x])!= 0):
					myRange.append(myRange[x]+ sliceSize)
			logger.debug("Start process with range (" + str(myRange[x]) + "," +str(myRange[x+1]) + ")")
			p = mp.Process(target=parallel_with_range,args=(model,(myRange[x],myRange[x+1]),counter,knn,locks.get(counter),folder))
			p.start()
			processes.append(p)
			counter +=1
			processCounter += 1
			if(counter%numberOfFiles == 0):
				counter = 0 
	# start processes that compute knn for exactly one word each
	else:
		for word in model.index2word[start_idx:end_idx]:
			p = mp.Process(target=parallel,args=(model,word,counter,knn,locks.get(counter),folder))
			p.start()
			processes.append(p)
			counter += 1
			processCounter += 1
			if(counter%numberOfFiles==0):
				counter = 0
	# wait for processes to finish
	logger.info("All processes initialized!")
	for proc in processes:
		proc.join()
	end = time.time()
	overallSize = 0
	for dirpath,dirnames,filenames in os.walk(folder):
		for f in filenames:
			#print f + '\n'
			fp = os.path.join(dirpath,f)
			overallSize += os.path.getsize(fp)				
	if(with_range):
		logger.info("Used worker parallel_with_range()")
	else:
		logger.info("Used worker parallel_with_range()")
	logger.info("End computation of KNN: \n" + str(datetime.fromtimestamp(end)))
	logger.info("Constructed " + str(processCounter) + " processes.")
	logInfo(start,end,'Wrote files in ')
	logger.info("Overall file size: " + str(overallSize/1024) + "kb")

# Logs the difference between end and start 
def logInfo(start, end,txt):
	logger.info(txt + str(end-start) + ' seconds')

# loads the model.
# "path" must identify the exact file 
# from which the model should be constructed.
def load_model(path):
	start = time.time()
	model = models.Word2Vec.load_word2vec_format(path, binary=True,encoding='utf8')
	end = time.time()
	logInfo(start,end,'Loaded model in ')
	return model

# Computes the KNN and prints the results to a csv-file.
# This function is inteded to be used for parallel computation.
# Parameters:
#	model: a gensim.word2vec model
# 	word: the word for which the neighbours are computed
# 	id: a provided integer ID used to name the csv-file
# 	nn: the number of nearest neighbours
# 	lock: a lock that is used to guard the critical section (writing to the file)
#	folder: the folder that contains the file
def parallel(model,word,id,nn,lock,folder):
	pid = str(os.getpid())
	logger.info("Start Pid: " + pid)
	neighbours = dict(model.most_similar(word,topn=nn))
	text = [('\t' + w.encode('utf-8') + '\t' + str(s) + '\n') for (w,s) in neighbours.iteritems()]
	lock.acquire()
	with open(folder+"/test_" + str(id) + ".csv", "a") as myfile:
		for line in text:
			myfile.write(word.encode('utf-8') + line)
	lock.release()
	logger.info("End Pid: " + pid)


# Parameters:
#	model: a gensim.word2vec model
#	range: a integer tuple holding start index and end index of the computation
#	
def parallel_with_range(model,range,id,nn,lock,folder):
	pid = str(os.getpid())
	logger.info("Start Pid: " + pid)
	for word in model.index2word[range[0]:range[1]]:
		neighbours = dict(model.most_similar(word,topn=nn))
		text = [('\t' + w.encode('utf-8') + '\t' + str(s) + '\n') for (w,s) in neighbours.iteritems()]
	lock.acquire()
	with open(folder+"/test_" + str(id) + ".csv", "a") as myfile:
		for line in text:
			myfile.write(word.encode('utf-8') + line)
	# allow other processes to write to the file
	lock.release()
	#end of function
	logger.info("End Pid: " + pid)

if __name__ == "__main__":
	try:
		model
	except NameError:
		model = load_model(path)
	
	#run_parallel(knn=200,model=model,numberOfFiles=40,folder='tmp1',end_idx=1000,with_range=True)
	run_parallel(knn=200,model=model,numberOfFiles=40,folder='tmp',end_idx=10,with_range=False)
	
