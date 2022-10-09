from flask import jsonify, request
from app import app, db
from app.models import *

@app.route('/wallets', methods=['GET'])
def get_wallets():
    wallets = Wallet.query.all()
    return jsonify({'wallets': wallets})
