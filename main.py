#Dependencies
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import pickle
import random as random
from math import exp
import os
import pathos.multiprocessing as mp
# FCM modules
from inoutfuncs import getGreyMap, outFCM
from greyMap import runFCM
from Hebbian import hebbian_learning
#ABM modules 
import sys
sys.path.insert(1, 'ABM')
import model_params
from evolution import simulate
from inoutfuncs import setupcitydata
from tests import RandomSymptomaticTesting
from interventions import InterventionQuarantine

if __name__ == '__main__':
    #Read city data using function setupcitydata available in inoutfuncs
    CD, CarProb=setupcitydata('InputData/city.geojson', 'InputData/car-prob.csv')
    # CD, CarProb=setupcitydata('InputData/TX_Counties.geojson', 'InputData/TX_prob.csv')

    ## Get FGCM
    fcm, k, edges, stableList, inOrderEdges = getGreyMap('InputData/testCase.txt') #fcm is the inital fcm(binary 0) and k is the number of edges
    '''
    ## Run FGCM with multiprocessors
    numCores = mp.cpu_count() #returns the number of cpu's and stores for size of pool
    # print(fcm, k, edges, stableList, inOrderEdges)
    print("number of Cores", numCores)
    pool = mp.Pool(numCores) #create maximum number of processes
    start, end = 0, 1
    '''
    # results = [pool.apply_async(runFCM, (fcm,num,k,edges,stableList))for num in range(start,end)]
    # for result in results:
    #     for element in stableList:
    #         print(result.get()[element])
    # print("CD:", CD.shape, "Prob:", CarProb.shape)
    
    seed='uniform' #Uniformly distribute initial cases, see details below
    TestingBudget = model_params.parameters['TestingBudget']
    FalseNegative = model_params.parameters['FalseNegative']
    LocationRepProb=np.ones(CD.shape[0]) #reporting probability per locality

    ##testing policy set to RandomSymptomaticTesting given in tests.py
    testingPolicy = partial(RandomSymptomaticTesting, TestingBudget, FalseNegative, LocationRepProb)

    ##intervention policy set to InterventionQuarantine in interventions.py
    interventionPolicy = InterventionQuarantine

    #Directory for storing output data
    script_dir = os.path.dirname(__file__)
    OutputDirectory = "OutputData/"
    SimulationDirectory = "SimulationResults/"

    #Create simulation directory
    SimulationDirectory = os.path.join(script_dir, SimulationDirectory)
    path = os.path.join(SimulationDirectory, OutputDirectory) 
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    ##Initial infected (seed)
    ## Seeding type 1: Uniform seeding
    ## covid and flu infected distributed uniformly
    InitFracLocalitiesCovid=0.1 # approx. fraction of localities with a single covid infection seed                                                               
    InitFracLocalitiesFlu=0.1 # approx. fraction of localities with a single flu infection seed                                                                   
    CovidMaxPerLocality= 5
    FluMaxPerLocality= 20

    ## Seeding type 2: clustered seeding
    ## all covid infections placed in a single locality (locality_name="Cottonpete", locality_id=120)
    ## flu infection seeds randomly placed across localities
    SeedLocalityID = 120
    InitNumSeedsCovid = 50 

    if seed == 'uniform':
        initcovidcts = np.random.binomial(CovidMaxPerLocality, InitFracLocalitiesCovid, CD.shape[0]).tolist()
        initflucts = np.random.binomial(FluMaxPerLocality, InitFracLocalitiesFlu, CD.shape[0]).tolist()

    elif seed == 'clustered':
        initcovidcts = np.zeros(CD.shape[0]).astype(int).tolist()
        initcovidcts[SeedLocalityID-1] = InitNumSeedsCovid
        initflucts = np.random.binomial(1, InitFracLocalitiesFlu, CD.shape[0]).tolist()

    ###Call to the simulate function in evolution.py
    OutputFileNamePrefix = SimulationDirectory+OutputDirectory+"FcmRandomSymptomaticTesting_UniformSeed_InterventionQuarantine_TestingBudget50_FalseNegative0" 
    for i in range(model_params.parameters['Iterations']):
        CovidCases, TestingHistory,  Symptomatic, Localities = simulate(fcm, stableList, \
                                                                        model_params.parameters['Days'], model_params.parameters['Population'], \
                                                                        model_params.ModelParams, CD, CarProb, interventionPolicy, testingPolicy,\
                                                                        InitCovidCounts=initcovidcts, InitFluCounts=initflucts)    
        print("Iteration number:"+str(i))
        FileName = OutputFileNamePrefix + "_Iter_" + str(i) + ".pickle"
        # plotresults(CovidCases, TestingHistory)
        with open(FileName, "wb") as f:
            pickle.dump((CovidCases, TestingHistory, Symptomatic, Localities), f)
            print("Results saved in " + FileName)