import argparse
import arrow
import json
import pathlib
import requests

from flask import Flask
from models import db, connect_db, Games, Odds
from secrets import API_KEY


class Event():
    def __init__(self, event_data):
        self.rundown_id = event_data.get('event_id')
        team_away_city = event_data.get('teams_normalized')[0].get('name')
        team_away_mascot = event_data.get('teams_normalized')[0].get('mascot')
       
        self.team_away_name = f'{team_away_city} {team_away_mascot}'
       
        team_home_city = event_data.get('teams_normalized')[1].get('name')
        team_home_mascot = event_data.get('teams_normalized')[1].get('mascot')
       
        self.team_home_name = f'{team_home_city} {team_home_mascot}'
        
        self.rotation_away = event_data.get('rotation_number_away')
        self.rotation_home = event_data.get('rotation_number_home')
        self.datetime = event_data.get('event_date')
        self.datetime_local = arrow.get(self.datetime).to('America/Phoenix').format('MM/DD/YYYY h:mma')
        self.rotation_away = event_data.get('rotation_number_away')
        self.rotation_away = event_data.get('rotation_number_away')
        
        self.event_status = event_data.get('score').get('event_status')
        self.score_away = event_data.get('score').get('score_away')
        self.score_home = event_data.get('score').get('score_home')
        self.winner_away = event_data.get('score').get('winner_away')
        self.winner_home = event_data.get('score').get('winner_home')

      
       
        lines = event_data.get('lines', {})
       
        self.moneyline_id = lines.get('1', {}).get('moneyline', {}).get('line_id')
        self.moneyline_odds_away = lines.get('1', {}).get('moneyline', {}).get('moneyline_away')
        self.moneyline_odds_home = lines.get('1', {}).get('moneyline', {}).get('moneyline_home')
        self.spread_odds_away_points = lines.get('1', {}).get('spread', {}).get('point_spread_away')
        self.spread_odds_away_moneyline = lines.get('1', {}).get('spread', {}).get('point_spread_away_money')
        self.spread_odds_home_points = lines.get('1', {}).get('spread', {}).get('point_spread_home')
        self.spread_odds_home_moneyline = lines.get('1', {}).get('spread', {}).get('point_spread_home_money')
        self.total_points = lines.get('1', {}).get('total', {}).get('total_over')
        self.total_over_moneyline = lines.get('1', {}).get('total', {}).get('total_over_money')
        self.total_under_moneyline = lines.get('1', {}).get('total', {}).get('total_under_money')

    def __repr__(self):
        return f'{self.team_away_name} at {self.team_home_name}'




def fetch_odds(date):
    url = f"https://therundown-therundown-v1.p.rapidapi.com/sports/3/events/{date}"
    querystring = {"include":"scores","offset":"-7"}

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "therundown-therundown-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_data = response.json()

    # Every time we make the request, save it to a JSON file in case we want to use it later
    pathlib.Path(f'{date}.json').write_text(response.text)

    game_list = []

    for event_dict in response_data.get('events'):
        event = Event(event_dict)
        game_list.append(event)

    return game_list


def load_odds_from_json(filename):
    filepath = pathlib.Path(filename)

    if filepath.exists():
        data = json.loads(pathlib.Path(filename).read_text())
        events = [Event(event_dict) for event_dict in data['events']]
        return events
    else:
        return None


# If you just run $ python fetch_and_save_odds.py from a command line, this will execute:
if __name__ == '__main__':

    # Read command-line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('date')
    args = argparser.parse_args()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///odds_tracker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = "basewinner100"
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # Connect to the database
    connect_db(app)

    # Fetch the odds from rundown
    events = load_odds_from_json(f'{args.date}.json')

    # If the file didn't exist, go fetch it from rundown
    if events is None:
        events = fetch_odds(args.date)

    # This will store all the games we create
    games_added = []
    odds_added = []
    pull_id = arrow.now().timestamp



    for event in events:
        rot_away = event.rotation_away
        rot_home = event.rotation_home

        # We need to see if we have already stored this game
        result_count = Games.query.filter_by(game_id = event.rundown_id).count()

        if result_count > 0:
            print('Game already exists in DB. Skipping.')

        elif event.event_status == 'STATUS_CANCELED':
            print ('Game cancelled. Skipping')

        else:
            game = Games()
            game.game_date = event.datetime
            game.game_id = event.rundown_id
            game.team_away_name = event.team_away_name
            game.team_home_name = event.team_home_name
            game.rotation_away = event.rotation_away
            game.rotation_home = event.rotation_home
            game.event_status =  event.event_status
            game.score_away = event.score_away
            game.score_home = event.score_home
            game.winner_away = event.winner_away
            game.winner_home = event.winner_home

            games_added.append(game)
            db.session.add_all(games_added)
            db.session.commit()

        if event.event_status == 'STATUS_CANCELED':
            print ('Game cancelled. Skipping')
        
        else:
            odds = Odds()
            odds.pull_id = pull_id
            odds.game_id = event.rundown_id
            odds.moneyline_id = event.moneyline_id
            odds.moneyline_away = event.moneyline_odds_away
            odds.moneyline_home = event.moneyline_odds_home
            odds_added.append(odds)

            db.session.add_all(odds_added)
            db.session.commit()     
