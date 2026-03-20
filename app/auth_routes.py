from flask import Blueprint, redirect, url_for, session, request
from app.oauth import oauth
from app.services import get_or_create_oauth_user
import datetime
import requests
import re

auth_bp = Blueprint('auth', __name__)


# ---- Google ----
@auth_bp.route('/auth/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
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
        print(f"Google OAuth error: {e}")
        return redirect(url_for('main.login'))


# ---- Steam ----
STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'


@auth_bp.route('/auth/steam')
def steam_login():
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
    try:
        params = request.args.to_dict()
        params['openid.mode'] = 'check_authentication'

        response = requests.post(STEAM_OPENID_URL, data=params)
        print(f"DEBUG Steam validation response: {response.text}")

        if 'is_valid:true' not in response.text:
            print("Steam OpenID validation failed")
            return redirect(url_for('main.login'))

        claimed_id = request.args.get('openid.claimed_id', '')
        print(f"DEBUG claimed_id: {claimed_id}")

        steam_id = re.search(r'(\d+)$', claimed_id)
        print(f"DEBUG steam_id: {steam_id}")

        if not steam_id:
            return redirect(url_for('main.login'))

        steam_id = steam_id.group(1)
        print(f"DEBUG steam_id extracted: {steam_id}")

        from app.config import Config
        api_url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
            f"?key={Config.STEAM_API_KEY}&steamids={steam_id}"
        )
        steam_response = requests.get(api_url)
        print(f"DEBUG STEAM_API_KEY: {Config.STEAM_API_KEY}")
        print(f"DEBUG API URL: {api_url}")
        print(f"DEBUG steam_response status: {steam_response.status_code}")
        print(f"DEBUG steam_response text: {steam_response.text}")
        steam_data = steam_response.json()
        print(f"DEBUG steam_data: {steam_data}")

        players = steam_data.get('response', {}).get('players', [])
        if not players:
            print("DEBUG: No players found")
            return redirect(url_for('main.login'))

        player = players[0]
        username = player.get('personaname', f'steam_{steam_id}')
        print(f"DEBUG username: {username}")

        user = get_or_create_oauth_user(
            provider='steam',
            provider_account_id=steam_id,
            email=None,
            username=username,
            access_token=steam_id
        )

        session['user_id'] = user.user_id
        session['username'] = user.username
        session['email'] = user.email

        return redirect(url_for('main.home'))

    except Exception as e:
        print(f"Steam OAuth error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('main.login'))