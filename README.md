# Pump.fun Account Creator

Automated account creation tool for pump.fun with Privy authentication.

## Features

- Bulk account creation with domain rotation
- Multi-threaded support for faster creation
- Automatic OTP fetching via API
- Profile customization (username, bio, profile picture)
- NLTK-powered username generation
- Auto-follow main profile
- Auto-reply to coin comments
- Database storage (MySQL)
- Proxy support
- Environment-based configuration

## Project Structure

```
PumpFun/
├── acc_creator.py          # Single-threaded account creator
├── acc_creator_multi.py    # Multi-threaded account creator
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (create from .env.example)
├── .env.example            # Example configuration
├── .gitignore
├── data/
│   ├── accounts.json       # Created accounts
│   ├── domains.json        # Email domains with stats
│   └── profile_image.png   # Default profile image
├── postman/                # API documentation
│   └── *.json
└── backup/                 # Backup files
```

## Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy example config and edit with your values
cp .env.example .env
```

## Configuration

Edit `.env` file with your settings:

```env
# Proxy
USE_PROXY=true
PROXY_USER=your_user
PROXY_PASS=your_pass

# Features
DO_FOLLOW=true
SEND_REPLY=false
UPDATE_PROFILE=true
INTERNET_IMAGE=true

# Database
SAVE_DATABASE=true
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=bots
```

## Usage

### Single-threaded
```bash
python3 acc_creator.py <amount> <sleep_seconds>
python3 acc_creator.py 10 30    # Create 10 accounts, 30s delay
```

### Multi-threaded
```bash
python3 acc_creator_multi.py <amount>
python3 acc_creator_multi.py 100    # Create 100 accounts
```

## Configuration Options

| Variable | Description |
|----------|-------------|
| `USE_PROXY` | Enable/disable proxy |
| `DO_FOLLOW` | Auto-follow main profile |
| `SEND_REPLY` | Send reply to coin comments |
| `UPDATE_PROFILE` | Update profile with username/bio |
| `INTERNET_IMAGE` | Use random internet images |
| `SAVE_DATABASE` | Save accounts to MySQL |
| `MAX_CONCURRENCY` | Thread count (multi only) |

## Dependencies

- `requests` - HTTP requests
- `pynacl` - Ed25519 cryptography
- `base58` - Solana address encoding
- `colorama` - Colored terminal output
- `fake-useragent` - Random user agents
- `pymysql` - MySQL database
- `python-dotenv` - Environment configuration
- `nltk` - Natural language username generation
