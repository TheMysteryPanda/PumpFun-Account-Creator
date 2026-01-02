#!/usr/bin/env python3
"""
Pump.fun Bulk Account Creator
Usage: python3 acc_creator.py <amount_of_accounts> <sleep_time_between_accounts>
"""

import sys
import os
import json
import random
import string
import time
import requests
import uuid
import re
import base58
import pymysql
import nltk
from tqdm import tqdm
from datetime import datetime
from nacl.signing import SigningKey
from nacl.encoding import RawEncoder
from colorama import init, Fore, Style
from fake_useragent import UserAgent
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Initialize fake user agent
ua = UserAgent()

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
DOMAINS_FILE = os.path.join(DATA_DIR, "domains.json")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

# Load environment variables
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# Helper function to parse boolean env vars
def env_bool(key, default=False):
    return os.getenv(key, str(default)).lower() in ('true', '1', 'yes')

# Proxy configuration
USE_PROXY = env_bool('USE_PROXY', True)
PROXY_URL = os.getenv('PROXY_URL', 'http://p.webshare.io:9999/')
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

# OTP API Configuration
OTP_API_URL = os.getenv('OTP_API_URL', 'https://email.famecheap.support/webmail/pumpfun/INBOX')
OTP_TIMEOUT = int(os.getenv('OTP_TIMEOUT', '90'))

# Constants
MAX_ERROR_COUNT = 5

# Follow configuration
DO_FOLLOW = env_bool('DO_FOLLOW', True)
MAIN_PROFILE = os.getenv('MAIN_PROFILE', '')

# Profile update configuration
UPDATE_PROFILE = env_bool('UPDATE_PROFILE', True)
PROFILE_BIO = os.getenv('PROFILE_BIO', '')
PROFILE_IMAGE_PATH = os.path.join(DATA_DIR, "profile_image.png")
INTERNET_IMAGE = env_bool('INTERNET_IMAGE', True)

# Database configuration
SAVE_DATABASE = env_bool('SAVE_DATABASE', True)
DB_HOST = os.getenv('DB_HOST', '')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', '')
DB_TABLE = os.getenv('DB_TABLE', 'pumpfun')

# Display configuration
PROGRESS_BAR = env_bool('PROGRESS_BAR', False)

# Download NLTK data (silently)
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words', quiet=True)

# Load NLTK words for username generation
from nltk.corpus import words
NLTK_WORDS = [w.lower() for w in words.words() if 4 <= len(w) <= 8 and w.isalpha()]


def print_banner():
    """Print colored banner"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  {Fore.MAGENTA}██████╗ ██╗   ██╗███╗   ███╗██████╗    ███████╗██╗   ██╗███╗   ██╗{Fore.CYAN}  ║
║  {Fore.MAGENTA}██╔══██╗██║   ██║████╗ ████║██╔══██╗   ██╔════╝██║   ██║████╗  ██║{Fore.CYAN}  ║
║  {Fore.MAGENTA}██████╔╝██║   ██║██╔████╔██║██████╔╝   █████╗  ██║   ██║██╔██╗ ██║{Fore.CYAN}  ║
║  {Fore.MAGENTA}██╔═══╝ ██║   ██║██║╚██╔╝██║██╔═══╝    ██╔══╝  ██║   ██║██║╚██╗██║{Fore.CYAN}  ║
║  {Fore.MAGENTA}██║     ╚██████╔╝██║ ╚═╝ ██║██║        ██║     ╚██████╔╝██║ ╚████║{Fore.CYAN}  ║
║  {Fore.MAGENTA}╚═╝      ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝      ╚═════╝ ╚═╝  ╚═══╝{Fore.CYAN}  ║
║                                                                      ║
║  {Fore.YELLOW}Bulk Account Creator{Fore.CYAN}                                                ║
╚══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def log_info(msg, indent=0):
    if PROGRESS_BAR:
        return
    prefix = "    " * indent
    print(f"{prefix}{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")


def log_success(msg, indent=0):
    if PROGRESS_BAR:
        return
    prefix = "    " * indent
    print(f"{prefix}{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")


def log_error(msg, indent=0):
    if PROGRESS_BAR:
        return
    prefix = "    " * indent
    print(f"{prefix}{Fore.RED}[-]{Style.RESET_ALL} {msg}")


def log_warning(msg, indent=0):
    if PROGRESS_BAR:
        return
    prefix = "    " * indent
    print(f"{prefix}{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")


def generate_username() -> str:
    """Generate a random realistic-sounding username using NLTK words"""
    word1 = random.choice(NLTK_WORDS)
    word2 = random.choice(NLTK_WORDS)
    num = random.randint(1, 999)

    # Different patterns
    patterns = [
        f"{word1}{word2}{num}",
        f"{word1}_{word2}",
        f"{word1}{num}",
        f"{word1}{word2}",
        f"{word2}_{num}",
    ]
    return random.choice(patterns)


def load_json(filepath: str) -> list:
    """Load JSON file"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
    return []


