import numpy as np
from reluplexpy import Reluplex
nnet_file_name = "./networks/HorizontalCAS_tiny_2.nnet"

net1 = Reluplex.read_nnet(nnet_file_name)
net1.setLowerBound(net1.outputVars[0][0], -3.2)
vals1 = net1.solve("")

