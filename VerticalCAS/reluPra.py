# Import statements
# Make sure ReluplexCav2017 (folder containing reluplexpy) is in python path
import numpy as np
import sys
from reluplexpy import Reluplex
from reluplexpy import ReluplexUtils

# Not every advisory is possible from any previous advisory.
# This matrix shows how the advisories are allowed to change.
# For example, if the previous advisory is advisory 1, then 
# advisories 1, 2, 3, 4, 5, and 6 are possible.
#
# There are separate networks for each previous advisory, so
# Each networks may have different numbers of outputs, and their
# Outputs will correspond to the different possible advisories
ra_transitions = [
[1, 2, 3, 4, 5,  6              ],
[1, 2, 3, 4,       7, 8         ],
[1, 2, 3, 4,       7, 8         ],
[1, 2, 3, 4,       7, 8, 9,10   ],
[1, 2, 3, 4, 5,       8, 9      ],
[1, 2, 3, 4,    6, 7,      10   ],
[1, 2, 3, 4,       7, 8, 9      ],
[1, 2, 3, 4,       7, 8,   10   ],
[1, 2, 3, 4,          8, 9      ],
[1, 2, 3, 4,       7,      10   ],
[1, 2, 3, 4,       7, 8,      11]]


# Define the w and vlo parameters for each advisory
adv = [
[0,0],
[-1,0],
[1,0],
[0,0],
[-1,-1500 / 60.0],
[1 , 1500 / 60.0],
[-1,-1500 / 60.0],
[1 , 1500 / 60.0],
[-1,-2500 / 60.0],
[1 , 2500 / 60.0],
[0,0],
] # (ND, ft/s)
adv_names = ["COC", "DNC", "DND", "MAINTAIN","DES1500","CL1500","SDES1500","SCL1500","SDES2500","SCL2500","MTLO"]
hp = 100 #ft

# Network normalization constants
R_h   = 16000.0  # ft
R_v  = 200.0    # ft/s
R_tau = 34.0     # s
mu_tau= 23.84210526  # s

# Read pra argument, should be in {1, 2, 3,...,11}
if len(sys.argv)==2:
    pra = int(sys.argv[1])
    nnet_file_name = "./networks/VerticalCAS_r15_pra%02d_v2_45HU_1200.nnet" % pra
    pra_name = adv_names[pra-1]

    
    # Get the indices of the valid advisories]
    ra = [i-1 for i in ra_transitions[pra-1]]
    ra_names = [adv_names[i-1] for i in ra_transitions[pra-1]]
    ra_params = [adv[i].copy() for i in ra]

    for advIndex in range(len(ra_params)):
        # Reload a clean network each time
        net1 = Reluplex.read_nnet(nnet_file_name)
        
        # Select the advisory we want to check
        w, vlo  = ra_params[advIndex]
        ra_name = ra_names[advIndex]
        
        # File names
        fn = "reluplexResults/pra%s_ra%s.txt"%(pra_name,ra_name)
        reluLog = "reluplexLogs/pra%s_ra%s.log"%(pra_name,ra_name)
        
        file = open(fn,"w") 
        file.write("Pra: %s, Advisory: %s (w: %d, vlo: %.2f ft/s)\n" % (pra_name,ra_name,w,vlo))
        file.close()
        
        print("\nPra: %s, Advisory: %s (w: %d, vlo: %.2f ft/s)" % (pra_name,ra_name,w,vlo))
        if abs(w)<0.5:
            print("Skipping Advisory")
            file = open(fn,"a") 
            file.write("Skipping advisory because w and vlo not defined\n")
            file.close()
            continue

        # Input constraints
        inputVars = net1.inputVars[0]
        # h:   inputVars[0]
        # v:   inputVars[1]
        # v_i: inputVars[2]
        # tau: inputVars[3]
        

        # Bound vertical rate of ownship
        if w>0.5:
            net1.setLowerBound(inputVars[1], vlo / R_v)
        else:
            net1.setUpperBound(inputVars[1], vlo / R_v)

        # Level flight for intruder
        net1.setLowerBound(inputVars[2], 0.0)
        net1.setUpperBound(inputVars[2], 0.0)

        # Inequality relating relative altitude and tau
        if abs(vlo)<1e-5:
            # if vlo is 0, then we just have a bound on h
            if w<-0.5:
                net1.setUpperBound(inputVars[0],  hp / R_h)
            else:
                net1.setLowerBound(inputVars[0], -hp / R_h)
        else:
            # Hyperplane boundary
            ReluplexUtils.addInequality(net1, [inputVars[0],inputVars[3]], [-w*R_h,vlo*w*R_tau], hp - vlo*w*mu_tau)

            
        # Output constraints
        outputVars = net1.outputVars[0]
        
        # Property to be UNSAT: advisory is maximum cost
        # Inequalities take the form vars'weights <= scalar
        # The function inputs are the network, the variable vector, the weight vector, and the scalar
        for i in range(len(outputVars)):
            if i != advIndex:
                ReluplexUtils.addInequality(net1, [outputVars[advIndex], outputVars[i]], [-1, 1],0)

        # Solve
        result, vals = net1.solve(reluLog)
        
        file = open(fn,"a")
        file.write(result + "\n")
        if result == "SAT":
            # Unnormalize input values
            file.write("\nInputs:\n")
            file.write("h   = {}\n".format(vals[inputVars[0]]*R_h))
            file.write("dh0 = {}\n".format(vals[inputVars[1]]*R_v))
            file.write("dh1 = {}\n".format(vals[inputVars[2]]*R_v))
            file.write("tau = {}\n".format(vals[inputVars[3]]*R_tau + mu_tau))

            file.write("\nOutputs:\n")
            for i in range(len(outputVars)):
                file.write("{} = {}\n".format(ra_names[i], vals[outputVars[i]]))
        file.close()

        # If we gave the ctrl+c early termination signal, break out of these loops!
        if result == "EARLY TERMINATION":
            break
else:
    print("Please give pRA index!")