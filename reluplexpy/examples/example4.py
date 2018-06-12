import numpy as np
from reluplexpy import Reluplex

tf_file_name = "./networks/graph_test_medium.pb"
net2 = Reluplex.read_tf(tf_file_name)
net2.setLowerBound(net2.outputVars.item(0),-3.0)
net2.solve("")
