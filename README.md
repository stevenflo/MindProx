# MindProx
A collection of Code for Generating Machine Independent Proxies

# The MindProx proxy tool was developed by the University of Texas at Austin in conjunction with Intel. MindProx uses the tool PIN to capture the required metrics and then generates the proxies into portable cpp files. This low run time process allows for rapid development of proxies regardless of how complex the software stack of the original workload may be.

# Generating a proxy requires three steps:
1. Profiling the original workload using PIN
2. Converting the profiling outputs into json files
3. Using the json files as inputs to the proxy generator to create a proxy

# Each folder in this directory handles one of the these steps and has its own readme detailing how to accomplish each step. If you have any questions please email steven.flolid@gmail.com

