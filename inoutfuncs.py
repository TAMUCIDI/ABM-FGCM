# FCM
import sys
sys.path.insert(1, 'FCM')
import FCM
import itertools as it
# ABM
import geopandas as gpd
import pandas
import matplotlib.pyplot as plt
import csv
import numpy as np
#Read Bangalore data
def setupcitydata(citygeojson, trafficcsv):
	city=gpd.read_file(citygeojson)
	#Add Neigbors, insert new column: locality_neighbors
	for index, row in city.iterrows():
		# neighbors = city[city.geometry.touches(row['geometry'])].COUNTY.tolist() 
		neighbors = city[city.geometry.touches(row['geometry'])].wardName.tolist() 
		city.at[index, "locality_neighbors"] = ", ".join(neighbors)
	#Insert new column: locality_density
	# density = city['Population']/sum(city['Population'])
	density = city['POP_TOTAL']/sum(city['POP_TOTAL'])
	city['locality_density']=density

	## Set Covid19-cases
	Covid_density = city['POP_ST']/city['POP_TOTAL']
	city['cases_density']=Covid_density

	CD = city[['locality_density', 'cases_density', 'geometry', 'locality_neighbors']]
	# CD = CD.assign(locality_name=city['COUNTY'])
	# CD = CD.assign(locality_id=city['id'].astype(int))
	CD = CD.assign(locality_name=city['wardName'])
	CD = CD.assign(locality_id=city['wardNo'].astype(int))
	# Can't use "ignore_index=True" in sort_values
	CD=CD.sort_values(by=['cases_density'])
	
	# print(CD.head(10))
	CarProb=[]
	with open(trafficcsv, 'r') as file:
		data =list(csv.reader(file, delimiter=','))
		CarProb = np.array(data[0:], dtype=np.float)
	
	print("City Data setup complete")	
	return CD, CarProb

'''
getGreyMap
Args: inFile: A text file formatted as i have the example file greyMap.txt
            node: value
            
            edge edge w1 w2
            
returns: two dictionaries, nodes which is a dictionary of the nodes and their starting values, and
        edges, which uses the tuple set of the edges as a key and has a tuple of the 2 values as the value
        
Desc: Read in the text file of the grey FCM formatted as stated above and return dictionaries for the nodes and edges
'''
def getGreyMap(inFile):
    
     #open text file and declare dictionaries
	f = open(inFile)
	nodes = {}
	edges = {}
	stable = []
	for line in f:
        #split the line into a list
		content = line.split()
		if content: #if the list is not empty
			if content[0] == "Stable:":
				for line in f:
					content = line.split()
					if not content:
						break
					stable.append(content[0])

		if content:
			if content[0] == "Nodes:":
				for line in f: #for all lines in node section add them to node dict. leave on blank line
					content = line.split()
					if not content:
						break
					nodes[content[0].strip(':')] = float(content[1])
                
		if content:#reach edge lists
			inOrder = []	
			if content[0] == "Edges:":
				for line in f: #for each line in edge section add tuples of node to node edges and tuple weights
					content = line.split()
					inOrder.append(content[0]+'->'+content[1])
					edges[(content[0],content[1])] = (float(content[2]), float(content[3]))
                
					if not content:
						break
	
	fcm = createInitialFCM(nodes, edges)  
	return fcm,len(edges),edges,stable,inOrder

'''
Create the initial FCM, all binary values are 0. Will create a separate function to modify it from the binary values later
'''
def createInitialFCM(nodeDict, edgeDict):
	fcm = FCM.FCM()
    
	for key in nodeDict:
		fcm.add_concept(key)
		fcm.set_value(key, nodeDict[key])
        
	for key in edgeDict:
## Edit: Use first value in the range.
		fcm.add_edge(key[0], key[1], edgeDict[key[0],key[1]][0])
	return fcm

'''
tupleToString
takes a tuple of strings and returns is as a single string for writing
'''
def tupleToString(element):
	returnString = ''
	first = True
	for i in range(0,len(element)):
		if first:
			returnString += element[i]
			first = False
		else:
			returnString += '&'+element[i]
	return returnString

def outFCM(outFile, sumDict, inOrderEdges):
	header = 'index'
	#create header for edges using itertools
	head2 = list(it.combinations(inOrderEdges,2))#2nd degree
	head3 = list(it.combinations(inOrderEdges,3))#3rd degree
	for element in inOrderEdges:
		header = header + ',,,' + element #only one not a set of tuples
         
	for element in head2:
		header = header + ',,' + tupleToString(element)
         
	for element in head3:
		header = header + ',' + tupleToString(element)

	header = header + '\n'

	f = open(outFile,'w')
	f.write(header)

	for key in sumDict:
		writeLine = '~'
		writeLine += key
		for element in sumDict[key]:
			writeLine = writeLine + ',' + str(element)
		writeLine += '\n'
		f.write(writeLine)

	f.close()