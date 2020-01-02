# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 19:38:38 2019

@author: arun_
"""

import numpy as np
import pandas as pd
import matplotlib as plt
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from statistics import mean


scoring_df = pd.read_csv('Scoring.csv') #Home Scoring Strength and Away Defending Strength of teams
conceding_df = pd.read_csv('Conceding.csv') #Home Defending Strength and Away Scoring Strength of teams

fixtures_df = pd.read_csv('Fixtures.csv')
new_teams = list(fixtures_df['Home Team'].unique())

Home_Scoring_df = scoring_df[scoring_df['team'].str.contains('Home')].copy()
Home_Scoring_df['team'] = Home_Scoring_df['team'].apply(lambda x: x.replace("Home_Team[","")[:-1])
Home_Scoring_df.reset_index(drop=True, inplace=True)

Away_Defending_df = scoring_df[scoring_df['team'].str.contains('Away')].copy()
Away_Defending_df['team'] = Away_Defending_df['team'].apply(lambda x: x.replace("Away_Team[T.","")[:-1])
Away_Defending_df.reset_index(drop=True, inplace=True)


Away_Scoring_df = conceding_df[conceding_df['team'].str.contains('Away')].copy()
Away_Scoring_df['team'] = Away_Scoring_df['team'].apply(lambda x: x.replace("Away_Team[T.","")[:-1])
Away_Scoring_df.reset_index(drop=True, inplace=True)

Home_Defending_df = conceding_df[conceding_df['team'].str.contains('Home')].copy()
Home_Defending_df['team'] = Home_Defending_df['team'].apply(lambda x: x.replace("Home_Team[","")[:-1])
Home_Defending_df.reset_index(drop=True, inplace=True)

existing_teams = list(Home_Scoring_df['team'].unique())
added_teams = list(set(new_teams) - set(existing_teams))

dummy_list = [Home_Scoring_df.iloc[0]['team']]
dummy_list.extend(added_teams)
dummy_vals = [0]
dummy_vals.extend([np.nan]*len(added_teams))

cols = list(Home_Scoring_df.columns)
dummy_df = pd.DataFrame({"team": dummy_list, cols[1]:dummy_vals, cols[2]:dummy_vals, cols[3]:dummy_vals, cols[4]:dummy_vals, cols[5]:dummy_vals})

dummy_df2 = pd.DataFrame({"team": added_teams, cols[1]:[np.nan]*len(added_teams), cols[2]:[np.nan]*len(added_teams), cols[3]:[np.nan]*len(added_teams), cols[4]:[np.nan]*len(added_teams), cols[5]:[np.nan]*len(added_teams)})

Away_Defending_df = pd.concat([Away_Defending_df, dummy_df], ignore_index=True)
Away_Scoring_df = pd.concat([Away_Scoring_df, dummy_df], ignore_index=True)

Home_Scoring_df = pd.concat([Home_Scoring_df, dummy_df2], ignore_index=True)
Home_Defending_df = pd.concat([Home_Defending_df, dummy_df2], ignore_index=True)

na_hs = {}
na_hd = {}
na_as = {}
na_ad = {}

for i in range(1,len(cols)):
    na_hs[cols[i]] = mean(sorted(list(Home_Scoring_df.iloc[:,i].dropna()))[:3]) #Home Scoring: More is good. Worst 3 are picked for NA.
    na_hd[cols[i]] = mean(sorted(list(Home_Defending_df.iloc[:,i].dropna()))[-3:]) #Home Defending: Less is good. Worst 3 are picked for NA.
    na_as[cols[i]] = mean(sorted(list(Away_Scoring_df.iloc[:,i].dropna()))[:3]) #Away Scoring: More is good. Worst 3 are picked for NA.
    na_ad[cols[i]] = mean(sorted(list(Away_Defending_df.iloc[:,i].dropna()))[-3:]) #Away Defending: Less is good. Worst 3 are picked for NA.
    
Home_Scoring_df.fillna(value=na_hs, inplace = True)
Home_Defending_df.fillna(value=na_hd, inplace = True)
Away_Scoring_df.fillna(value=na_as, inplace = True)
Away_Defending_df.fillna(value=na_ad, inplace = True)

dataframes = [Home_Scoring_df, Home_Defending_df, Away_Scoring_df, Away_Defending_df]

hs_f, hd_f, as_f, ad_f = {}, {}, {}, {}
forecasts = [hs_f, hd_f, as_f, ad_f]

for df in range(len(dataframes)):
    plot_df = dataframes[df].copy()
    plot_df = plot_df.set_index('team').T
    #plot_df.plot(figsize=(40,20))
    teams = list(plot_df.columns)
    #abc_df = pd.Series(np.array(plot_df['Everton']))
    for team in teams:
        exp_sm = Holt(pd.Series(np.array(plot_df[team]))).fit(smoothing_level=0.9, smoothing_slope=0.5)
        fcast = exp_sm.forecast(1)
        forecasts[df][team] = fcast
        #exp_sm.fittedvalues.plot(marker="o", color='green')
        #fcast.plot(color='green', marker="o", legend=True)
        #abc_df.plot()
        #plt.show()

for i in range(len(forecasts)):
    forecasts[i] = pd.DataFrame(forecasts[i]).T
    forecasts[i] = forecasts[i].rename(columns = {5:'forecast_19-20'})
    forecasts[i]['team'] = forecasts[i].index

Home_Scoring_df = Home_Scoring_df.merge(forecasts[0], on = 'team')
Home_Defending_df = Home_Defending_df.merge(forecasts[1], on = 'team')
Away_Scoring_df = Away_Scoring_df.merge(forecasts[2], on = 'team')
Away_Defending_df = Away_Defending_df.merge(forecasts[3], on = 'team')

Home_Scoring_df.to_csv('Home_Scoring.csv', index=False)
Home_Defending_df.to_csv('Home_Defending.csv', index=False)
Away_Scoring_df.to_csv('Away_Scoring.csv', index=False)
Away_Defending_df.to_csv('Away_Defending.csv', index=False)

