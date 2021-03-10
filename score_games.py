from datetime import datetime, timedelta

from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Games, Odds, User, Pick

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///odds_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "basewinner100"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Connect to the database
connect_db(app)

##Score any outstanding picks
picks = Pick.query.filter_by(pick_status = 'STATUS_SCHEDULED')
scored_count = 0

for pick in picks:
    if pick.game_pick.event_status == 'STATUS_FINAL':
        if pick.side == 'away' and pick.game_pick.winner_away == 1:
            winner = True    
        elif pick.side == 'home' and pick.game_pick.winner_home == 1:
            winner = True
        else:
            winner = False

        if winner == True:
            pick.coin_return = pick.to_win_amount
            pick.pick_win = 1
            pick.pick_loss = 0
        else:
            pick.coin_return = pick.risk_amount * -1
            pick.pick_loss = 1
            pick.pick_win = 0

        pick.pick_status = 'Scored'
        scored_count +=1

        db.session.add(pick)
        db.session.commit()

##update user coin balances
users = User.query.all()

for user in users:
    running_balance = 0
    user_picks = Pick.query.filter_by(user_id = user.id)

    for pick in user_picks:
        if pick.pick_status == 'Scored':
          running_balance += pick.coin_return

    ##initial deposit is always 500 coins
    initial_balance = 500
    user.coin_balance = initial_balance + running_balance

    db.session.add(user)
    db.session.commit()

print(f'picks scored: {scored_count}')    