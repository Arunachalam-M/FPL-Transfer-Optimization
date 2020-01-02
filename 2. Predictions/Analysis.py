# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 15:40:23 2019

@author: arun_
"""

import pandas as pd
import statsmodels.api as sm
from patsy import dmatrices
from statistics import variance
from statistics import mean



data = pd.read_csv('FPL_Raw_Data.csv')

data = data.rename(columns = {'Home Team':'Home_Team', 'Away Team':'Away_Team', 'Goals Scored':'Goals_Scored', 'Goals Conceded':'Goals_Conceded'})

seasons = list(data['Season'].unique())

seasons.sort()

scoring_coefs = []
conceding_coefs = []

for sn in seasons:
    season_data = data[data['Season'] == sn]
    
    fm1 = """Goals_Scored ~  Home_Team + Away_Team - 1"""
    fm2 = """Goals_Conceded ~  Home_Team + Away_Team - 1"""
    
    y_train1, x_train1 = dmatrices(fm1, season_data, return_type = 'dataframe')
    y_train2, x_train2 = dmatrices(fm2, season_data, return_type = 'dataframe')
    
    model1 = sm.GLM(y_train1, x_train1, family=sm.families.Poisson())
    model2 = sm.GLM(y_train2, x_train2, family=sm.families.Poisson())
    
    results1 = model1.fit()
    results2 = model2.fit()
    
    model_fitted_y1 = results1.fittedvalues  
    model_fitted_y2 = results2.fittedvalues 
    
    results_df = pd.concat([y_train1, model_fitted_y1, y_train2, model_fitted_y2], ignore_index=True, axis = 1)
    results_df = results_df.rename(columns = {0:'y_train1', 1:'model_fitted_y1', 2:'y_train2', 3:'model_fitted_y2'})
    
    phi1 = variance(results_df['model_fitted_y1']) / mean(results_df['model_fitted_y1'])
    phi2 = variance(results_df['model_fitted_y2']) / mean(results_df['model_fitted_y2'])
    
    results_as_html = results1.summary().tables[1].as_html()
    scored_summary = pd.read_html(results_as_html, header=0, index_col=0)[0]
    
    results_as_html = results2.summary().tables[1].as_html()
    conceded_summary = pd.read_html(results_as_html, header=0, index_col=0)[0]
    
    scoring_coefs.append(scored_summary['coef'])
    conceding_coefs.append(conceded_summary['coef'])
    
    
scoring_df = pd.DataFrame(scoring_coefs[0])
scoring_df['team'] = scoring_df.index
scoring_df = scoring_df[['team', 'coef']]
scoring_df = scoring_df.rename(columns = {'coef':'coef_'+seasons[0]})


conceding_df = pd.DataFrame(conceding_coefs[0])
conceding_df['team'] = conceding_df.index
conceding_df = conceding_df[['team', 'coef']]
conceding_df = conceding_df.rename(columns = {'coef':'coef_'+seasons[0]})

for i in range(1,len(scoring_coefs)):
    new_df1 = pd.DataFrame(scoring_coefs[i])
    new_df1['team'] = new_df1.index
    scoring_df = scoring_df.merge(new_df1, how = 'outer', on = 'team', suffixes=('', '_'+seasons[i]))
    new_df2 = pd.DataFrame(conceding_coefs[i])
    new_df2['team'] = new_df2.index
    conceding_df = conceding_df.merge(new_df2, how = 'outer', on = 'team', suffixes=('', '_'+seasons[i]))


scoring_df.to_csv('Scoring.csv', index=False) #Home Scoring Strength and Away Defending Strength of teams
conceding_df.to_csv('Conceding.csv', index=False) #Home Defending Strength and Away Scoring Strength of teams

