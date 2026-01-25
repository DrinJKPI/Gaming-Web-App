"""
Unit Tests for Gaming Webstore Application
Tests user authentication, library operations, game retrieval, and API endpoints
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User, Game, UserLibrary
from app.services import create_user, get_user_by_email, hash_password, check_password
from app.game_metadata_service import get_all_games_from_mongodb, get_game_by_id_from_mongodb


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    yield app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create an application context"""
    with app.app_context():
        yield


# ========== USER AUTHENTICATION TESTS ==========

def test_password_hashing():
    """Test that password hashing works correctly"""
    password = "testpassword123"
    hashed = hash_password(password)

    assert hashed is not None
    assert isinstance(hashed, str)
    assert check_password(password, hashed) is True
    assert check_password("wrongpassword", hashed) is False


def test_user_registration(client):
    """Test user registration endpoint"""
    import random
    random_num = random.randint(1000, 9999)

    response = client.post('/register', data={
        'username': f'testuser{random_num}',
        'email': f'test{random_num}@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=False)

    # Should redirect to log in after successful registration
    assert response.status_code in [200, 302]


def test_user_login(client, app_context):
    """Test user login endpoint"""
    import random
    random_num = random.randint(1000, 9999)

    # First create a user
    create_user(f'logintest{random_num}', f'login{random_num}@test.com', 'testpass123')

    # Try to log in
    response = client.post('/login', data={
        'email': f'login{random_num}@test.com',
        'password': 'testpass123'
    }, follow_redirects=False)

    assert response.status_code in [200, 302]


def test_login_with_wrong_password(client, app_context):
    """Test login fails with wrong password"""
    import random
    random_num = random.randint(1000, 9999)

    create_user(f'wrongpasstest{random_num}', f'wrong{random_num}@test.com', 'correctpass')

    response = client.post('/login', data={
        'email': f'wrong{random_num}@test.com',
        'password': 'wrongpass'
    })

    assert response.status_code == 401


# ========== GAME RETRIEVAL TESTS ==========

def test_get_all_games(app_context):
    """Test retrieving all games from MongoDB"""
    games = get_all_games_from_mongodb()

    assert games is not None
    assert isinstance(games, list)
    assert len(games) > 0


def test_get_game_by_id(app_context):
    """Test retrieving a single game by ID"""
    # Get first game from all games
    games = get_all_games_from_mongodb()
    if games:
        first_game_id = games[0].get('mysql_game_id')
        game = get_game_by_id_from_mongodb(first_game_id)

        assert game is not None
        assert game.get('title') is not None
        assert game.get('platform') is not None


def test_game_has_required_fields(app_context):
    """Test that games have all required fields"""
    games = get_all_games_from_mongodb()

    if games:
        game = games[0]
        assert 'title' in game
        assert 'platform' in game
        assert 'price' in game
        assert 'mysql_game_id' in game


# ========== API ENDPOINT TESTS ==========

def test_api_get_all_games(client):
    """Test API endpoint for getting all games"""
    response = client.get('/api/games')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'games' in data
    assert isinstance(data['games'], list)


def test_api_get_single_game(client, app_context):
    """Test API endpoint for getting a single game"""
    games = get_all_games_from_mongodb()
    if games:
        game_id = games[0].get('mysql_game_id')
        response = client.get(f'/api/games/{game_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'game' in data


def test_api_search_games(client):
    """Test API endpoint for searching games"""
    response = client.get('/api/games/search?q=hollow')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'games' in data
    assert 'query' in data


def test_api_search_without_query(client):
    """Test API search fails without query parameter"""
    response = client.get('/api/games/search')

    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_api_get_user_library(client):
    """Test API endpoint for getting user library"""
    response = client.get('/api/library/2')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'games' in data
    assert 'total_games' in data


def test_api_get_recommendations(client):
    """Test API endpoint for getting recommendations"""
    response = client.get('/api/recommendations/2')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recommendations' in data


# ========== PAGE RENDERING TESTS ==========

def test_home_page(client):
    """Test home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200


def test_login_page(client):
    """Test login page loads successfully"""
    response = client.get('/login')
    assert response.status_code == 200


def test_register_page(client):
    """Test register page loads successfully"""
    response = client.get('/register')
    assert response.status_code == 200


def test_library_page_without_login(client):
    """Test library page accessible without login"""
    response = client.get('/library')
    assert response.status_code == 200


def test_recommendations_page(client):
    """Test recommendations page loads"""
    response = client.get('/recommendations')
    assert response.status_code == 200


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])