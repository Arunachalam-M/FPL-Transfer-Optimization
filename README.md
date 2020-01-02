# FPL-Transfer-Optimization
 
# Problem
Every season, about 6 million users play the Fantasy Premier League. For those of you who are unfamiliar, it involves selecting a squad of 15 players and selecting a playing 11 among them. Points will be allotted depending on how the selected player perform in each match. You can check the detailed rules of FPL here - https://fantasy.premierleague.com/

How you perform in the league is determined by how good of a Football Pundit you are right? Mostly yes. But can we 'Moneyball' Premier League to better use your domain knowledge? This is a project which tries to do the same. 

The underlying structures we try to exploit here is that the fixtures are assigned in some random manner which leads to some teams not having a game in a game week. Some might have 2 games in a game week. A top tier team might have a series of clashes against weak teams. Intuition tells us we need to pick more forwards and mid-fielders that team, so that they have better opportunities to score more goals without the need to make transfers during that period. We have an option to use 2 wildcards to shuffle the entire team. When is the best time to use it. There are several other similar structural patterns emanating from the schedule of matches. This project purely tries to exploit it to find the best schedule of transfers i.e How many Forwards/Midfielders, Defenders to have in each team for each game week and how many transfers to make, to maximize the expected, points based the schedule of matches and past performance of teams. We do not focus on which individual players to pick and that might be best left to you, the Football pundit. What we are trying to do is to help you with the bigger picture, so that you can purely focus on which player you want to choose based on your experience.

# Approach
This is a fairly long expedition and we divide it into 3 main sections.

1. Scraping - Scraping the Premier League website to get the performance of teams for the past 5 seasons and the current year fixtures in a structured way for further analysis.

2. Predictions - We try to estimate this year results by executing the following 4 steps.
    a. Build a Poisson Regression model to estimate the Home and Away, Offensive and Defensive strength for all teams. 
    b. Imputation of these values for relegated teams and new teams. 
    c. Using Holts method to project forecasts for these parameters for the current season. 
    d. Using the forecasted coefficients to predict the results this year from the fixtures.
    
3. Optimization - We will use the predicted results from the previous prediction model to build an optimization model which gives us the required schedule of transfers according to which we will operate.


