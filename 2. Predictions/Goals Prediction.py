# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 01:26:17 2019

@author: arun_
"""

import pandas as pd
import math

Home_Scoring_df = pd.read_csv('Home_Scoring.csv')
Home_Defending_df = pd.read_csv('Home_Defending.csv')
Away_Scoring_df = pd.read_csv('Away_Scoring.csv')
Away_Defending_df = pd.read_csv('Away_Defending.csv')

Home_Scoring_df = Home_Scoring_df.set_index('team')
Home_Scoring = pd.Series(Home_Scoring_df['forecast_19-20'])

Home_Defending_df = Home_Defending_df.set_index('team')
Home_Defending = pd.Series(Home_Defending_df['forecast_19-20'])

Away_Scoring_df = Away_Scoring_df.set_index('team')
Away_Scoring = pd.Series(Away_Scoring_df['forecast_19-20'])

Away_Defending_df = Away_Defending_df.set_index('team')
Away_Defending = pd.Series(Away_Defending_df['forecast_19-20'])


fixtures_df = pd.read_csv('Fixtures.csv')

fixtures_df['Home Goals Predicted'] = fixtures_df.apply(lambda x: math.exp(Home_Scoring[x['Home Team']] + Away_Defending[x['Away Team']]),axis = 1) #Home Scoring Strength and Away Defending Strength of teams

fixtures_df['Away Goals Predicted'] = fixtures_df.apply(lambda x: math.exp(Home_Defending[x['Home Team']] + Away_Scoring[x['Away Team']]),axis = 1) #Home Defending Strength and Away Scoring Strength of teams

fixtures_df.to_csv('predicted_results.csv', index = False)