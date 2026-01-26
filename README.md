# Gaming Webstore Application

A cloud-based gaming platform built with Flask, MySQL, MongoDB Atlas, and external APIs. Users can browse games, manage their library, and receive personalized recommendations.

## Features

- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Game Catalog**: 15 games (2023-2025) with rich metadata from RAWG API
- **Personal Library**: Add/remove games, track ownership
- **Recommendations Engine**: AI-powered suggestions based on user preferences
- **RESTful API**: External access to game and library data
- **Cloud Functions**: Automated recommendation generation and library synchronization

## Technologies Used

### Backend
- **Flask**: Web framework
- **Python 3.12**: Programming language
- **SQLAlchemy**: ORM for MySQL database

### Databases
- **MySQL**: Relational database for users, sessions, and library relationships
- **MongoDB Atlas**: NoSQL cloud database for game metadata

### External APIs
- **RAWG Video Games Database API**: Game metadata enrichment

### Testing
- **Pytest**: Unit testing framework (18 tests, 100% pass rate)

## Project Structure
```
Gaming-Webstore-App/
├── app/
│   ├── static/css/          # Styling
│   ├── templates/           # HTML templates
│   ├── __init__.py          # Flask app initialization
│   ├── api_routes.py        # REST API endpoints
│   ├── config.py            # Configuration
│   ├── models.py            # Database models
│   ├── routes.py            # Web routes
│   ├── services.py          # Business logic (MySQL)
│   ├── mongodb.py           # MongoDB connection
│   └── game_metadata_service.py  # MongoDB operations
├── cloud_functions/
│   ├── generate_recommendations.py  # Recommendation engine
│   └── sync_library.py      # Library synchronization
├── database/
│   └── schema.sql           # MySQL schema
├── tests/
│   └── test_basic.py        # Unit tests
├── .env                     # Environment variables
├── main.py                  # Application entry point
└── requirements.txt         # Python dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Set up environment variables in `.env`:
```
   MONGO_URI=your_mongodb_connection_string
   RAWG_API_KEY=your_rawg_api_key
```
4. Set up MySQL database:
```bash
   # Run schema.sql in your MySQL database
```
5. Run the application:
```bash
   python main.py
```

## API Endpoints

- `GET /api/games` - Get all games
- `GET /api/games/<id>` - Get single game details
- `GET /api/games/search?q=query` - Search games
- `GET /api/recommendations/<user_id>` - Get personalized recommendations
- `GET /api/library/<user_id>` - Get user's game library

## Testing

Run unit tests:
```bash
pytest tests/test_basic.py -v
```

## Database Schema

### MySQL Tables
- **users**: User accounts and authentication
- **user_sessions**: Active user sessions
- **user_library**: Games owned by users
- **games**: Basic game information (maintained for referential integrity)

### MongoDB Collections
- **games**: Complete game metadata (title, description, genres, tags, images, ratings)
- **user_activity**: User interaction tracking

## Author

Drin Jakupi - Systems Development Assignment

## License

Educational project for university coursework.