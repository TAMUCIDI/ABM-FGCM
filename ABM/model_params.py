# ptrans = Transmission probability.
# population = Total population within all containers.
# progression_period = Average number of days until a patient seeks treatment.
# progression_sd = Standard deviation of progression_period.
# interactions = Average number of interactions per person per day (decreases with social distancing).
# reinfection_rate = Probability of becoming susceptible again after recovery.
# I0 = Initial probability of being infected.
# death_rate = Probability of dying after being infected after progression_period and before recovery_days.
# recovery_days = Average number of days until recovery.
# recovery_sd = Standard deviation of recovery_days.
# severe = Probability of developing severe, symptomatic disease.
# steps = number of days in siimulation.

parameters = {'I0':0.01, 'ptrans':0.25, 'progression_period':3, 
              'progression_sd':2, 'population':10, 'interactions':12,
              'reinfection_rate':0.00, 'death_rate':0.0193, 
              'recovery_days':21, 'recovery_sd':7, 'severe':0.18, 'steps':90,
              'Days':360, 'Population':10000, 'Iterations':30,
              'TestingBudget':50, #tests per day
              'FalseNegative':0.0, #false nagative prob for each test 
            }

#Model Parameters                                                                                                                                             
ModelParams = {\
    #Probability with which two persons who meet will transfer Covid                                                                                         
    "CovidInfectionRate":0.1, \

    #Covid [1/Average time to symptoms, 1/Average time to recovery]                                                                                           
    "CovidRateVector": [1, 1/8], \

    #Flu [S2I, 1/Average time with Flu symptoms]                                                                                                              
    "FluRateVector": [0.02, 1/8], \

    #Each person meets these many random people locally                                                                                                       
    "NeighborhoodContact": 1, \

    #Each person meets these many fixed people locally                                                                                                        
    "NeighborhoodContactFixed": 5, \

    #Each person meets these many random people at a hotspot                                                                                                  
    "HotspotContact": 2, \
        
    #Each person meets these many fixed people at a hotspot                                                                                                   
    "HotspotContactFixed": 10,}