def save_json(filepath: str, data: list):
    """Save JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def generate_random_username(length: int = 10) -> str:
    """Generate random username"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class DomainManager:
    def __init__(self):
        self.domains = load_json(DOMAINS_FILE)

    def get_active_domain(self) -> dict:
        """Get a random active domain"""
        active_domains = [d for d in self.domains if d.get("is_active", 1) == 1]
        if not active_domains:
            return None
        return random.choice(active_domains)

    def increment_error(self, domain: str):
        """Increment error count for a domain"""
        for d in self.domains:
            if d["domain"] == domain:
                d["error_count"] = d.get("error_count", 0) + 1
                if d["error_count"] >= MAX_ERROR_COUNT:
                    d["is_active"] = 0
                    log_warning(f"Domain {Fore.RED}{domain}{Style.RESET_ALL} deactivated (errors >= {MAX_ERROR_COUNT})", indent=1)
                self.save()
                break

    def increment_success(self, domain: str):
        """Increment accounts created for a domain"""
        for d in self.domains:
            if d["domain"] == domain:
                d["accounts_created"] = d.get("accounts_created", 0) + 1
                d["error_count"] = 0  # Reset error count on success
                self.save()
                break

    def save(self):
        """Save domains to file"""
        save_json(DOMAINS_FILE, self.domains)

    def get_stats(self) -> dict:
        """Get domain statistics"""
        active = sum(1 for d in self.domains if d.get("is_active", 1) == 1)
        inactive = len(self.domains) - active
        total_accounts = sum(d.get("accounts_created", 0) for d in self.domains)
        return {"active": active, "inactive": inactive, "total_accounts": total_accounts}


