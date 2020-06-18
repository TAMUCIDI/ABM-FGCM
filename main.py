import os
import argparse
import pathos.multiprocessing as mp
# FCM modules
from inoutfuncs import getGreyMap
from greyMap import runFCM

def parse_arguments():
    parser = argparse.ArgumentParser()
    # inFile = "/scratch/user/matthong1038/Parallel-FCM/Analyzing_and_simplifying_model_uncertainty_in_fuzzy_cognitive_maps/Experimental_set-up/caseTest1-AllStabilizes.txt"
    # #sys.argv[1]#[0] is program name
    # outFile = "test1.txt"#sys.argv[4]#output filename
    parser.add_argument('--config_file', default=None)
    parser.add_argument('--output_file', default='results.txt')
    parser.add_argument('--start', default=0, type=int) #start of range
    parser.add_argument('--end', default=3, type=int) #range 

    args = parser.parse_args()
    return args.start, args.end

if __name__ == '__main__':
    start, end = parse_arguments()
    print(start, end)
    # /scratch/user/matthong1038/ABM-FGCM/inputData/caseStudy1-AllStabilizes.txt
    script_dir = os.path.dirname(__file__)
    rel_path = "inputData/caseStudy1-SubsetStabilizes.txt"
    inFile = os.path.join(script_dir, rel_path)
    fcm, k, edges, stableList, inOrderEdges = getGreyMap(inFile) #fcm is the inital fcm(binary 0) and k is the number of edges
    
    numCores = mp.cpu_count() #returns the number of cpu's and stores for size of pool
    print("number of Cores", numCores)

    pool = mp.Pool(numCores)#create maximum number of processes
    results = [pool.apply_async(runFCM, (fcm,num,k,edges,stableList))for num in range(start,end)]
    
    sumDict = {}
    for element in stableList :
        sumDict[element] = [0]*len(list(results[0].get()[element]))

    count = 0
    for result in results :
        count +=1
        for element in stableList :
            for i in range(0, len(sumDict[element])):
                sumDict[element][i] = sumDict[element][i] + list(result.get()[element])[i]

    print("=================")
    print('sumDict', sumDict)
    print ('Number of results processed was: ', count)