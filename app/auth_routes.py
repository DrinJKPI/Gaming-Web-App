from flask import Blueprint, redirect, url_for, session, request, flash
from app.oauth import oauth
from app.services import get_or_create_oauth_user
import requests
import re

auth_bp = Blueprint('auth', __name__)


# ---- Google OAuth ----

@auth_bp.route('/auth/google')
def google_login():
    """Redirect user to Google's OAuth login page"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback and create/login user"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            flash('Google login failed. Please try again.', 'error')
            return redirect(url_for('main.login'))

        user = get_or_create_oauth_user(
            provider='google',
            provider_account_id=user_info['sub'],
            email=user_info.get('email'),
            username=user_info.get('name'),
            access_token=token.get('access_token')
        )

        session['user_id'] = user.user_id
        session['username'] = user.username
        session['email'] = user.email

        return redirect(url_for('main.home'))

    except Exception as e:
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('main.login'))


# ---- Steam OAuth ----

STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'


@auth_bp.route('/auth/steam')
def steam_login():
    """Redirect user to Steam's OpenID login page"""
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': url_for('auth.steam_callback', _external=True),
        'openid.realm': request.host_url,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
    }

    auth_url = STEAM_OPENID_URL + '?' + '&'.join(f'{k}={v}' for k, v in params.items())
    return redirect(auth_url)


@auth_bp.route('/auth/steam/callback')
def steam_callback():
    """Handle Steam OpenID callback, validate response and create/login user"""
    try:
        # Validate the Steam OpenID response
        params = request.args.to_dict()
        params['openid.mode'] = 'check_authentication'

        response = requests.post(STEAM_OPENID_URL, data=params)

        if 'is_valid:true' not in response.text:
            flash('Steam login failed. Please try again.', 'error')
            return redirect(url_for('main.login'))

        # Extract Steam ID from the claimed identity URL
        claimed_id = request.args.get('openid.claimed_id', '')
        steam_id = re.search(r'(\d+)$', claimed_id)

        if not steam_id:
            flash('Could not retrieve Steam ID. Please try again.', 'error')
            return redirect(url_for('main.login'))

        steam_id = steam_id.group(1)

        # Fetch Steam user profile via Steam Web API
        from app.config import Config
        api_url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
            f"?key={Config.STEAM_API_KEY}&steamids={steam_id}"
        )
        steam_response = requests.get(api_url)
        steam_data = steam_response.json()

        players = steam_data.get('response', {}).get('players', [])
        if not players:
            flash('Could not retrieve Steam profile. Please try again.', 'error')
            return redirect(url_for('main.login'))

        player = players[0]
        username = player.get('personaname', f'steam_{steam_id}')

        # Get existing user or create a new one
        user = get_or_create_oauth_user(
            provider='steam',
            provider_account_id=steam_id,
            email=None,  # Steam does not return email addresses
            username=username,
            access_token=steam_id
        )

        session['user_id'] = user.user_id
        session['username'] = user.username
        session['email'] = user.email

        return redirect(url_for('main.home'))

    except Exception as e:
        flash('Steam login failed. Please try again.', 'error')
        return redirect(url_for('main.login'))