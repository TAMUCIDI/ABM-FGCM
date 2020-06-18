import operator
from copy import deepcopy
import itertools as it
from functools import reduce
import FCM

debug=2

'''
Main
pass the file to get grey map to get the set up for the fcm
create the initial fcm
figure out number of processors and make a pool with that many processors
'''
def runFCM(fcm, num, k, edgeDict,stableList):
	config, minMaxList = fcmConfiguration(num, k)
	testFCM, updatedEdgeDict = newFCM(fcm, edgeDict, config)
	if debug==1:
		print ('first time update: ', updatedEdgeDict)
	sim = createSim(testFCM, stableList)
	res = runSims(sim)

	products = getResults(res, minMaxList, stableList)
	if debug==1:
		print ('Products are: ', products)
		print ('MinMax list is: ', minMaxList) 
	return products
	# return (res, updatedEdgeDict)

'''
fcmConfiguration
arguments: num: an integer for which configuration of the FCM to run
           k: an integer that represents how many edges there are. used for padding
return: the binary configuration for the FCM
Desc: Takes in the number for which FCM is being run in a fuzzy grey map, and returns the binary configuration 
that will determine which values are on each edge.
'''
def fcmConfiguration(num, k): 
    minMaxList = []
    string = '{0:0'+str(k)+'b}' #format string for binary conversion
    config = string.format(num) #get a binary string of the value

    if debug==1:
        print ('Length of config is: ', (config) ) 
    for element in config:
        if int(element) == 0:
            minMaxList.append(-1)
        else:
            minMaxList.append(1)
    if debug==1:
        print ('in configuration length of minMaxLIst is: ', (minMaxList) )
    return config, minMaxList

'''
create a new FCM with the same node values but adjust edge weights according to the next one needed for the 2^k test
'''
def newFCM(fcm, edgeDict, binary):
    newFcm = deepcopy(fcm)
    count = 0
    newEdgeDict = {}
    for key in edgeDict:
        newFcm.add_edge(key[0], key[1], edgeDict[key[0],key[1]][int(binary[count])])
		#same code to create an edge will change the wieght if it already exists		
        newEdgeDict[(key[0],key[1])] = edgeDict[key[0],key[1]][int(binary[count])]        
        count += 1        
    return newFcm, newEdgeDict

def createSim(fcm, stableList):
	sim = FCM.simulation(fcm)
	# set how many steps for simulation
	sim.steps(100)
	for element in stableList:
		# threshold = 0.001
		sim.stabilize(element, .001)
	return sim
        
'''
Run the simulation and return the final concept values
'''
def runSims(sim):
	# return the last element of the list
	return sim.run()[-1]
    
'''
getResults
Gets all the min and max information and the simulation results. It creates the interactions and multiplies the 
results in a dictionary of stable elements and multiplies each by the interaction effect
'''
def getResults(simResults, minMaxList, stableList):
	result2 = list(it.combinations(minMaxList, 2))#get interaction for the second degree
	result3 = list(it.combinations(minMaxList, 3))#get list of all interaction for 3rd degree effects
	interactions = []
	for element in minMaxList:
		interactions.append(element)
	# print('result2',result2,'result3',result3,'interactions',interactions)
    	#add the second degree interactions to the list
	for element in result2:
		interactions.append(prod(element))
    	#add the 3rd degree interacitons to the list
	for element in result3:
		interactions.append(prod(element))
	if debug==1:
		print ('The interaction list is: ', interactions)

	returnDict = {}    
	for element in stableList:
		returnDict[element] = []
		# for networkx version = 2.3
		returnDict[element] = list(map(lambda x: x * simResults[element], interactions)) # x = interactions
		if debug==1:
			print ('Element is: ', element)
			print ('Element value is: ', simResults[element])
	if debug==1:
		print ('After all multplication Value is:', returnDict)

	return returnDict

'''
Will get the product of all elements in the iterable. Used for the diffferent combinations for interactions
'''
def prod(iterable):
	return reduce(operator.mul, iterable, 1)

