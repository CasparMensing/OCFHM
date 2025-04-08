# Object-Centric Causal Net Miner

This repository contains the code for the object-centric causal net miner.
The miner can discover and visualize object-centric causal nets from object-centric event logs in the [OCEL format](https://www.ocel-standard.org/).
Here you can see an example visualization for the [logisitcs event log](https://www.ocel-standard.org/event-logs/simulations/logistics/).

![Example image for the logistics event logs.](examples/Container_Logistics_OCCN_legend.png)

## Getting Started
After cloning the repository, you can install the dependencies specified in the `requirements.txt`. 
Once the dependencies are installed, you can start the miner by running the `object_centric_causal_net_miner.py` file.
This will start a command line interaction in which you are asked for the object-centric event log file path, which version of an [OCEL](https://www.ocel-standard.org/) you use, and which parameter setting you want to select.
Once the causal net is computed it is visualized on a website in your browser that you can interact with for filtering and repositioning of the activities in the net.
