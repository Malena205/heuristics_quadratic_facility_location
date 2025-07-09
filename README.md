# Heuristics for a capacitated facility location problem with a quadratic objective function
This project contains the code used in both M. Schmidt's completed master thesis and the article **The Balanced Facility Location Problem: Complexity and Heuristics** by M. Schmidt and B. Singh published in the [INFORMS Journal on Computing](https://pubsonline.informs.org/doi/full/10.1287/ijoc.2024.0693). We provide the implementations of all the algorithms and heuristics discussed in the article as well as the the instances we use to test our heuristics on.


## Requirements for running the code
Before cloning the code, make sure you have [Git Large File Storage (Git LFS)](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) installed. Please see instructions for downloading and installing Git LFS on the linked website. Note that the data files will not function properly, due to their size, if you just download the zipped file. After installing Git LFS, 
(i) clone the repository as usual (with `git clone https://github.com/Malena205/heuristics_quadratic_facility_location.git`) to get the actual data files. Then, (ii) navigate into the folder as usual (with `cd`) and (iii) pull the large data files with Git LFS (`git lfs pull` and then `git lfs install`). Finally, (iv) copy the `Data` folder into the `heuristics_and_mips` folder. 
 
Further, before running the code, make sure you have the below installed and linked with their respective paths (see instructions on installation on their respective pages):
- python3
- numpy
- pandas
- geopy
- pyomo
- gurobi

  
## Repository content
Please refer to the preprint for the terminology. The repository is structured as follows:
- ```data```: This folder contains the data for the four instances. For each instance, there is a file containing the travel probabilities $P_{ij}$ (e.g., ```instance_1_travel_dict.json.pbz2```) and a file containing the rest of the input data in a dataframe (e.g., ```instance_1_users_and_facs.csv```). For each instance, we also provide a corresponding instance where the capacity has been scaled to $C_j = \sum_{i \in I} U_i P_{ij}$ (```instance_1_suff_users_and_facs.csv```). 
To load the data, we provide the function ```load_an_instance```. See an example of loading Instance 1 without sufficient capacity just below. ```users``` is the set $I$ and ```facs``` is the set $J$. Note that in our use of the instances we scale the input capacities by a factor. If ```cap_factor``` is provided as an input to the function, then set it: to 1.0 for any of the sufficient capacity instances, to 1.5 for Instance 1 or Instance 2, and to 0.8 for Instance 3 or Instance 4.
```python
users_and_facs_df, travel_dict, users, facs = load_an_instance(1, False)
```
- ```heuristics_and_mips```: This folder contains the main part of the code. We briefly describe the purpose of each of the files:
	- ```BFLP_heuristics.py```: This file contains the code for all the BFLP heuristics. 
	- ```BFLP_MIP.py```: This file contains the code for running the BFLP MIP.
	- ```BUAP_heuristics.py```: This file contains all the BUAP heuristics and also implementations of those that are just needed for use within the BFLP heuristics; e.g., the optimization of `relaxation rounding` when used in the first version of `close greedy`.
	- ```BUAP_MIP.py```: This file contains the code for running the BUAP MIP and also for editing the model, as needed for `relaxation rouding` with the first version of `close greedy`.
	- ```results_heuristics.py```: This file contains functions for running all the heuristics across multiple budget factors and input parameters. For each BFLP heuristic, we provide a function for running the heuristics with multiple inputs (see the function name starting with `get_`). Results are written in JSON files; we also provide a function for converting these results into more easily readable Excel tables (see the function name starting with `write_`). All results created are saved in the `own_results` folder, which is created if it does not exist yet. For the BUAP, there is a function that runs all the heuristics on a single instance and the corresponding function which writes the results into a table.
	- ```utils.py```: This file contains a few subroutines that are useful for reading and writing data, and some subroutines that are used in multiple heuristics.
 	- ```main.py```: This file contains a concrete example of how to run the functions in the repository. The line `results = ` may be changed to run the relevant heuristic (with the appropriate data input existing).
  	- ```run_instance_i.py```: This file contains the code for instance `i = 1, ..., 4` which solve model naively and greedy_heuristic to obtain optimality gap and overall access in a table.

## Example
We provide a short concrete example of how to run this code in the ```main.py``` file. To run the file, make sure you have navigated to the appropriate repository folder in your terminal. Then, run the file from the terminal using ```python3 ./heuristics_and_mips/main.py``` or directly from a python interface (such as, Spyder). In this example, by default, we run the `open greedy` algorithm on Instance 1. The algorithm tests out how different values for the parameters $n_c$ and $d$ perform across different budgets. The results for the BFLP MIP for this instance are saved in the file ```instance_1_BFLP_MIP.json``` in the `own_results` folder. 

Similarly, to run the `close greedy` algorithm, or the BFLP and BUAP models, just copy-paste the corresponding get_ command as we explained above into the main file and run it. 
