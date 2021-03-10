from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)
    

# MODELS GO BELOW!


class Games(db.Model):
   
    __tablename__ = 'games'
   
    game_id = db.Column(db.String, primary_key=True)
    game_date = db.Column(db.DateTime, nullable=False)
    team_away_name = db.Column(db.String, nullable=False)
    team_home_name = db.Column(db.String, nullable=False)
    rotation_away = db.Column(db.Integer, nullable=True)
    rotation_home = db.Column(db.Integer, nullable=True)
    event_status = db.Column(db.String, nullable=True)
    score_away = db.Column(db.Integer, nullable=True)
    score_home = db.Column(db.Integer, nullable=True)
    winner_away = db.Column(db.Integer, nullable=True)
    winner_home = db.Column(db.Integer, nullable=True)
    
   
    odds = db.relationship('Odds', back_populates='game')
    pick = db.relationship('Pick', back_populates='game_pick')


class Odds(db.Model):
   
    __tablename__ = 'odds'
   
    odds_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pull_id = db.Column(db.Integer, nullable=False)
    moneyline_id = db.Column(db.Integer, nullable=True)
    moneyline_away = db.Column(db.Integer, nullable=True)
    moneyline_home = db.Column(db.Integer, nullable=True)
    game_id = db.Column(db.String, db.ForeignKey('games.game_id'))

    game = db.relationship('Games', uselist=False, back_populates='odds')




class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False,  unique=True)

    password = db.Column(db.Text, nullable=False)

    coin_balance = db.Column(db.Float, nullable=True)

    picks = db.relationship('Pick', back_populates = 'user')


    @classmethod
    def register(cls, username, pwd, coins):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        #turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        #return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, coin_balance = coins)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            #return user instance
            return u
        else:
            return False

class Pick(db.Model):
    """User."""

    __tablename__ = "picks"

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game_id = db.Column(db.Text, db.ForeignKey('games.game_id'))
    risk_amount = db.Column(db.Float, nullable=True)
    to_win_amount = db.Column(db.Float, nullable=True)
    pick = db.Column(db.Text, nullable=True)
    side = db.Column(db.Text, nullable=True)
    pick_odds_amer = db.Column(db.Float, nullable=True)
    pick_odds_pct = db.Column(db.Float, nullable=True)
    pick_status = db.Column(db.Text, nullable= True)
    pick_win = db.Column(db.Float, nullable=True)
    pick_loss = db.Column(db.Float, nullable=True)
    pick_push = db.Column(db.Float, nullable=True)
    coin_return = db.Column(db.Float, nullable=True)

    user = db.relationship('User', uselist=False, back_populates='picks')
    game_pick = db.relationship('Games', uselist=False, back_populates='pick')
   


