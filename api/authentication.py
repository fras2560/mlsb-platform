'''
@author: Dallas Fraser
@author: 2015-09-29
@organization: MLSB API
@summary: Holds the authentication functions
'''
from functools import wraps
from flask import request, Response
from flask import session
import os
try:
    # running local
    local = True
    from api.credentials import ADMIN, PASSWORD
except:
    ADMIN = os.environ['ADMIN']
    PASSWORD = os.environ['PASSWORD']
    

from api.model import Team, Player

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == ADMIN and password == PASSWORD

def check_captain(player, password, game):
    player = Player.query.filter_by(name=player).first()
    game = Game.query.get(game)
    away_team = Team.query.get(game.away_team_id)
    home_team = Team.query.get(game.home_team_id)
    return (home_team.player_id == player.id or away_team.player_id)\
             and player.check_password(password)

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        elif 'admin' in session and 'password' in session:
            # check if user signed in already
            logged = check_auth(session['admin'], session['password'])
            if not logged:
                return authenticate()
        return f(*args, **kwargs)
    return decorated

def requires_captain(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth  = request.authorization
        if not auth or not check_captain(auth.name, auth.password, auth.game):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
