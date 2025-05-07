import json
import os
import threading
from config import WALLETS_FILE

wallets_lock = threading.Lock()

def load_wallets():
    if not os.path.exists(WALLETS_FILE):
        return {}
    with wallets_lock:
        with open(WALLETS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

def save_wallets(wallets):
    with wallets_lock:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f, indent=2)
