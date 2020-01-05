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

We can observe that the residuals are evenly distributed about 0 and the variance of the residuals also seems acceptable. We can, of course, see some Outliers for eg. the Man City	- Watford match which was predicted to have a 3.14 -	0.71 result, but ended up 8 - 0 or the Southampton -	Leicester	fixture which was estimated to have a result along 1.32	- 2.13,	but the actual result was 0 - 9. We certainly cannot expect to predict such occurrences as even the Poisson model would suggest that there is some small probability of observing such results. We nevertheless try to optimize our decisions based on the most likely outcomes.

Please find the plots for the Home Attack Strength metric for each team across the past 5 years

![Exponential Smoothing](https://github.com/Arunachalam-M/FPL-Transfer-Optimization/blob/master/Forecasts.png)

The Results Analysis file and the Final Output Final_Transfer_Plan are also included in the repository for further analysis.

The predictions for this season matches purely based on past 5 year performances is provided below. We can make much better predictions during the season by taking into account the performance of the teams and the same can be used to dynamically update the FPL transfer plans using the same methodology described above.

Game Week|Home Team|Away Team|Goals by Home Team|Goal by Away Team
------------ | ------------- | ------------ | ------------- |------------
1|Leicester|Wolves|0.81|0.91
1|Newcastle|Arsenal|1.69|1.53
1|Man Utd|Chelsea|1.84|1.55
1|West Ham|Man City|0.57|2.23
1|Bournemouth|Sheffield Utd|2.62|0.65
1|Burnley|Southampton|1.81|1.34
1|Crystal Palace|Everton|0.76|1.22
1|Watford|Brighton|1.40|1.11
1|Spurs|Aston Villa|2.67|0.47
1|Liverpool|Norwich|5.00|0.22
2|Wolves|Man Utd|1.90|1.37
2|Sheffield Utd|Crystal Palace|0.76|2.76
2|Chelsea|Leicester|1.83|0.64
2|Arsenal|Burnley|2.82|0.90
2|Aston Villa|Bournemouth|1.29|2.22
2|Brighton|West Ham|0.94|1.04
2|Everton|Watford|1.45|1.39
2|Norwich|Newcastle|0.47|1.59
2|Southampton|Liverpool|0.47|2.56
2|Man City|Spurs|2.59|0.76
3|Spurs|Newcastle|1.07|0.75
3|Bournemouth|Man City|0.53|1.94
3|Wolves|Burnley|2.07|0.95
3|Norwich|Chelsea|0.77|1.68
3|Brighton|Southampton|1.38|0.98
3|Man Utd|Crystal Palace|1.76|2.58
3|Sheffield Utd|Leicester|0.70|2.22
3|Watford|West Ham|1.33|1.15
3|Liverpool|Arsenal|4.31|0.53
3|Aston Villa|Everton|0.63|1.94
4|Everton|Wolves|1.05|0.99
4|Arsenal|Spurs|1.88|1.17
4|Southampton|Man Utd|1.61|2.64
4|Chelsea|Sheffield Utd|3.11|0.28
4|Crystal Palace|Aston Villa|1.48|0.62
4|Leicester|Bournemouth|1.88|1.20
4|Man City|Brighton|3.12|0.42
4|Newcastle|Watford|1.24|1.56
4|West Ham|Norwich|2.88|0.74
4|Burnley|Liverpool|0.43|2.66
5|Aston Villa|West Ham|0.73|1.42
5|Bournemouth|Everton|1.37|1.27
5|Watford|Arsenal|1.93|1.89
5|Liverpool|Newcastle|2.03|0.36
5|Brighton|Burnley|1.24|1.40
5|Man Utd|Leicester|1.62|2.08
5|Sheffield Utd|Southampton|1.05|1.34
5|Spurs|Crystal Palace|1.66|1.32
5|Wolves|Chelsea|1.76|0.83
5|Norwich|Man City|0.23|2.97
6|Crystal Palace|Wolves|0.66|1.07
6|West Ham|Man Utd|2.05|2.08
6|Arsenal|Aston Villa|3.67|0.46
6|Chelsea|Liverpool|0.65|0.77
6|Leicester|Spurs|0.93|1.36
6|Burnley|Norwich|2.09|0.98
6|Everton|Sheffield Utd|2.29|0.57
6|Man City|Watford|3.14|0.72
6|Newcastle|Brighton|1.23|0.90
6|Southampton|Bournemouth|2.38|2.13
7|Man Utd|Arsenal|2.41|2.17
7|Leicester|Newcastle|0.73|0.85
7|Sheffield Utd|Liverpool|0.25|2.65
7|Bournemouth|West Ham|1.57|0.93
7|Aston Villa|Burnley|0.96|1.92
7|Chelsea|Brighton|1.96|0.40
7|Crystal Palace|Norwich|1.46|0.62
7|Spurs|Southampton|2.29|0.64
7|Wolves|Watford|1.68|1.18
7|Everton|Man City|0.46|1.73
8|Arsenal|Bournemouth|3.81|1.04
8|Man City|Wolves|2.27|0.51
8|Southampton|Chelsea|1.49|1.60
8|Newcastle|Man Utd|1.40|1.81
8|Brighton|Spurs|0.82|1.84
8|Burnley|Everton|1.08|1.93
8|Liverpool|Leicester|2.91|0.50
8|Norwich|Aston Villa|1.18|0.99
8|Watford|Sheffield Utd|2.22|0.80
8|West Ham|Crystal Palace|1.81|2.10
9|Sheffield Utd|Arsenal|1.04|2.32
9|Man Utd|Liverpool|0.58|2.48
9|Everton|West Ham|1.37|0.83
9|Bournemouth|Norwich|2.65|0.64
9|Aston Villa|Brighton|0.77|1.37
9|Chelsea|Newcastle|1.28|0.46
9|Leicester|Burnley|1.39|1.04
9|Spurs|Watford|1.66|1.13
9|Wolves|Southampton|2.31|0.67
9|Crystal Palace|Man City|0.29|1.87
10|Newcastle|Wolves|0.89|1.11
10|Arsenal|Crystal Palace|2.28|1.30
10|Liverpool|Spurs|2.59|0.57
10|Norwich|Man Utd|0.83|2.77
10|Man City|Aston Villa|5.05|0.30
10|Brighton|Everton|0.82|1.42
10|Watford|Bournemouth|2.35|1.80
10|West Ham|Sheffield Utd|2.85|0.74
10|Burnley|Chelsea|1.38|1.66
10|Southampton|Leicester|1.32|2.14
11|Everton|Spurs|1.20|1.47
11|Crystal Palace|Leicester|0.85|1.41
11|Bournemouth|Man Utd|1.88|1.81
11|Arsenal|Wolves|1.65|0.79
11|Aston Villa|Liverpool|0.25|2.67
11|Brighton|Norwich|1.59|0.72
11|Man City|Southampton|4.33|0.41
11|Sheffield Utd|Burnley|0.94|1.91
11|West Ham|Newcastle|1.17|1.20
11|Watford|Chelsea|1.48|1.35
12|Man Utd|Brighton|1.75|1.28
12|Wolves|Aston Villa|2.70|0.49
12|Liverpool|Man City|0.99|0.67
12|Chelsea|Crystal Palace|1.98|0.80
12|Burnley|West Ham|1.24|1.41
12|Newcastle|Bournemouth|2.06|1.46
12|Southampton|Everton|1.17|1.85
12|Spurs|Sheffield Utd|2.62|0.47
12|Leicester|Arsenal|1.54|1.26
12|Norwich|Watford|0.73|2.39
13|Aston Villa|Newcastle|0.50|1.58
13|Sheffield Utd|Man Utd|0.86|2.74
13|West Ham|Spurs|1.49|1.90
13|Bournemouth|Wolves|1.20|1.11
13|Arsenal|Southampton|3.15|0.63
13|Brighton|Leicester|0.92|1.63
13|Crystal Palace|Liverpool|0.30|1.69
13|Everton|Norwich|2.31|0.57
13|Watford|Burnley|1.74|1.55
13|Man City|Chelsea|3.29|0.51
14|Norwich|Arsenal|1.00|2.34
14|Wolves|Sheffield Utd|2.64|0.49
14|Leicester|Everton|0.93|1.04
14|Man Utd|Aston Villa|2.82|0.91
14|Newcastle|Man City|0.39|1.94
14|Burnley|Crystal Palace|1.31|2.76
14|Chelsea|West Ham|1.86|0.41
14|Liverpool|Brighton|3.13|0.31
14|Spurs|Bournemouth|2.77|1.06
14|Southampton|Watford|1.42|2.28
15|Arsenal|Brighton|2.27|0.64
15|Sheffield Utd|Newcastle|0.49|1.57
15|Chelsea|Aston Villa|3.18|0.28
15|Leicester|Watford|1.13|1.28
15|Man Utd|Spurs|1.45|2.33
15|Southampton|Norwich|2.27|0.94
15|Wolves|West Ham|1.58|0.70
15|Liverpool|Everton|2.59|0.44
15|Crystal Palace|Bournemouth|1.53|1.41
15|Burnley|Man City|0.41|2.94
16|West Ham|Arsenal|2.48|1.76
16|Aston Villa|Leicester|0.71|2.23
16|Newcastle|Southampton|1.70|0.88
16|Norwich|Sheffield Utd|1.15|0.99
16|Brighton|Wolves|0.72|1.24
16|Everton|Chelsea|1.52|0.98
16|Bournemouth|Liverpool|0.55|1.75
16|Spurs|Burnley|2.06|0.91
16|Watford|Crystal Palace|1.41|2.25
16|Man City|Man Utd|3.55|0.83
17|Crystal Palace|Brighton|0.91|0.87
17|Man Utd|Everton|1.44|1.80
17|Wolves|Spurs|1.38|1.25
17|Arsenal|Man City|0.72|1.38
17|Liverpool|Watford|3.14|0.54
17|Burnley|Newcastle|0.85|1.57
17|Chelsea|Bournemouth|3.30|0.64
17|Leicester|Norwich|1.79|0.53
17|Sheffield Utd|Aston Villa|1.22|0.98
17|Southampton|West Ham|1.34|1.36
18|Watford|Man Utd|1.59|2.23
18|Spurs|Chelsea|1.74|0.79
18|Everton|Arsenal|1.99|1.36
18|Bournemouth|Burnley|2.06|1.26
18|Aston Villa|Southampton|1.07|1.35
18|Brighton|Sheffield Utd|1.57|0.72
18|Newcastle|Crystal Palace|1.24|1.82
18|Norwich|Wolves|0.53|1.70
18|Man City|Leicester|2.90|0.68
19|Wolves|Man City|0.53|1.47
19|Spurs|Brighton|1.65|0.65
19|Bournemouth|Arsenal|2.28|1.53
19|Aston Villa|Norwich|1.23|0.98
19|Chelsea|Southampton|2.73|0.39
19|Crystal Palace|West Ham|0.87|0.90
19|Everton|Burnley|1.80|1.12
19|Sheffield Utd|Watford|0.76|2.37
19|Man Utd|Newcastle|1.14|1.47
19|Leicester|Liverpool|0.37|1.44
20|Brighton|Bournemouth|1.67|1.63
20|Newcastle|Everton|1.02|1.27
20|Southampton|Crystal Palace|1.42|2.66
20|Watford|Aston Villa|2.27|0.80
20|Norwich|Spurs|0.60|2.52
20|West Ham|Leicester|1.67|1.69
20|Burnley|Man Utd|1.49|2.74
20|Arsenal|Chelsea|2.39|0.78
20|Liverpool|Wolves|2.27|0.38
20|Man City|Sheffield Utd|4.94|0.30
21|Brighton|Chelsea|1.05|1.22
21|Burnley|Aston Villa|2.11|0.98
21|Newcastle|Leicester|1.14|1.47
21|Southampton|Spurs|1.17|2.40
21|Watford|Wolves|1.02|1.37
21|Man City|Everton|2.58|0.59
21|Norwich|Crystal Palace|0.73|2.79
21|West Ham|Bournemouth|3.02|1.68
21|Arsenal|Man Utd|2.58|1.29
21|Liverpool|Sheffield Utd|4.95|0.22
22|Sheffield Utd|West Ham|0.72|1.41
22|Crystal Palace|Arsenal|1.26|1.47
22|Chelsea|Burnley|2.44|0.55
22|Everton|Brighton|1.45|0.80
22|Leicester|Southampton|1.55|0.73
22|Man Utd|Norwich|2.80|0.91
22|Wolves|Newcastle|1.08|0.79
22|Spurs|Liverpool|0.55|1.27
22|Bournemouth|Watford|1.67|1.56
22|Aston Villa|Man City|0.24|2.95
23|Watford|Spurs|1.16|2.03
23|Arsenal|Sheffield Utd|3.59|0.46
23|Brighton|Aston Villa|1.61|0.72
23|Man City|Crystal Palace|3.14|0.84
23|Norwich|Bournemouth|1.22|2.23
23|Southampton|Wolves|1.03|1.62
23|West Ham|Everton|1.49|1.46
23|Newcastle|Chelsea|1.30|1.10
23|Burnley|Leicester|1.21|2.22
23|Liverpool|Man Utd|3.55|0.62
24|Bournemouth|Brighton|1.65|0.90
24|Aston Villa|Watford|0.77|2.38
24|Crystal Palace|Southampton|1.27|0.85
24|Everton|Newcastle|0.94|0.92
24|Sheffield Utd|Man City|0.24|2.94
24|Chelsea|Arsenal|2.71|0.67
24|Leicester|West Ham|1.06|0.76
24|Spurs|Norwich|2.65|0.47
24|Man Utd|Burnley|2.17|1.78
24|Wolves|Liverpool|0.55|1.33
25|West Ham|Liverpool|0.60|2.02
25|Leicester|Chelsea|1.18|0.90
25|Bournemouth|Aston Villa|2.68|0.64
25|Crystal Palace|Sheffield Utd|1.45|0.62
25|Liverpool|Southampton|4.34|0.30
25|Newcastle|Norwich|1.97|0.64
25|Watford|Everton|1.16|1.57
25|West Ham|Brighton|1.80|1.04
25|Man Utd|Wolves|1.27|1.58
25|Burnley|Arsenal|1.80|2.32
25|Spurs|Man City|0.52|1.40
26|Everton|Crystal Palace|1.45|1.62
26|Brighton|Watford|1.00|1.74
26|Sheffield Utd|Bournemouth|1.27|2.21
26|Man City|West Ham|2.96|0.43
26|Wolves|Leicester|1.55|1.11
26|Southampton|Burnley|1.76|1.84
26|Norwich|Liverpool|0.24|2.68
26|Aston Villa|Spurs|0.64|2.51
26|Arsenal|Newcastle|1.48|0.74
26|Chelsea|Man Utd|2.23|0.79
27|Chelsea|Spurs|1.63|0.72
27|Burnley|Bournemouth|2.19|2.21
27|Crystal Palace|Newcastle|0.59|1.00
27|Sheffield Utd|Brighton|0.76|1.36
27|Southampton|Aston Villa|2.29|0.94
27|Leicester|Man City|0.36|1.60
27|Man Utd|Watford|1.76|2.21
27|Wolves|Norwich|2.67|0.49
27|Arsenal|Everton|1.88|0.90
27|Liverpool|West Ham|2.97|0.32
28|Norwich|Leicester|0.68|2.24
28|Brighton|Crystal Palace|1.00|2.03
28|Bournemouth|Chelsea|1.75|1.10
28|Aston Villa|Sheffield Utd|1.22|0.98
28|Newcastle|Burnley|1.53|1.26
28|West Ham|Southampton|2.50|1.02
28|Watford|Liverpool|0.46|2.16
28|Everton|Man Utd|1.64|1.61
28|Man City|Arsenal|4.31|0.71
28|Spurs|Wolves|1.20|0.81
29|Arsenal|West Ham|2.15|0.66
29|Burnley|Spurs|1.08|2.50
29|Chelsea|Everton|1.62|0.56
29|Crystal Palace|Watford|0.92|1.50
29|Leicester|Aston Villa|1.81|0.53
29|Liverpool|Bournemouth|5.24|0.50
29|Man Utd|Man City|0.55|2.75
29|Sheffield Utd|Norwich|1.21|0.98
29|Southampton|Newcastle|0.92|1.52
29|Wolves|Brighton|1.67|0.68
30|Bournemouth|Crystal Palace|1.66|1.82
30|Aston Villa|Chelsea|0.81|1.67
30|Brighton|Arsenal|1.37|1.70
30|Everton|Liverpool|0.48|1.56
30|Man City|Burnley|3.88|0.58
30|Newcastle|Sheffield Utd|1.95|0.65
30|Norwich|Southampton|1.01|1.35
30|Spurs|Man Utd|1.88|1.31
30|Watford|Leicester|1.30|1.81
30|West Ham|Wolves|1.31|1.28
31|Burnley|Watford|1.31|2.37
31|Chelsea|Man City|0.62|0.85
31|Leicester|Brighton|1.12|0.74
31|Liverpool|Crystal Palace|3.14|0.63
31|Man Utd|Sheffield Utd|2.77|0.92
31|Newcastle|Aston Villa|1.99|0.64
31|Norwich|Everton|0.60|1.94
31|Southampton|Arsenal|1.95|2.23
31|Spurs|West Ham|1.57|0.67
31|Wolves|Bournemouth|2.80|1.11
32|Bournemouth|Newcastle|1.08|1.04
32|Arsenal|Norwich|3.63|0.46
32|Aston Villa|Wolves|0.56|1.70
32|Brighton|Man Utd|1.13|2.01
32|Crystal Palace|Burnley|1.14|1.21
32|Everton|Leicester|1.34|1.30
32|Man City|Liverpool|1.03|0.81
32|Sheffield Utd|Spurs|0.63|2.50
32|Watford|Southampton|1.95|1.09
32|West Ham|Chelsea|1.90|1.26
33|Burnley|Sheffield Utd|2.07|0.98
33|Chelsea|Watford|1.98|0.69
33|Leicester|Crystal Palace|1.13|1.50
33|Liverpool|Aston Villa|5.05|0.22
33|Man Utd|Bournemouth|2.93|2.07
33|Newcastle|West Ham|1.17|0.93
33|Norwich|Brighton|0.73|1.38
33|Southampton|Man City|0.45|2.83
33|Spurs|Everton|1.37|0.92
33|Wolves|Arsenal|2.30|1.16
34|Bournemouth|Spurs|1.37|1.65
34|Arsenal|Leicester|2.11|1.04
34|Aston Villa|Man Utd|0.87|2.75
34|Brighton|Liverpool|0.33|1.95
34|Crystal Palace|Chelsea|0.96|1.06
34|Everton|Southampton|2.01|0.79
34|Man City|Newcastle|2.03|0.48
34|Sheffield Utd|Wolves|0.55|1.69
34|Watford|Norwich|2.24|0.79
34|West Ham|Burnley|2.24|1.45
35|Bournemouth|Leicester|1.54|1.46
35|Aston Villa|Crystal Palace|0.77|2.78
35|Brighton|Man City|0.32|2.16
35|Liverpool|Burnley|3.89|0.43
35|Man Utd|Southampton|2.42|1.25
35|Norwich|West Ham|0.69|1.42
35|Sheffield Utd|Chelsea|0.80|1.66
35|Spurs|Arsenal|2.28|1.11
35|Watford|Newcastle|0.91|1.28
35|Wolves|Everton|1.38|0.96
36|Arsenal|Liverpool|0.75|1.25
36|Burnley|Wolves|0.95|1.69
36|Chelsea|Norwich|3.14|0.28
36|Crystal Palace|Man Utd|1.04|1.74
36|Everton|Aston Villa|2.34|0.57
36|Leicester|Sheffield Utd|1.77|0.53
36|Man City|Bournemouth|5.24|0.67
36|Newcastle|Spurs|1.02|1.65
36|Southampton|Brighton|1.42|1.31
36|West Ham|Watford|1.81|1.80
37|Bournemouth|Southampton|2.30|0.88
37|Aston Villa|Arsenal|1.06|2.33
37|Brighton|Newcastle|0.65|1.16
37|Liverpool|Chelsea|3.30|0.38
37|Man Utd|West Ham|1.66|1.32
37|Norwich|Burnley|0.91|1.93
37|Sheffield Utd|Everton|0.63|1.92
37|Spurs|Leicester|1.54|1.06
37|Watford|Man City|0.44|2.39
37|Wolves|Crystal Palace|1.68|1.38
38|Arsenal|Watford|2.28|1.11
38|Burnley|Brighton|1.31|1.37
38|Chelsea|Wolves|1.43|0.49
38|Crystal Palace|Spurs|0.76|1.59
38|Everton|Bournemouth|2.43|1.30
38|Leicester|Man Utd|1.27|1.49
38|Man City|Norwich|5.00|0.30
38|Newcastle|Liverpool|0.41|1.75
38|Southampton|Sheffield Utd|2.24|0.94
38|West Ham|Aston Villa|2.91|0.74
