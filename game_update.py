import argparse
import arrow
import json
import pathlib
import requests

from flask import Flask
from models import db, connect_db, Games, Odds
from secrets import API_KEY
from sqlalchemy.exc import ProgrammingError

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
        
        self.event_status = event_data.get('score').get('event_status')
        self.score_away = event_data.get('score').get('score_away')
        self.score_home = event_data.get('score').get('score_home')
        self.winner_away = event_data.get('score').get('winner_away')
        self.winner_home = event_data.get('score').get('winner_home')
    
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

    game_list = []

    for event_dict in response_data.get('events'):
        event = Event(event_dict)
        game_list.append(event)

    return game_list




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

  
    events = fetch_odds(args.date)

    # This will store all the games we create
    games_added = []
  

    for event in events:
        game_id = event.rundown_id 

        try:
            game = Games.query.get(game_id)
        except Exception:
            print(f'game not found:{game_id}')
            continue
        
        if not game:
            print(f'game not found:{game_id}')
            continue

        game.event_status = event.event_status
        game.score_away = event.score_away
        game.score_home = event.score_home
        game.winner_away = event.winner_away
        game.winner_home = event.winner_home
        db.session.add(game)
        db.session.commit()