class AccountManager:
    def __init__(self):
        self.accounts = load_json(ACCOUNTS_FILE)

    def add_account(self, account: dict):
        """Add account to JSON and optionally to database"""
        self.accounts.append(account)
        self.save()

        # Save to database if enabled
        if SAVE_DATABASE:
            self.save_to_database(account)

    def save(self):
        """Save accounts to file"""
        save_json(ACCOUNTS_FILE, self.accounts)

    def save_to_database(self, account: dict):
        """Save account to MySQL database"""
        try:
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = conn.cursor()

            sql = f"""
                INSERT INTO {DB_TABLE}
                (email, domain, wallet_address, private_key, profile_url, username, bio,
                 profile_picture, followed_main, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                account.get('email'),
                account.get('domain'),
                account.get('wallet_address'),
                account.get('private_key'),
                account.get('profile_url'),
                account.get('username'),
                account.get('bio'),
                account.get('profile_picture', False),
                account.get('followed_main', False),
                account.get('created_at')
            )

            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            log_warning(f"Database save failed: {e}")


class EmailFetcher:
    def __init__(self):
        self.api_url = OTP_API_URL

    def wait_for_otp(self, target_email: str, timeout: int = OTP_TIMEOUT, poll_interval: int = 3) -> str:
        """Wait for OTP via web API and extract the code"""
        # Extract username from email (part before @)
        username = target_email.split('@')[0]
        url = f"{self.api_url}/{username}"

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    text = response.text
                    # Look for 6-digit OTP code
                    match = re.search(r'\b(\d{6})\b', text)
                    if match:
                        return match.group(1)
            except Exception:
                pass

            time.sleep(poll_interval)

        return None


class SolanaWallet:
    def __init__(self):
        self.signing_key = SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        self.public_key = base58.b58encode(bytes(self.verify_key)).decode()
        self.private_key = base58.b58encode(bytes(self.signing_key)).decode()

    def sign_message(self, message: str) -> str:
        """Sign a message and return base58 encoded signature"""
        message_bytes = message.encode('utf-8')
        signed = self.signing_key.sign(message_bytes, encoder=RawEncoder)
        signature = signed[:64]
        return base58.b58encode(signature).decode()


class PumpFunAuth:
    def __init__(self):
        self.session = requests.Session()
        self.privy_base_url = "https://auth.privy.io/api/v1"
        self.pump_base_url = "https://frontend-api-v3.pump.fun"
        self.client_id = "client-WY5brZnRUhFQnX6ip6yRzypC9WLtB9j8mFnq4cyPBMq8W"
        self.ca_id = str(uuid.uuid4())
        self.access_token = None
        self.wallet = None

        # Set proxy for session
        if USE_PROXY:
            self.session.proxies.update(PROXIES)

        # Generate random user agent
        self.user_agent = ua.random

        self.privy_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "privy-app-id": "cm1p2gzot03fzqty5xzgjgthq",
            "privy-client": "react-auth:2.21.4",
            "privy-client-id": self.client_id,
            "privy-ca-id": self.ca_id,
            "privy-ui": "t",
            "User-Agent": self.user_agent,
            "Origin": "https://pump.fun",
            "Referer": "https://pump.fun/",
        }

        self.pump_headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "Origin": "https://pump.fun",
            "Referer": "https://pump.fun/",
        }

    def init_passwordless(self, email_addr: str) -> bool:
        """Send OTP to email"""
        url = f"{self.privy_base_url}/passwordless/init"
        payload = {"email": email_addr}

        try:
            response = self.session.post(url, json=payload, headers=self.privy_headers, timeout=30)
            return response.status_code == 200
        except Exception:
            return False

    def authenticate(self, email_addr: str, otp: str) -> bool:
        """Authenticate with email and OTP"""
        url = f"{self.privy_base_url}/passwordless/authenticate"
        payload = {
            "email": email_addr,
            "code": otp,
            "mode": "login-or-sign-up"
        }

        try:
            response = self.session.post(url, json=payload, headers=self.privy_headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("token")
                return True
        except Exception:
            pass
        return False

    def pump_login(self) -> bool:
        """Login to pump.fun with Solana wallet"""
        self.wallet = SolanaWallet()

        timestamp = int(time.time() * 1000)
        message = f"Sign in to pump.fun: {timestamp}"
        signature = self.wallet.sign_message(message)

        url = f"{self.pump_base_url}/auth/login"
        payload = {
            "address": self.wallet.public_key,
            "signature": signature,
            "timestamp": timestamp
        }

        try:
            response = self.session.post(url, json=payload, headers=self.pump_headers, timeout=30)
            return response.status_code in [200, 201]
        except Exception:
            return False

    def pump_register(self) -> bool:
        """Register on pump.fun"""
        if not self.wallet:
            return False

        url = f"{self.pump_base_url}/users/register"
        payload = {"address": self.wallet.public_key}

        try:
            response = self.session.post(url, json=payload, headers=self.pump_headers, timeout=30)
            return response.status_code in [200, 201]
        except Exception:
            return False

    def follow_profile(self, profile_address: str) -> bool:
        """Follow a profile on pump.fun"""
        url = f"{self.pump_base_url}/following/v2/{profile_address}"

        try:
            response = self.session.post(url, headers=self.pump_headers, timeout=30)
            return response.status_code in [200, 201]
        except Exception:
            return False

    def fetch_random_image(self) -> tuple:
        """Fetch a random image from the internet and return as bytes"""
        # Using picsum.photos for random images (200x200 px)
        url = f"https://picsum.photos/200/200?random={random.randint(1, 100000)}"

        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            if response.status_code == 200:
                return response.content, None
            else:
                return None, f"Failed to fetch image: {response.status_code}"
        except Exception as e:
            return None, str(e)

    def upload_image_bytes_to_ipfs(self, image_bytes: bytes, filename: str = "profile.jpg") -> tuple:
        """Upload image bytes to IPFS and return the URL"""
        url = "https://pump.fun/api/ipfs-file"

        try:
            files = {'file': (filename, image_bytes, 'image/jpeg')}
            headers = {
                "Accept": "*/*",
                "User-Agent": self.user_agent,
                "Origin": "https://pump.fun",
                "Referer": "https://pump.fun/",
            }
            response = self.session.post(url, files=files, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                ipfs_url = data.get('fileUri') or data.get('metadataUri') or data.get('url') or data.get('ipfsUrl')
                if ipfs_url:
                    return ipfs_url, None
                return None, f"No IPFS URL in response: {response.text[:200]}"
            else:
                return None, f"{response.status_code}: {response.text[:200]}"
        except Exception as e:
            return None, str(e)

    def upload_image_to_ipfs(self, image_path: str) -> tuple:
        """Upload image to IPFS and return the URL"""
        url = "https://pump.fun/api/ipfs-file"

        if not os.path.exists(image_path):
            return None, f"Image file not found: {image_path}"

        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/png')}
                headers = {
                    "Accept": "*/*",
                    "User-Agent": self.user_agent,
                    "Origin": "https://pump.fun",
                    "Referer": "https://pump.fun/",
                }
                response = self.session.post(url, files=files, headers=headers, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    # Response should contain the IPFS URL
                    ipfs_url = data.get('fileUri') or data.get('metadataUri') or data.get('url') or data.get('ipfsUrl')
                    if ipfs_url:
                        return ipfs_url, None
                    return None, f"No IPFS URL in response: {response.text[:200]}"
                else:
                    return None, f"{response.status_code}: {response.text[:200]}"
        except Exception as e:
            return None, str(e)

    def update_profile(self, username: str, bio: str, profile_image_url: str = None) -> tuple:
        """Update user profile with username, bio, and optional profile image"""
        url = f"{self.pump_base_url}/users"
        payload = {
            "username": username,
            "bio": bio
        }

        if profile_image_url:
            payload["profileImage"] = profile_image_url

        try:
            response = self.session.post(url, json=payload, headers=self.pump_headers, timeout=30)
            if response.status_code in [200, 201]:
                return True, None
            else:
                return False, f"{response.status_code}: {response.text[:200]}"
        except Exception as e:
            return False, str(e)


def create_account(domain_manager: DomainManager, account_manager: AccountManager, email_fetcher: EmailFetcher) -> bool:
    """Create a single pump.fun account"""

    # Get active domain
    domain_info = domain_manager.get_active_domain()
    if not domain_info:
        log_error("No active domains available!", indent=1)
        return False

    domain = domain_info["domain"]
    username = generate_random_username()
    email_addr = f"{username}@{domain}"

    log_info(f"Email: {Fore.WHITE}{email_addr}{Style.RESET_ALL}", indent=1)

    auth = PumpFunAuth()

    # Step 1: Send OTP
    log_info("Sending OTP...", indent=1)
    if not auth.init_passwordless(email_addr):
        log_error("Failed to send OTP", indent=1)
        domain_manager.increment_error(domain)
        return False

    # Step 2: Wait for OTP
    log_info("Waiting for OTP...", indent=1)
    otp = email_fetcher.wait_for_otp(email_addr)
    if not otp:
        log_error("OTP not received (timeout)", indent=1)
        domain_manager.increment_error(domain)
        return False

    log_success(f"OTP received: {Fore.YELLOW}{otp}{Style.RESET_ALL}", indent=1)

    # Step 3: Authenticate
    log_info("Authenticating...", indent=1)
    if not auth.authenticate(email_addr, otp):
        log_error("Authentication failed", indent=1)
        return False

    # Step 4: Login to pump.fun
    log_info("Logging into pump.fun...", indent=1)
    if not auth.pump_login():
        log_error("Pump.fun login failed", indent=1)
        return False

    # Step 5: Register
    log_info("Registering...", indent=1)
    if not auth.pump_register():
        log_error("Registration failed", indent=1)
        return False

    # Step 6: Update profile (if enabled)
    profile_picture_uploaded = False
    generated_username = None
    bio_used = None
    if UPDATE_PROFILE:
        log_info("Updating profile...", indent=1)

        # Upload profile image to IPFS
        ipfs_url = None
        if INTERNET_IMAGE:
            # Fetch random image from the internet
            log_info("Fetching random image...", indent=2)
            image_bytes, error = auth.fetch_random_image()
            if image_bytes:
                log_info("Uploading to IPFS...", indent=2)
                ipfs_url, error = auth.upload_image_bytes_to_ipfs(image_bytes)
                if ipfs_url:
                    log_success("Image uploaded to IPFS", indent=2)
                    profile_picture_uploaded = True
                else:
                    log_warning(f"IPFS upload failed: {error}", indent=2)
            else:
                log_warning(f"Image fetch failed: {error}", indent=2)
        elif os.path.exists(PROFILE_IMAGE_PATH):
            log_info("Uploading profile image...", indent=2)
            ipfs_url, error = auth.upload_image_to_ipfs(PROFILE_IMAGE_PATH)
            if ipfs_url:
                log_success("Image uploaded to IPFS", indent=2)
                profile_picture_uploaded = True
            else:
                log_warning(f"Image upload failed: {error}", indent=2)

        # Generate username and update profile
        generated_username = generate_username()
        bio_used = PROFILE_BIO
        success, error = auth.update_profile(generated_username, PROFILE_BIO, ipfs_url)
        if success:
            log_success(f"Profile updated: {Fore.YELLOW}{generated_username}{Style.RESET_ALL}", indent=1)
        else:
            log_warning(f"Profile update failed: {Fore.RED}{error}{Style.RESET_ALL}", indent=1)

    # Step 7: Follow main profile (if enabled)
    followed = False
    if DO_FOLLOW:
        log_info(f"Following main profile...", indent=1)
        if auth.follow_profile(MAIN_PROFILE):
            log_success(f"Followed {Fore.YELLOW}{MAIN_PROFILE[:8]}...{Style.RESET_ALL}", indent=1)
            followed = True
        else:
            log_warning("Follow failed (non-critical)", indent=1)

    # Success!
    profile_url = f"https://pump.fun/profile/{auth.wallet.public_key}"
    print()
    log_success(f"{Fore.GREEN}{Style.BRIGHT}SUCCESS!{Style.RESET_ALL}", indent=1)
    log_success(f"Wallet: {Fore.YELLOW}{auth.wallet.public_key}{Style.RESET_ALL}", indent=1)
    log_success(f"Profile: {Fore.BLUE}{profile_url}{Style.RESET_ALL}", indent=1)

    # Save account
    account_data = {
        "email": email_addr,
        "domain": domain,
        "wallet_address": auth.wallet.public_key,
        "private_key": auth.wallet.private_key,
        "profile_url": profile_url,
        "username": generated_username,
        "bio": bio_used,
        "profile_picture": profile_picture_uploaded,
        "followed_main": followed,
        "created_at": datetime.now().isoformat()
    }
    account_manager.add_account(account_data)
    domain_manager.increment_success(domain)

    return True


def main():
    if len(sys.argv) < 3:
        print_banner()
        print(f"{Fore.RED}Usage:{Style.RESET_ALL} python3 acc_creator.py <amount_of_accounts> <sleep_time_between_accounts>")
        print(f"{Fore.YELLOW}Example:{Style.RESET_ALL} python3 acc_creator.py 10 30")
        sys.exit(1)

    try:
        amount = int(sys.argv[1])
        sleep_time = int(sys.argv[2])
    except ValueError:
        print(f"{Fore.RED}Error:{Style.RESET_ALL} Both arguments must be integers")
        sys.exit(1)

    print_banner()

    domain_manager = DomainManager()
    account_manager = AccountManager()
    email_fetcher = EmailFetcher()

    stats = domain_manager.get_stats()
    print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    log_info(f"Active domains: {Fore.GREEN}{stats['active']}{Style.RESET_ALL}")
    log_info(f"Inactive domains: {Fore.RED}{stats['inactive']}{Style.RESET_ALL}")
    log_info(f"Total accounts created: {Fore.YELLOW}{stats['total_accounts']}{Style.RESET_ALL}")
    proxy_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL}" if USE_PROXY else f"{Fore.RED}Disabled{Style.RESET_ALL}"
    log_info(f"Proxy: {proxy_status}")
    log_info(f"Random User-Agent: {Fore.GREEN}Enabled{Style.RESET_ALL}")
    follow_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL} ({MAIN_PROFILE[:8]}...)" if DO_FOLLOW else f"{Fore.RED}Disabled{Style.RESET_ALL}"
    log_info(f"Auto-Follow: {follow_status}")
    profile_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL} (bio: {PROFILE_BIO})" if UPDATE_PROFILE else f"{Fore.RED}Disabled{Style.RESET_ALL}"
    log_info(f"Profile Update: {profile_status}")
    if UPDATE_PROFILE:
        image_source = f"{Fore.MAGENTA}Internet (random){Style.RESET_ALL}" if INTERNET_IMAGE else f"{Fore.YELLOW}Local file{Style.RESET_ALL}"
        log_info(f"Profile Image: {image_source}")
    db_status = f"{Fore.GREEN}Enabled{Style.RESET_ALL} ({DB_HOST})" if SAVE_DATABASE else f"{Fore.RED}Disabled{Style.RESET_ALL}"
    log_info(f"Database Save: {db_status}")
    if not PROGRESS_BAR:
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        log_info(f"Creating {Fore.WHITE}{amount}{Style.RESET_ALL} accounts with {Fore.WHITE}{sleep_time}s{Style.RESET_ALL} delay")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")

    success_count = 0
    fail_count = 0
    attempt = 0

    # Progress bar mode
    if PROGRESS_BAR:
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        pbar = tqdm(
            total=amount,
            desc=f"{Fore.GREEN}Creating accounts{Style.RESET_ALL}",
            bar_format='{desc}: {bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}',
            ncols=80
        )
        pbar.set_postfix_str(f'{Fore.GREEN}✓{success_count}{Style.RESET_ALL} {Fore.RED}✗{fail_count}{Style.RESET_ALL}')

        while success_count < amount:
            attempt += 1
            try:
                if create_account(domain_manager, account_manager, email_fetcher):
                    success_count += 1
                    pbar.update(1)
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

            pbar.set_postfix_str(f'{Fore.GREEN}✓{success_count}{Style.RESET_ALL} {Fore.RED}✗{fail_count}{Style.RESET_ALL}')

            if success_count < amount:
                time.sleep(sleep_time)

        pbar.close()
    else:
        # Verbose mode
        while success_count < amount:
            attempt += 1
            print()
            print(f"{Fore.MAGENTA}{Style.BRIGHT}[Account {success_count + 1}/{amount}]{Style.RESET_ALL} {Fore.CYAN}(attempt #{attempt}){Style.RESET_ALL}")

            try:
                if create_account(domain_manager, account_manager, email_fetcher):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                log_error(f"Error: {e}", indent=1)
                fail_count += 1

            if success_count < amount:
                print()
                log_info(f"Sleeping {Fore.YELLOW}{sleep_time}s{Style.RESET_ALL}...", indent=1)
                time.sleep(sleep_time)

    # Summary
    print()
    print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}  SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Successful: {Fore.GREEN}{Style.BRIGHT}{success_count}{Style.RESET_ALL}")
    print(f"{Fore.RED}[-]{Style.RESET_ALL} Failed: {Fore.RED}{Style.BRIGHT}{fail_count}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} Total attempts: {Fore.YELLOW}{attempt}{Style.RESET_ALL}")
    print()

    stats = domain_manager.get_stats()
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} Active domains remaining: {Fore.GREEN}{stats['active']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} Total accounts created: {Fore.YELLOW}{stats['total_accounts']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} Accounts saved to: {Fore.BLUE}{ACCOUNTS_FILE}{Style.RESET_ALL}")
    print()


if __name__ == "__main__":
    main()
