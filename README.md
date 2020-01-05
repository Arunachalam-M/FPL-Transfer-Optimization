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

Game Week|Home Team|Away Team|Home Win %|Away Win %|Draw %
------------ | ------------- | ------------ | ------------- | ------------ | ------------
1|Leicester|Wolves|30.36|35.99|33.64
1|Newcastle|Arsenal|41.88|34.87|23.25
1|Man Utd|Chelsea|44.77|32.8|22.43
1|West Ham|Man City|7.96|75.43|16.61
1|Bournemouth|Sheffield Utd|79.58|6.86|13.56
1|Burnley|Southampton|48.63|28.43|22.94
1|Crystal Palace|Everton|22.88|47.25|29.87
1|Watford|Brighton|43.58|29.84|26.58
1|Spurs|Aston Villa|83.95|4.39|11.66
1|Liverpool|Norwich|98.46|0.22|1.32
2|Wolves|Man Utd|49.84|27.8|22.36
2|Sheffield Utd|Crystal Palace|7.67|79.04|13.29
2|Chelsea|Leicester|65.77|12.49|21.75
2|Arsenal|Burnley|77.18|9.11|13.71
2|Aston Villa|Bournemouth|21.41|58.6|19.99
2|Brighton|West Ham|32.08|36.92|31.0
2|Everton|Watford|38.97|35.99|25.04
2|Norwich|Newcastle|10.71|65.06|24.23
2|Southampton|Liverpool|4.84|82.5|12.66
2|Man City|Spurs|76.62|8.69|14.69
3|Spurs|Newcastle|42.73|25.3|31.97
3|Bournemouth|Man City|9.1|71.24|19.66
3|Wolves|Burnley|63.21|16.45|20.33
3|Norwich|Chelsea|16.91|59.1|23.99
3|Brighton|Southampton|45.97|26.81|27.22
3|Man Utd|Crystal Palace|25.73|55.8|18.48
3|Sheffield Utd|Leicester|10.34|71.97|17.69
3|Watford|West Ham|40.88|32.11|27.01
3|Liverpool|Arsenal|94.72|1.37|3.91
3|Aston Villa|Everton|11.31|68.33|20.36
4|Everton|Wolves|36.35|33.19|30.47
4|Arsenal|Spurs|53.89|23.61|22.49
4|Southampton|Man Utd|22.36|59.69|17.95
4|Chelsea|Sheffield Utd|91.32|1.64|7.04
4|Crystal Palace|Aston Villa|58.01|15.59|26.4
4|Leicester|Bournemouth|53.24|24.25|22.51
4|Man City|Brighton|89.28|2.62|8.1
4|Newcastle|Watford|30.19|44.9|24.91
4|West Ham|Norwich|80.97|6.78|12.25
4|Burnley|Liverpool|4.04|84.46|11.5
5|Aston Villa|West Ham|19.25|53.47|27.29
5|Bournemouth|Everton|39.25|34.62|26.13
5|Watford|Arsenal|40.31|38.47|21.22
5|Liverpool|Newcastle|77.4|5.46|17.15
5|Brighton|Burnley|33.13|40.82|26.05
5|Man Utd|Leicester|30.48|48.42|21.11
5|Sheffield Utd|Southampton|29.36|43.27|27.37
5|Spurs|Crystal Palace|45.51|30.49|23.99
5|Wolves|Chelsea|59.38|17.42|23.2
5|Norwich|Man City|1.45|91.14|7.4
6|Crystal Palace|Wolves|22.48|44.92|32.6
6|West Ham|Man Utd|39.17|40.49|20.33
6|Arsenal|Aston Villa|92.4|1.89|5.7
6|Chelsea|Liverpool|27.46|34.68|37.86
6|Leicester|Spurs|25.67|46.67|27.66
6|Burnley|Norwich|63.02|16.72|20.26
6|Everton|Sheffield Utd|76.27|7.67|16.06
6|Man City|Watford|84.29|5.37|10.34
6|Newcastle|Brighton|43.72|27.11|29.17
6|Southampton|Bournemouth|44.83|35.88|19.29
7|Man Utd|Arsenal|44.82|36.04|19.14
7|Leicester|Newcastle|28.64|35.9|35.46
7|Sheffield Utd|Liverpool|2.11|88.12|9.77
7|Bournemouth|West Ham|52.36|22.3|25.34
7|Aston Villa|Burnley|18.28|59.89|21.83
7|Chelsea|Brighton|75.17|6.48|18.35
7|Crystal Palace|Norwich|57.63|15.75|26.62
7|Spurs|Southampton|74.79|8.71|16.5
7|Wolves|Watford|48.93|26.94|24.13
7|Everton|Man City|9.28|68.62|22.1
8|Arsenal|Bournemouth|85.56|5.73|8.71
8|Man City|Wolves|77.38|6.82|15.8
8|Southampton|Chelsea|35.77|40.39|23.85
8|Newcastle|Man Utd|29.83|47.27|22.9
8|Brighton|Spurs|16.34|61.34|22.32
8|Burnley|Everton|20.94|57.05|22.01
8|Liverpool|Leicester|85.75|4.01|10.24
8|Norwich|Aston Villa|40.22|30.54|29.24
8|Watford|Sheffield Utd|69.78|12.0|18.23
8|West Ham|Crystal Palace|33.99|45.25|20.76
9|Sheffield Utd|Arsenal|15.66|65.8|18.54
9|Man Utd|Liverpool|6.65|79.11|14.24
9|Everton|West Ham|49.68|22.6|27.73
9|Bournemouth|Norwich|79.97|6.7|13.32
9|Aston Villa|Brighton|20.94|51.23|27.83
9|Chelsea|Newcastle|57.17|13.25|29.57
9|Leicester|Burnley|45.14|27.94|26.92
9|Spurs|Watford|49.8|25.9|24.3
9|Wolves|Southampton|74.4|9.07|16.52
9|Crystal Palace|Man City|4.98|76.29|18.73
10|Newcastle|Wolves|28.98|40.48|30.54
10|Arsenal|Crystal Palace|59.54|20.87|19.59
10|Liverpool|Spurs|80.8|5.98|13.22
10|Norwich|Man Utd|8.54|77.74|13.71
10|Man City|Aston Villa|98.17|0.32|1.51
10|Brighton|Everton|21.81|50.99|27.2
10|Watford|Bournemouth|50.52|29.83|19.65
10|West Ham|Sheffield Utd|80.57|6.95|12.48
10|Burnley|Chelsea|31.88|44.25|23.86
10|Southampton|Leicester|23.12|56.21|20.66
11|Everton|Spurs|30.93|43.32|25.75
11|Crystal Palace|Leicester|22.61|50.17|27.23
11|Bournemouth|Man Utd|40.71|37.66|21.63
11|Arsenal|Wolves|57.79|17.83|24.38
11|Aston Villa|Liverpool|2.12|88.21|9.68
11|Brighton|Norwich|58.32|16.71|24.97
11|Man City|Southampton|95.83|0.92|3.25
11|Sheffield Utd|Burnley|18.14|59.95|21.91
11|West Ham|Newcastle|35.42|36.7|27.88
11|Watford|Chelsea|40.3|34.64|25.07
12|Man Utd|Brighton|48.47|28.05|23.48
12|Wolves|Aston Villa|83.76|4.56|11.68
12|Liverpool|Man City|42.17|23.96|33.86
12|Chelsea|Crystal Palace|64.89|14.37|20.74
12|Burnley|West Ham|33.08|40.92|26.0
12|Newcastle|Bournemouth|51.51|27.23|21.26
12|Southampton|Everton|23.96|53.34|22.71
12|Spurs|Sheffield Utd|83.29|4.59|12.12
12|Leicester|Arsenal|44.0|31.03|24.97
12|Norwich|Watford|9.59|74.18|16.24
13|Aston Villa|Newcastle|11.38|64.17|24.45
13|Sheffield Utd|Man Utd|9.18|76.68|14.14
13|West Ham|Spurs|30.48|47.3|22.22
13|Bournemouth|Wolves|38.12|33.65|28.23
13|Arsenal|Southampton|85.95|4.43|9.62
13|Brighton|Leicester|21.3|54.01|24.69
13|Crystal Palace|Liverpool|6.09|72.32|21.59
13|Everton|Norwich|76.69|7.51|15.81
13|Watford|Burnley|42.56|34.51|22.93
13|Man City|Chelsea|89.21|2.94|7.85
14|Norwich|Arsenal|14.69|67.14|18.17
14|Wolves|Sheffield Utd|83.09|4.77|12.13
14|Leicester|Everton|31.36|37.6|31.04
14|Man Utd|Aston Villa|76.83|9.35|13.82
14|Newcastle|Man City|6.5|74.89|18.61
14|Burnley|Crystal Palace|15.9|67.81|16.29
14|Chelsea|West Ham|72.93|7.29|19.78
14|Liverpool|Brighton|91.01|1.8|7.19
14|Spurs|Bournemouth|73.2|11.78|15.02
14|Southampton|Watford|23.43|56.72|19.84
15|Arsenal|Brighton|74.34|8.9|16.76
15|Sheffield Utd|Newcastle|11.31|64.13|24.56
15|Chelsea|Aston Villa|91.77|1.54|6.68
15|Leicester|Watford|32.46|40.06|27.48
15|Man Utd|Spurs|23.13|57.36|19.51
15|Southampton|Norwich|67.26|14.21|18.52
15|Wolves|West Ham|58.45|16.48|25.06
15|Liverpool|Everton|83.51|4.35|12.14
15|Crystal Palace|Bournemouth|40.53|34.93|24.54
15|Burnley|Man City|3.04|87.72|9.24
16|West Ham|Arsenal|53.84|27.17|18.99
16|Aston Villa|Leicester|10.41|71.97|17.62
16|Newcastle|Southampton|56.78|19.34|23.88
16|Norwich|Sheffield Utd|39.48|31.05|29.46
16|Brighton|Wolves|21.64|48.6|29.76
16|Everton|Chelsea|50.04|24.19|25.78
16|Bournemouth|Liverpool|11.04|66.73|22.23
16|Spurs|Burnley|63.88|15.78|20.34
16|Watford|Crystal Palace|23.52|56.47|20.01
16|Man City|Man Utd|86.34|4.9|8.76
17|Crystal Palace|Brighton|34.7|32.21|33.1
17|Man Utd|Everton|31.06|46.07|22.87
17|Wolves|Spurs|40.01|33.84|26.15
17|Arsenal|Man City|19.52|52.69|27.79
17|Liverpool|Watford|87.46|3.6|8.94
17|Burnley|Newcastle|20.24|54.45|25.31
17|Chelsea|Bournemouth|87.09|4.07|8.84
17|Leicester|Norwich|68.12|10.3|21.58
17|Sheffield Utd|Aston Villa|41.82|29.36|28.82
17|Southampton|West Ham|36.8|37.38|25.82
18|Watford|Man Utd|27.5|52.23|20.27
18|Spurs|Chelsea|59.99|16.73|23.27
18|Everton|Arsenal|52.22|26.08|21.7
18|Bournemouth|Burnley|55.88|22.96|21.16
18|Aston Villa|Southampton|29.6|43.16|27.24
18|Brighton|Sheffield Utd|57.87|16.95|25.18
18|Newcastle|Crystal Palace|25.88|51.18|22.94
18|Norwich|Wolves|11.04|66.14|22.82
18|Man City|Leicester|82.48|5.89|11.62
19|Wolves|Man City|13.25|60.43|26.32
19|Spurs|Brighton|61.6|14.41|23.99
19|Bournemouth|Arsenal|54.65|25.42|19.93
19|Aston Villa|Norwich|41.81|29.43|28.76
19|Chelsea|Southampton|86.1|3.35|10.55
19|Crystal Palace|West Ham|32.55|34.13|33.32
19|Everton|Burnley|53.28|23.57|23.15
19|Sheffield Utd|Watford|10.24|73.11|16.65
19|Man Utd|Newcastle|29.21|44.88|25.91
19|Leicester|Liverpool|9.33|64.38|26.29
20|Brighton|Bournemouth|39.36|37.6|23.04
20|Newcastle|Everton|29.63|42.2|28.17
20|Southampton|Crystal Palace|18.81|63.84|17.35
20|Watford|Aston Villa|70.64|11.59|17.78
20|Norwich|Spurs|6.81|79.09|14.1
20|West Ham|Leicester|38.32|38.89|22.78
20|Burnley|Man Utd|19.01|63.96|17.03
20|Arsenal|Chelsea|73.17|10.33|16.5
20|Liverpool|Wolves|80.55|4.82|14.63
20|Man City|Sheffield Utd|98.01|0.35|1.65
21|Brighton|Chelsea|31.48|40.07|28.45
21|Burnley|Aston Villa|63.43|16.5|20.07
21|Newcastle|Leicester|29.5|44.56|25.94
21|Southampton|Spurs|17.1|64.58|18.32
21|Watford|Wolves|27.85|44.97|27.18
21|Man City|Everton|80.3|6.26|13.43
21|Norwich|Crystal Palace|7.14|79.99|12.87
21|West Ham|Bournemouth|64.81|19.23|15.96
21|Arsenal|Man Utd|65.3|17.27|17.43
21|Liverpool|Sheffield Utd|98.38|0.23|1.38
22|Sheffield Utd|West Ham|19.1|53.5|27.4
22|Crystal Palace|Arsenal|32.38|42.14|25.48
22|Chelsea|Burnley|79.1|6.5|14.4
22|Everton|Brighton|52.34|20.81|26.86
22|Leicester|Southampton|57.15|17.39|25.46
22|Man Utd|Norwich|76.44|9.53|14.03
22|Wolves|Newcastle|42.13|26.25|31.62
22|Spurs|Liverpool|16.01|54.32|29.67
22|Bournemouth|Watford|40.6|36.11|23.29
22|Aston Villa|Man City|1.56|90.84|7.59
23|Watford|Spurs|21.26|57.5|21.23
23|Arsenal|Sheffield Utd|91.96|2.02|6.03
23|Brighton|Aston Villa|58.71|16.53|24.76
23|Man City|Crystal Palace|82.14|6.68|11.19
23|Norwich|Bournemouth|19.99|60.24|19.78
23|Southampton|Wolves|24.01|51.23|24.76
23|West Ham|Everton|38.31|37.17|24.51
23|Newcastle|Chelsea|41.05|31.41|27.54
23|Burnley|Leicester|20.0|60.14|19.86
23|Liverpool|Man Utd|89.47|3.19|7.34
24|Bournemouth|Brighton|55.17|20.4|24.44
24|Aston Villa|Watford|10.31|73.11|16.58
24|Crystal Palace|Southampton|46.08|24.98|28.94
24|Everton|Newcastle|34.33|33.47|32.2
24|Sheffield Utd|Man City|1.56|90.76|7.67
24|Chelsea|Arsenal|80.17|6.77|13.05
24|Leicester|West Ham|42.04|25.9|32.06
24|Spurs|Norwich|83.64|4.48|11.88
24|Man Utd|Burnley|47.28|32.24|20.48
24|Wolves|Liverpool|15.43|55.9|28.67
25|West Ham|Liverpool|9.87|70.99|19.14
25|Leicester|Chelsea|42.32|27.98|29.7
25|Bournemouth|Aston Villa|80.32|6.57|13.1
25|Crystal Palace|Sheffield Utd|57.19|15.97|26.84
25|Liverpool|Southampton|96.67|0.61|2.72
25|Newcastle|Norwich|68.69|11.24|20.06
25|Watford|Everton|28.17|46.77|25.06
25|West Ham|Brighton|55.25|21.66|23.09
25|Man Utd|Wolves|30.75|44.53|24.72
25|Burnley|Arsenal|30.37|49.82|19.81
25|Spurs|Man City|13.82|58.82|27.37
26|Everton|Crystal Palace|34.42|41.71|23.87
26|Brighton|Watford|21.63|54.73|23.64
26|Sheffield Utd|Bournemouth|21.24|58.71|20.05
26|Man City|West Ham|87.69|3.11|9.21
26|Wolves|Leicester|47.46|27.23|25.32
26|Southampton|Burnley|37.52|40.56|21.92
26|Norwich|Liverpool|1.97|88.57|9.46
26|Aston Villa|Spurs|7.33|78.23|14.44
26|Arsenal|Newcastle|54.76|18.74|26.5
26|Chelsea|Man Utd|70.07|11.85|18.08
27|Chelsea|Spurs|59.03|16.45|24.52
27|Burnley|Bournemouth|39.8|40.55|19.64
27|Crystal Palace|Newcastle|21.3|44.41|34.29
27|Sheffield Utd|Brighton|20.78|51.27|27.95
27|Southampton|Aston Villa|67.68|14.01|18.32
27|Leicester|Man City|7.85|68.65|23.5
27|Man Utd|Watford|31.1|48.58|20.32
27|Wolves|Norwich|83.45|4.66|11.9
27|Arsenal|Everton|60.24|17.65|22.11
27|Liverpool|West Ham|89.63|2.15|8.22
28|Norwich|Leicester|9.7|73.01|17.29
28|Brighton|Crystal Palace|17.88|61.23|20.88
28|Bournemouth|Chelsea|52.59|23.79|23.61
28|Aston Villa|Sheffield Utd|41.39|29.74|28.87
28|Newcastle|Burnley|43.57|31.35|25.08
28|West Ham|Southampton|69.64|13.44|16.92
28|Watford|Liverpool|6.59|76.88|16.53
28|Everton|Man Utd|39.17|37.63|23.21
28|Man City|Arsenal|92.99|2.16|4.86
28|Spurs|Wolves|45.28|24.76|29.95
29|Arsenal|West Ham|71.84|10.07|18.08
29|Burnley|Spurs|14.56|68.21|17.24
29|Chelsea|Everton|63.49|12.44|24.06
29|Crystal Palace|Watford|23.05|50.88|26.07
29|Leicester|Aston Villa|68.51|10.16|21.33
29|Liverpool|Bournemouth|97.5|0.59|1.91
29|Man Utd|Man City|5.13|83.05|11.82
29|Sheffield Utd|Norwich|41.48|29.57|28.96
29|Southampton|Newcastle|22.91|51.16|25.94
29|Wolves|Brighton|61.11|14.98|23.91
30|Bournemouth|Crystal Palace|35.64|42.09|22.26
30|Aston Villa|Chelsea|17.99|57.86|24.15
30|Brighton|Arsenal|30.99|45.4|23.61
30|Everton|Liverpool|11.09|64.18|24.73
30|Man City|Burnley|92.15|2.22|5.63
30|Newcastle|Sheffield Utd|68.24|11.45|20.31
30|Norwich|Southampton|28.01|44.59|27.4
30|Spurs|Man Utd|50.82|26.68|22.49
30|Watford|Leicester|27.68|49.3|23.02
30|West Ham|Wolves|37.4|36.16|26.45
31|Burnley|Watford|20.18|60.79|19.03
31|Chelsea|Man City|24.9|38.39|36.71
31|Leicester|Brighton|44.44|24.16|31.4
31|Liverpool|Crystal Palace|85.92|4.44|9.65
31|Man Utd|Sheffield Utd|75.99|9.75|14.26
31|Newcastle|Aston Villa|69.08|11.09|19.83
31|Norwich|Everton|10.59|69.34|20.08
31|Southampton|Arsenal|34.74|45.23|20.04
31|Spurs|West Ham|58.97|15.86|25.17
31|Wolves|Bournemouth|72.55|12.34|15.11
32|Bournemouth|Newcastle|36.06|34.11|29.83
32|Arsenal|Norwich|92.19|1.95|5.86
32|Aston Villa|Wolves|11.76|65.19|23.06
32|Brighton|Man Utd|20.86|57.81|21.33
32|Crystal Palace|Burnley|34.14|37.86|27.99
32|Everton|Leicester|37.9|35.99|26.11
32|Man City|Liverpool|40.0|27.86|32.14
32|Sheffield Utd|Spurs|7.29|78.2|14.51
32|Watford|Southampton|57.25|20.89|21.86
32|West Ham|Chelsea|52.27|25.36|22.37
33|Burnley|Sheffield Utd|62.52|17.01|20.47
33|Chelsea|Watford|67.82|12.01|20.18
33|Leicester|Crystal Palace|28.5|45.8|25.7
33|Liverpool|Aston Villa|98.52|0.21|1.27
33|Man Utd|Bournemouth|56.11|26.72|17.17
33|Newcastle|West Ham|41.2|29.1|29.71
33|Norwich|Brighton|19.77|52.43|27.8
33|Southampton|Man City|3.68|86.01|10.31
33|Spurs|Everton|47.2|25.25|27.55
33|Wolves|Arsenal|62.92|17.99|19.09
34|Bournemouth|Spurs|31.99|44.04|23.97
34|Arsenal|Leicester|61.84|17.86|20.31
34|Aston Villa|Man Utd|9.24|76.67|14.09
34|Brighton|Liverpool|5.32|76.78|17.9
34|Crystal Palace|Chelsea|32.26|37.1|30.63
34|Everton|Southampton|65.92|13.74|20.34
34|Man City|Newcastle|74.18|7.62|18.2
34|Sheffield Utd|Wolves|11.68|65.16|23.16
34|Watford|Norwich|70.24|11.76|17.99
34|West Ham|Burnley|55.44|24.45|20.11
35|Bournemouth|Leicester|39.51|36.22|24.27
35|Aston Villa|Crystal Palace|7.71|79.05|13.24
35|Brighton|Man City|4.24|80.57|15.19
35|Liverpool|Burnley|93.84|1.46|4.7
35|Man Utd|Southampton|63.22|18.34|18.44
35|Norwich|West Ham|18.15|54.63|27.22
35|Sheffield Utd|Chelsea|17.85|57.9|24.25
35|Spurs|Arsenal|63.71|17.22|19.07
35|Watford|Newcastle|26.46|45.01|28.53
35|Wolves|Everton|46.47|26.23|27.3
36|Arsenal|Liverpool|22.37|48.07|29.56
36|Burnley|Wolves|21.15|54.71|24.14
36|Chelsea|Norwich|91.56|1.59|6.86
36|Crystal Palace|Man Utd|22.51|53.84|23.65
36|Everton|Aston Villa|77.05|7.38|15.58
36|Leicester|Sheffield Utd|67.69|10.48|21.83
36|Man City|Bournemouth|96.55|0.97|2.48
36|Newcastle|Spurs|23.37|52.11|24.52
36|Southampton|Brighton|39.51|34.88|25.61
36|West Ham|Watford|39.32|38.79|21.9
37|Bournemouth|Southampton|69.15|12.89|17.97
37|Aston Villa|Arsenal|15.78|65.74|18.48
37|Brighton|Newcastle|20.58|48.12|31.29
37|Liverpool|Chelsea|91.18|1.99|6.83
37|Man Utd|West Ham|45.47|30.5|24.03
37|Norwich|Burnley|17.13|61.26|21.62
37|Sheffield Utd|Everton|11.24|68.31|20.45
37|Spurs|Leicester|48.29|26.19|25.52
37|Watford|Man City|5.2|80.84|13.96
37|Wolves|Crystal Palace|44.53|31.71|23.76
38|Arsenal|Watford|63.69|17.25|19.06
38|Burnley|Brighton|35.65|38.39|25.96
38|Chelsea|Wolves|60.45|12.62|26.93
38|Crystal Palace|Spurs|17.73|57.18|25.08
38|Everton|Bournemouth|62.26|19.18|18.56
38|Leicester|Man Utd|32.49|42.19|25.32
38|Man City|Norwich|98.09|0.33|1.58
38|Newcastle|Liverpool|7.94|70.71|21.35
38|Southampton|Sheffield Utd|66.78|14.48|18.74
38|West Ham|Aston Villa|81.32|6.64|12.04
