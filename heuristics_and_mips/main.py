from utils import *
from results_heuristics import * 
from BFLP_MIP import *

users_and_facs_df, travel_dict, users, facs = load_an_instance(1)

# the code below runs the open greedy heuristic with the given parameters
results = get_results_open_greedy(users_and_facs_df, travel_dict, users, facs, 
                             budget_factors = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], 
                             cap_factor=1.5, threads=1, tolerance=0.0,
                             cutoff_localsearch = 0.2, num_consider_in_relaxation = 50, 
                             num_consider_per_iterations = [5,50], time_limit_relaxation=1000,
                             assignment_methods =["greedy_assign"],local_search_methods = ["local_random_reassign"], 
                             time_limit_while_localsearch = 1, num_fix_assignment_iterations = [len(facs)],
                             depths_greedy_reassign = [1,2],
                             final_assignment_methods = ["relaxation_rounding"],output_filename = "open_greedy_instance_1.json")

# similarly the code below (after uncommenting) runs the BFLP model with the given parameters
# is_feasible, results = run_BFLP_model(users_and_facs_df, travel_dict, users, facs, budget_factor = 1.0,
#                         cap_factor = 1.5, cutoff = 0.0, strict_assign_to_one = True,
#                         cap_dict = None, continous = False, num_consider = -1, 
#                         threads=1, tolerance=0.0,time_limit = 20000, output_filename = "basic_model.json")

# and, again, similarly the code below (afet uncommenting) runs the BUAP model with the given parameters; 
# this model additionally requires a set of open facilities as example of which we give below
open_facs = [1024, 1027, 1049, 1051, 1066, 1076, 1079, 1081, 1087, 1091, 1094, 1098, 1100, 1128, 1132, 1137, 1139, 1141, 1145, 1146, 1149, 1151, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1162, 1189, 1192, 1194, 1195, 1196, 1197, 1198, 1200, 1201, 1204, 1207, 1209, 1210, 1212, 1213, 1214, 1215, 1216, 1218, 1219, 1220, 1221, 1223, 1224, 1231, 1232, 1233, 1234, 1238, 1239, 1240, 1243, 1244, 1245, 1246, 1247, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1258, 1259, 1261, 1263, 1264, 1265, 1266, 1267, 1268, 1270, 1271, 1273, 1274, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1290, 1291, 1292, 1295, 1296, 1299, 1300, 1301, 1302, 1303, 1304, 1306, 1311, 1314, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1344, 1348, 1350, 1352, 1387]
results = get_results_all_BUAP_methods(users_and_facs_df, travel_dict, users, facs, open_facs,
                         cap_factor=1.5,define_u = True,cutoff_relaxation = 0.0,
                          num_consider_relaxation = 20,
                         cutoff_localsearch = 0.2, time_limit_while_localsearch = 1,
                         output_filename = "BUAP_heuristics.json")


# to write the results in a file, do:
#write_results_open_greedy_table("open_greedy_instance_1.json", "open_greedy_instance_1.xlsx","instance_1_BFLP_MIP.json")
