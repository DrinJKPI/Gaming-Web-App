from flask import Blueprint, redirect, url_for, session, request
from app.oauth import oauth
from app.services import get_or_create_oauth_user
import datetime

auth_bp = Blueprint('auth', __name__)


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

        # Get or create user
        user = get_or_create_oauth_user(
            provider='google',
            provider_account_id=user_info['sub'],
            email=user_info.get('email'),
            username=user_info.get('name'),
            access_token=token.get('access_token')
        )

        # Set session
        session['user_id'] = user.user_id
        session['username'] = user.username
        session['email'] = user.email

        return redirect(url_for('main.home'))

    except Exception as e:
        print(f"Google OAuth error: {e}")
        return redirect(url_for('main.login'))