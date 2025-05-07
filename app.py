from flask import Flask, request, jsonify
import uuid
import json
import os
import threading
from datetime import datetime
from flask_cors import CORS
from config import WALLETS_FILE
from storage import load_wallets, save_wallets

app = Flask(__name__)
CORS(app)
wallets_lock = threading.Lock()

# API Endpoints

@app.route('/wallets', methods=['POST'])
def create_wallet():
    wallets = load_wallets()
    wallet_id = str(uuid.uuid4())
    wallets[wallet_id] = {
        'id': wallet_id,
        'balance': 0.0,
        'transactions': []
    }
    save_wallets(wallets)
    return jsonify(wallets[wallet_id]), 201

@app.route('/wallets/<wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    wallets = load_wallets()
    wallet = wallets.get(wallet_id)
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    return jsonify(wallet)

@app.route('/wallets/<wallet_id>/deposit', methods=['POST'])
def deposit(wallet_id):
    wallets = load_wallets()
    wallet = wallets.get(wallet_id)
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400
    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Amount must be a number'}), 400
    if amount <= 0:
        return jsonify({'error': 'Invalid deposit amount'}), 400
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat()
    wallet['balance'] += amount
    wallet['transactions'].append({
        'type': 'deposit',
        'amount': amount,
        'timestamp': timestamp
    })
    save_wallets(wallets)
    return jsonify(wallet)

@app.route('/wallets/<wallet_id>/withdraw', methods=['POST'])
def withdraw(wallet_id):
    wallets = load_wallets()
    wallet = wallets.get(wallet_id)
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400
    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Amount must be a number'}), 400
    if amount <= 0:
        return jsonify({'error': 'Invalid withdraw amount'}), 400
    if amount > wallet['balance']:
        return jsonify({'error': 'Insufficient funds'}), 400
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat()
    wallet['balance'] -= amount
    wallet['transactions'].append({
        'type': 'withdraw',
        'amount': amount,
        'timestamp': timestamp
    })
    save_wallets(wallets)
    return jsonify(wallet)

@app.route('/wallets/<wallet_id>/transactions', methods=['GET'])
def get_transactions(wallet_id):
    wallets = load_wallets()
    wallet = wallets.get(wallet_id)
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    return jsonify(wallet['transactions'])

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
