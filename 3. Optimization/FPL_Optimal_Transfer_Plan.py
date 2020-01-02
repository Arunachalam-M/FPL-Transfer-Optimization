# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 22:23:02 2019

@author: arun_
"""

from pulp import *
import pandas as pd
import math
import time
import numpy as np

start_time = time.time()

max_players_in_team = 3
Wildcards = 2
Permitted_Trasfers_Per_GameWeek = 1
Total_Players = 11
max_defenders = 7
max_attackers = 8
clean_sheet_points = 4
average_goal_points = 4
Playing_points = 2
points_lost_per_transfer = 4

#Custom Entries
Pick_Accuracy = float(1/3) #For attackers

schedule = pd.read_excel('FPL_Data.xlsx', sheet_name = 'Schedule')
attack = pd.read_excel('FPL_Data.xlsx', sheet_name = 'Attack')
defend = pd.read_excel('FPL_Data.xlsx', sheet_name = 'Defend')
gameweeks = pd.read_excel('FPL_Data.xlsx', sheet_name = 'Game Weeks')

schedule.drop(['Home Team', 'Away Team'], axis=1, inplace = True)
attack.drop(['Home Team', 'Away Team', 'Home Goals Predicted', 'Away Goals Predicted'], axis=1, inplace = True)
defend.drop(['Home Team', 'Away Team', 'Home Goals Predicted', 'Away Goals Predicted'], axis=1, inplace = True)

teams = list(schedule.columns)

Match_arr = sorted(list(gameweeks['Game Week'].unique()))
sub_match_arr = Match_arr[1:]
lone_variable = [0]

#Probability of 0 goals for away team = e^-lambda in a Poisson distribution
defender_points = defend.applymap(lambda x: clean_sheet_points*math.exp(x)%4)
attacker_points = attack.applymap(lambda x: Pick_Accuracy*average_goal_points*x)

defender_points['Match No'] = defender_points.index
attacker_points['Match No'] = attacker_points.index
defender_points['GameWeek'] = pd.to_numeric(defender_points['Match No'].apply(lambda x: gameweeks.iloc[x]['Game Week']))
attacker_points['GameWeek'] =  pd.to_numeric(attacker_points['Match No'].apply(lambda x: gameweeks.iloc[x]['Game Week']))

defender_points.drop(['Match No'], axis=1, inplace = True)
attacker_points.drop(['Match No'], axis=1, inplace = True)

defender_points = defender_points.groupby(['GameWeek'], as_index=False).sum()
attacker_points = attacker_points.groupby(['GameWeek'], as_index=False).sum()

defender_points.set_index('GameWeek', inplace=True) 
attacker_points.set_index('GameWeek', inplace=True) 

#Define the problem
fpl_prob = LpProblem("Team Teansfer Scheduling", LpMaximize)

#Define LP Variables
Defenders = LpVariable.dicts("Number of Defenders",(Match_arr,teams),0,max_players_in_team)
Attackers = LpVariable.dicts("Number of Attackers",(Match_arr,teams),0,max_players_in_team)
Players = LpVariable.dicts("Number of Players",(Match_arr,teams),0,max_players_in_team)
Transfers = LpVariable.dicts("Number of Transfers",(Match_arr[1:],teams),0,2*Total_Players)
Full_Shuffle = LpVariable.dicts("Wildcard Use",(Match_arr[1:]),0,1,LpBinary)
Additional_Transfers_per_Match = LpVariable.dicts("Number of Transfers",sub_match_arr,0,2*Total_Players)
Additional_Transfers = LpVariable.dicts("Number of Additional Transfers",lone_variable,0,len(Match_arr)*15)

#Objective Function
fpl_prob += lpSum([[(defender_points.iloc[i-1][j]*Defenders[i][j] + attacker_points.iloc[i-1][j]*Attackers[i][j] + Playing_points*Players[i][j]) for j in teams] for i in Match_arr]) - Additional_Transfers[0]*points_lost_per_transfer

#Constraints
for i in Match_arr:
    for j in teams:
        fpl_prob += Defenders[i][j]+ Attackers[i][j] == Players[i][j]

for i in Match_arr:
    fpl_prob += lpSum([Defenders[i][j] for j in teams]) <= max_defenders
    fpl_prob += lpSum([Attackers[i][j] for j in teams]) <= max_attackers
    fpl_prob += lpSum([Players[i][j] for j in teams]) == Total_Players

for i in sub_match_arr:
    fpl_prob += Additional_Transfers_per_Match[i] >= 0
    fpl_prob += lpSum([Transfers[i][j] for j in teams]) - 2*Permitted_Trasfers_Per_GameWeek - 2*Total_Players*Full_Shuffle[i] <= 2*Additional_Transfers_per_Match[i]
    
    
fpl_prob += lpSum([Additional_Transfers_per_Match[i] for i in sub_match_arr]) <= Additional_Transfers

fpl_prob += lpSum([Full_Shuffle[i] for i in sub_match_arr]) <= Wildcards

for i in sub_match_arr:
    for j in teams:
        fpl_prob += Players[i][j] - Players[i-1][j] <= Transfers[i][j]
        fpl_prob += Players[i-1][j] - Players[i][j] <= Transfers[i][j]
    
fpl_prob.writeLP("FPL_Problem.lp")

fpl_prob.solve()

print("Status:", LpStatus[fpl_prob.status])

results = []
for v in fpl_prob.variables():
    if v.varValue > 0:
        results.append(v.name + " = " + str(v.varValue))
        print(v.name, " = ", v.varValue)
    
print("Total Player value is ", value(fpl_prob.objective))

results.append("Total points expected is " + str(value(fpl_prob.objective)))

time_taken = time.time() - start_time

print("Time taken is ", time_taken)

results.append("Time taken is " + str(time_taken))

result_string = "\n".join(results)

file1 = open("Optimization_Results.txt","w+")
file1.write(result_string) 
file1.close()

attack_results = pd.DataFrame.from_dict(Attackers, orient='index')
attack_results = attack_results.applymap(lambda x: x.varValue)
attack_results = attack_results.applymap(np.int64)

defend_results = pd.DataFrame.from_dict(Defenders, orient='index')
defend_results = defend_results.applymap(lambda x: x.varValue)
defend_results = defend_results.applymap(np.int64)

player_results = pd.DataFrame.from_dict(Players, orient='index')
player_results = player_results.applymap(lambda x: x.varValue)
player_results = player_results.applymap(np.int64)

with pd.ExcelWriter('Final_Transfer_Plan.xlsx') as writer:
    player_results.to_excel(writer, sheet_name = 'Total Players')
    attack_results.to_excel(writer, sheet_name = 'Attacking Players')
    defend_results.to_excel(writer, sheet_name = 'Defending Players')
