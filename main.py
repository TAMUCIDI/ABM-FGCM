import os
import argparse
import numpy as np
import pathos.multiprocessing as mp
# FCM modules
from inoutfuncs import getGreyMap, outFCM
from greyMap import runFCM
# ABM modules
from inoutfuncs import setupcitydata
import sys
sys.path.insert(1, 'ABM')
import agent
import model_params
from mesa import Model
from mesa_geo.geoagent import AgentCreator
from model import InfectedModel


def parse_arguments():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--config_file', default=None)
    # parser.add_argument('--output_file', default='results.txt')
    parser.add_argument('--start', default=0, type=int) #start of range
    parser.add_argument('--end', default=3, type=int) #range 
    parser.add_argument('--days', default=10, type=int) 
    parser.add_argument('--population', default=10000, type=int)
    parser.add_argument('--iterations', default=3, type=int)
    args = parser.parse_args()
    return args.start, args.end, \
           args.days, args.population, args.iterations

if __name__ == '__main__':
    ## Parameters
    start, end, days, population, iterations = parse_arguments()
    seed='uniform' #Uniformly distribute initial cases, see details below
    TestingBudget=50 #tests per day
    FalseNegative=0.0 #false nagative prob for each test 
    # LocationRepProb=np.ones(CD.shape[0]) #reporting probability per locality
    print("start:", start, "end:", end) 
    print("days:", days, "population:", population, "iterations", iterations)
    
    # population = model_params.parameters['population']

    # for node in range(population):
    #     new_agent = agent.PersonAgent(node, Model)
    #     print("iter", node, new_agent)
    
    ## Input file 
    script_dir = os.path.dirname(__file__)
    rel_path = "InputData/caseStudy1-SubsetStabilizes.txt"
    inFile = os.path.join(script_dir, rel_path)
    CD, CarProb = setupcitydata('InputData/city.geojson', 'InputData/car-prob.csv')    

    ## Get FGCM
    fcm, k, edges, stableList, inOrderEdges = getGreyMap(inFile) #fcm is the inital fcm(binary 0) and k is the number of edges
    ## Run FGCM with multiprocessors
    numCores = mp.cpu_count() #returns the number of cpu's and stores for size of pool
    print("number of Cores", numCores)
    pool = mp.Pool(numCores) #create maximum number of processes
    results = [pool.apply_async(runFCM, (fcm,num,k,edges,stableList))for num in range(start,end)]
    ## Output FGCM
    sumDict = {}
    for element in stableList :
        sumDict[element] = [0]*len(list(results[0].get()[element]))

    count = 0
    for result in results :
        count +=1
        for element in stableList :
            for i in range(0, len(sumDict[element])):
                sumDict[element][i] = sumDict[element][i] + list(result.get()[element])[i]
    
    #Directory for storing output data
    OutputDirectory = "OutputData/"
    SimulationDirectory = "SimulationResults/"

    #Create simulation directory
    SimulationDirectory = os.path.join(script_dir, SimulationDirectory)
    path = os.path.join(SimulationDirectory, OutputDirectory) 
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    OutputFileNamePrefix = SimulationDirectory+OutputDirectory
    FileName = OutputFileNamePrefix + "test.txt"
    outFCM(FileName, sumDict, inOrderEdges)

    # Instantiate model
    test_model = InfectedModel(100, 0.2, 50)

    for i in range(10):
        print('Running step {}'.format(str(i)))
        test_model.step()