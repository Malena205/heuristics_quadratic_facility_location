from utils import *
from model import *
from greedy_heuristic import *
from results import *
import os
import numpy as np
import pandas as pd

if __name__ == '__main__':
    users_and_facs_df, travel_dict, users, facs = load_an_instance(4)
    save_greedy_results(
        users_and_facs_df,
        travel_dict,
        output_filename='greedy_results_4.xlsx',
        cutoff=0.0,                           # **turn off** the 0.2 cutoff
        strict_assign_to_one=False,          # or True if that’s how you ran your experiments
        cap_factor=1.5,
        max_access=False,
        main_threads=1,
        main_tolerance=5e-3,
        main_time_limit=20_000,
        post_threads=1,
        post_tolerance=0.0
    )