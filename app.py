from datetime import datetime, timedelta

from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Games, Odds, User, Pick
from forms import UserForm, PickForm, ConfirmForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///odds_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "basewinner100"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)




@app.route('/')
def homepage():
    """ Show index page """
    return render_template('home.html')




@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        coins = 500
        new_user = User.register(username, password, coins)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/mlb')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session['user_id'] = user.id
            session['user_name'] = user.username
            return redirect('/mlb')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/login')



@app.route('/mlb')
def get_all():
    last_item = Odds.query.order_by(Odds.pull_id.desc()).first()
    last = last_item.pull_id
    now = datetime.now()
    datetime_new = now + timedelta(hours = 7)
    matches = Odds.query.filter(Odds.pull_id == last)
    
    return render_template('mlb.html', matches = matches, now = datetime_new)

@app.route('/mlb_selection/<odds_id>',  methods=['GET', 'POST'])
def show_pick_form(odds_id):
    ##Check if user is logged in

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect(f'/login?return=/mlb_selection/{odds_id}')

    form= PickForm()

    if form.validate_on_submit():
      
        session['risk_amount'] = form.risk_amount.data
               
        return redirect('/confirm_pick')

    ###This if/then code already existed that Scott wrote 

    odds = Odds.query.get(odds_id)
    side = request.args.get('side')


    if side == 'away':
        moneyline = odds.moneyline_away
        team = odds.game.team_away_name
        opponent = odds.game.team_home_name
        game_id = odds.game.game_id
        game_date = odds.game.game_date
        rotation_number = odds.game.rotation_away
    else:
        moneyline = odds.moneyline_home
        team = odds.game.team_home_name
        opponent = odds.game.team_away_name
        game_id = odds.game.game_id
        game_date = odds.game.game_date
        rotation_number = odds.game.rotation_home

    session['game_date'] = game_date
    session['rotation_number'] = rotation_number
    session['team'] = team
    session['moneyline'] = moneyline
    session['opponent'] = opponent
    session['game_id'] = game_id
    session['side'] = side
    

    return render_template('mlb_selection.html', game_date = game_date, rotation_number = rotation_number, team = team, moneyline = moneyline, opponent = opponent, form=form)

@app.route('/confirm_pick', methods=['GET', 'POST'])
def show_confirm_form():

    ##Check if user is logged in

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect(f'/login?return=/home')

    form =ConfirmForm()

    game_date = session['game_date']
    rotation_number = session['rotation_number']
    moneyline = session['moneyline']
    team = session['team']
    opponent = session['opponent']
    risk_amount = session['risk_amount']
    game_id = session['game_id']
    side = session['side']
    user_id = session['user_id']

    if moneyline<-99:
        win_amount = round( risk_amount * 100 / abs(moneyline),2)
        pick_odds_pct = round(abs( moneyline) / (abs(moneyline) + 100),3)
        print(pick_odds_pct)
    else:
        win_amount = round((risk_amount * moneyline * .01),2)
        pick_odds_pct = round( 100 / (abs(moneyline) + 100),3)
        print(pick_odds_pct) 



    if form.validate_on_submit():

        new_pick = Pick( user_id=user_id, game_id=game_id,risk_amount = risk_amount, to_win_amount = win_amount, pick = team, side = side, pick_odds_amer = moneyline, pick_odds_pct = pick_odds_pct, pick_status = 'STATUS_SCHEDULED')
        db.session.add(new_pick)
        db.session.commit()
        flash('Pick Created!', 'success')
        return redirect ('/')

    return render_template("confirm_pick.html", game_date = game_date, rotation_number = rotation_number, team = team, moneyline = moneyline, opponent = opponent, risk_amount = risk_amount, win_amount = win_amount, form=form)



@app.route('/show_picks')
def show_user_picks():

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect(f'/login?return=/home')

    user_id = session['user_id']
    user_name = session['user_name']
    user_picks = Pick.query.filter_by(user_id = user_id).join(Games).order_by(Games.game_date.desc())
    user = User.query.get(user_id)
    
    return render_template('show_picks.html', user_picks = user_picks, user_name = user_name, user=user)