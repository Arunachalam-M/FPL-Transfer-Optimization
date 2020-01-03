# FPL-Transfer-Optimization
 
# Problem
Every season, about 6 million users play the Fantasy Premier League. For those of you who are unfamiliar, it involves selecting a squad of 15 players and selecting a playing 11 among them. Points will be allotted depending on how the selected player performs in each match. You can check the detailed rules of FPL here - https://fantasy.premierleague.com/

How you perform in the league is determined by how good of a Football Pundit you are right? Mostly yes. But can we 'Moneyball' Premier League to better use your domain knowledge? This is a project which tries to do the same.

The underlying structures we try to exploit here is that the fixtures are assigned in some random manner which leads to some teams not having a game in a game week. Some might have 2 games in a game week. A top tier team might have a series of clashes against weak teams. Intuition tells us we need to pick more forwards and mid-fielders that team so that they have better opportunities to score more goals without the need to make transfers during that period. We have an option to use 2 wildcards to shuffle the entire team. When is the best time to use it? There are several other similar structural patterns emanating from the schedule of matches. This project purely tries to exploit it to find the best schedule of transfers i.e How many Forwards/Midfielders, Defenders to have in each team for each game week and how many transfers to make, to maximize the expected, points-based the schedule of matches and past performance of teams. We do not focus on which individual players to pick and that might be best left to you, the Football pundit. What we are trying to do is to help you with the bigger picture, so that you can purely focus on which player you want to choose based on your experience.

# Approach
This is a fairly long expedition and we divide it into 3 main sections.

1. Scraping - Scraping the Premier League website to get the performance of teams for the past 5 seasons and the current year fixtures in a structured way for further analysis.

2. Predictions - We try to estimate this year results by executing the following 5 steps.
    a. Build a Poisson Regression model to estimate the Home and Away, Offensive and Defensive strength for all teams. 
    b. Imputation of these values for relegated teams and new teams. 
    c. Using Holts method to project forecasts for these parameters for the current season. 
    d. Using the forecasted coefficients to predict the results this year from the fixtures.
    e. Use the Probability Distribution for Goals scored to predict the estimated points.
    
3. Optimization - We will use the predicted results from the previous prediction model to build an optimization model which gives us the required schedule of transfers according to which we will operate.

# Key Details of Implementation
The entire code is shared here. This section will cover the major things covered in each section

1. Scraping - Scraping should be a really easy process with Beautiful Soup, but there is a small obstruction in this case. The results site does not load all the entries at once and the results are loaded as you scroll down. We use selenium web driver with firefox to automatically open web pages and scroll down to the end of the page at repeated intervals. Once the entire results section id downloaded, the results are mined using beautiful soup for making predictions in the next section.

2. Predictions - 
    1. We build a Poisson regression model with no intercept. We build to separate models for predicting Goals Scored and Goals Conceded. The predictors are just the Home Team and Away Team. So we have 20 teams and 19x2 dummy variables since the teams are factors. Arsenal is chosen as the reference variable (Alphabetically by default) and all the coefficients are relative to it. The primary reason for using a Poisson regression model is that all the coefficients have interpretable meanings and we can understand how a Team's coefficients for eg. Defensive Strength at Home, will evolve from season to season. The number of Goals scored is discrete and is one of the metrics which can be modeled well using a Poisson distribution.
    2. Another Difficulty with Premier League is relegations and the possibility of teams with no past playing history playing this time. Now we might be tempted to fill these values with 0, but remember, the reference chosen here is Arsenal (Alphabetically chosen) whose Defensive Strength is coded as 0. To make a reasonable approximation, we take the mean values of the 3 teams which have the worst coefficients of a particular coefficient and use it to impute the coefficients for the teams which did not play the league that year.
    3. Since we do not know how teams are going to perform this year, it is imperative to forecast the coefficients for this year. Using last year's value might be a good idea, but we observe regression to the mean in all walks of life and we not want one offseason to throw off our predictions for the season or vice versa. Since there is no reason to expect seasonality in a team's performance, we use Holt's Linear Trend method to do simple exponential smoothing accounting for trends. This gives us the expected values for Offensive Home Strength, Defensive Home Strength, Offensive Away Strength, and Defensive Away Strength, the 4 parameters we use to predict home and away goals.
    4. With the forecasted parameters above, we can use the Poisson regression equation to predict the Goals scored for and against for each match in the fixtures. 
    5. In this step, we have to convert these distributions of expected goals to expected points. Each clean sheet is worth 4 points for a defending player. Each Goal is worth 4 or 5 points for an attacking player depending on if he is a forward or midfielder. The expected points per defender are the probability that the number of goals will be 0 x 4 points. For a Poisson distribution, the probability of getting 0 goals reduces to e^(-mean_expected_goals). For the expected points per attacking player, we just need to multiply the estimated number of goals with the points per goal divided by the number of possible attacking players to choose from. The last variable 'Likelihood of Chosen Attacking Player to score' is subject to change depending on your skill. If you have the option to choose an attacking player and you are always able to choose the right one, you can enter this value as 1. I have used a placeholder value of 1/3 from past experience.
    
3. Optimization - We need to build a convex optimization problem preferably linear to get our final results. But linearizing functions is tricky. The Goal of our optimization model is to maximize the expected points. The constraints will be the maximum defenders, maximum attacking players, maximum players from a team. It will also be tricky to model the use of wild cards, which allows you to shuffle entire teams without losing points. Another key modeling requirement is if it is worth losing 4 points to accommodate an extra transfer. This will occur more often if you choose a higher value for the variable 'Likelihood of Chosen Attacking Player to score'. Skipping the mathematical tricks to linearize the model, we have obtained the optimal transfer schedule for players.

# Results
Since this season is half done, I have provided the expectation vs reality to see how well our model predicted the results so far. I obtained an MSPE of about 1.66 goals and MAD of about 1 Goal. 

Provided below are some of the sanity checks for Goodness of Fit

![Residual Distribution 1](https://github.com/Arunachalam-M/FPL-Transfer-Optimization/blob/master/Residuals1.jpg)
![Residual Distribution 2](https://github.com/Arunachalam-M/FPL-Transfer-Optimization/blob/master/Residuals2.jpg)

We can observe that the residuals are evenly distributed about 0 and the variance of the residuals also seems acceptable. We can, of course, see some Outliers for eg. the Man City	- Watford match which was predicted to have a 3.14 -	0.71 result, but ended up 8 - 0 or the Southampton -	Leicester	fixture which was estimated to have a result along 1.32	- 2.13,	but the actual result was 0 - 9. We certainly cannot expect to predict suck occurrences as even the Poisson model would suggest that there is some small probability of observing such results. We nevertheless try to optimize our decisions based on the most likely outcomes.

Please find the plots for the Home Attack Strength metric for each team across the past 5 years

![Exponential Smoothing](https://github.com/Arunachalam-M/FPL-Transfer-Optimization/blob/master/Forecasts.png)

The Results Analysis file and the Final Output Final_Transfer_Plan are also included in the repository for further analysis.
