# 🚀 Pump.fun Account Creator

**Bulk Account Creator by [TheMysteryPanda](https://github.com/TheMysteryPanda)**

Automated account creation tool for pump.fun with Privy authentication.

---

## ✨ Features

- 🔄 Bulk account creation with domain rotation
- 📧 Automatic OTP fetching via API
- 👤 Profile customization (username, bio, profile picture)
- 🎲 NLTK-powered random username generation
- 👥 Auto-follow main profile
- 🗄️ Database storage (MySQL)
- 🌐 Proxy support
- ⚙️ Environment-based configuration

---

## 🎯 Milestones

| Stars | Reward |
|-------|--------|
| ⭐ 50 | 🚀 **Multi-threaded version** - Create accounts 10x faster! |
| ⭐ 100 | 💬 **Auto-reply feature** - 400+ random crypto comments! |
| ⭐ 250 | 🔥 **Live chat messaging** (WebSocket) |
| ⭐ 500 | 🎁 **Something special...** |

**Current:** Help us reach 50 stars to unlock the multi-threaded version!

---

## 📁 Project Structure

```
PumpFun/
├── acc_creator.py          # Main account creator
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (create from .env.example)
├── .env.example            # Example configuration
├── data/
│   ├── accounts.json       # Created accounts
│   ├── domains.json        # Email domains with stats
│   └── profile_image.png   # Default profile image (optional)
└── postman/                # API documentation
```

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/TheMysteryPanda/PumpFun.git
cd PumpFun

# Install dependencies
pip3 install -r requirements.txt

# Copy example config and edit with your values
cp .env.example .env
```

---

## ⚙️ Configuration

Edit `.env` file with your settings:

```env
# Proxy
USE_PROXY=true
PROXY_URL=http://your-proxy:port/

# Features
DO_FOLLOW=true
UPDATE_PROFILE=true
INTERNET_IMAGE=true

# Database (optional)
SAVE_DATABASE=true
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=bots
```

---

## 🚀 Usage

```bash
python3 acc_creator.py <amount> <sleep_seconds>

# Examples:
python3 acc_creator.py 10 30    # Create 10 accounts, 30s delay
python3 acc_creator.py 100 60   # Create 100 accounts, 60s delay
```

---

## 📊 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_PROXY` | Enable/disable proxy | `true` |
| `DO_FOLLOW` | Auto-follow main profile | `true` |
| `UPDATE_PROFILE` | Update profile with username/bio | `true` |
| `INTERNET_IMAGE` | Use random internet images | `true` |
| `SAVE_DATABASE` | Save accounts to MySQL | `true` |
| `PROGRESS_BAR` | Show progress bar instead of logs | `true` |

---

## 📦 Dependencies

- `requests` - HTTP requests
- `pynacl` - Ed25519 cryptography
- `base58` - Solana address encoding
- `colorama` - Colored terminal output
- `fake-useragent` - Random user agents
- `pymysql` - MySQL database
- `python-dotenv` - Environment configuration
- `nltk` - Natural language username generation
- `tqdm` - Progress bars

---

## ⭐ Star History

If you find this useful, please give it a star! It helps a lot and unlocks new features.

---

## 📜 License

MIT License - feel free to use and modify.

---

## 👨‍💻 Author

**TheMysteryPanda**
- GitHub: [@TheMysteryPanda](https://github.com/TheMysteryPanda)

---

<p align="center">
  <b>If you like this project, please ⭐ star it!</b>
</p>

---

## 🔍 Related

[pump.fun bot](https://fame.cheap/shop/pumpfun) · [pump.fun stream bots](https://fame.cheap/shop/pumpfun) · [pump.fun viewer bot](https://fame.cheap/shop/pumpfun) · [pump.fun view bots](https://fame.cheap/shop/pumpfun) · [pump.fun streaming](https://fame.cheap/shop/pumpfun) · [pump.fun hourly](https://fame.cheap/shop/pumpfun) · [pump.fun livebot](https://fame.cheap/shop/pumpfun) · [how to get viewers on pump.fun](https://fame.cheap/shop/pumpfun) · [viewer bot pump.fun](https://fame.cheap/shop/pumpfun) · [pump.fun bots](https://fame.cheap/shop/pumpfun) · [how to get more viewers on pump.fun](https://fame.cheap/shop/pumpfun) · [livebot for pump.fun](https://fame.cheap/shop/pumpfun) · [pump.fun chatbot](https://fame.cheap/shop/pumpfun) · [bots for pump.fun streaming](https://fame.cheap/shop/pumpfun) · [livestream viewer](https://fame.cheap/shop/pumpfun) · [pump.fun stream bot](https://fame.cheap/shop/pumpfun) · [best bot for pump.fun](https://fame.cheap/shop/pumpfun) · [pump.fun viewer bot free](https://fame.cheap/shop/pumpfun) · [pump.fun streaming bot](https://fame.cheap/shop/pumpfun) · [bots for pump.fun](https://fame.cheap/shop/pumpfun) · [bot pump.fun viewers](https://fame.cheap/shop/pumpfun) · [pump.fun view bot free](https://fame.cheap/shop/pumpfun) · [pump.fun chat bot](https://fame.cheap/shop/pumpfun) · [pump.fun viewer bots](https://fame.cheap/shop/pumpfun) · [free pump.fun view bot](https://fame.cheap/shop/pumpfun) · [pump.fun view botting](https://fame.cheap/shop/pumpfun) · [buy pump.fun viewers](https://fame.cheap/shop/pumpfun) · [pump.fun viewer](https://fame.cheap/shop/pumpfun) · [view bot pump.fun](https://fame.cheap/shop/pumpfun) · [pump.fun viewbotting](https://fame.cheap/shop/pumpfun) · [pump.fun streaming bots](https://fame.cheap/shop/pumpfun) · [pump.fun viewers](https://fame.cheap/shop/pumpfun) · [pump.fun viewbot](https://fame.cheap/shop/pumpfun) · [pump.fun view bot](https://fame.cheap/shop/pumpfun) · [pump.fun viewbot free](https://fame.cheap/shop/pumpfun) · [viewbot pump.fun](https://fame.cheap/shop/pumpfun) · [viewbots for pump.fun](https://fame.cheap/shop/pumpfun) · [pump.fun streaming viewbot](https://fame.cheap/shop/pumpfun) · [viewbot for pump.fun](https://fame.cheap/shop/pumpfun) · [pump.fun viewbots](https://fame.cheap/shop/pumpfun) · [free pump.fun viewbot](https://fame.cheap/shop/pumpfun) · [pump.fun streaming followers](https://fame.cheap/shop/pumpfun)
