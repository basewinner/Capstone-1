# Capstone-1
# MLB ODDS And Bet Tracker APP
## Overview
* Allows a user to see MLB moneyline odds, make game selections and track the results of their selections.
* The targeted user is anyone who enjoys watching the MLB and either wants to make selections for fun or to see if they could win at a sports book.
* The data will come from TheRundown API. I am pulling in Full Game Moneyline Odds. 
## Schema
* Table for users containing username, password, e-mail, coins
* Tables for odds and game results. Included will be game_id, team_away_name, team_home_name, rotation_away, rotation_home, game_date, event_status, score_away, score_home, winner_away, winner_home, odds_id, pull_id_money_id,moneyline_home, moneyline_away
* Table for user picks and results. Fields will include user_id, game_id, risk_amount, to_win_amount, pick, side pick_odds_american, pick_win, pick_loss,pick_push, coin_return
## Potential API issues
* calls are limited to 50 per day. To start, will keep calls to 1 per hour and update odds database. App will use odds pulled from odds database.
## User Flow
* Users starts at homepage which shows login/registration options
* Once logged in, User can go to the days game selection page or to their selection tracker page.
* Selection page will have all games for that day.
* If user chooses a game, they will be directed to a selection page where they can input the amount of coins they want to risk.
* When they submit the coins risked , they will be sent to a page that that will shows coins risked to return number and a confirmation button.
* When they confirm, the will be flashed a your selection has been succesfully accepted message and returned to their home page.
## Data
* TheRundown API has odds for American sports.
* All of the information for the odds and game results will originate with TheRundown API.