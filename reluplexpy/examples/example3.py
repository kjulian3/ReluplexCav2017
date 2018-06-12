import numpy as np
from reluplexpy import Reluplex

tf_file_name = "./networks/graph_test_medium.pb"
net2 = Reluplex.read_tf(tf_file_name)
print("With Reluplex:")
print(net2.evaluateWithReluplex(np.ones(net2.inputVars.shape))[0])
print("With Tensorflow:")
print(net2.evaluateWithoutReluplex(np.ones(net2.inputVars.shape)))
