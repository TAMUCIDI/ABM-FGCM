import pathos
import sys
sys.path.insert(1, 'FCM')
import FCM

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