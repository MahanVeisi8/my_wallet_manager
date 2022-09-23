from flask import jsonify, request
from app import app, db
from app.models import *


@app.route('/wallets', methods=['GET'])
def get_wallets():
    wallets = Wallet.query.all()
    wallets = [wallet.to_dict() for wallet in wallets]
    for wallet in wallets:
        balance = 0
        for coin in wallet['coins']:
            balance += coin['quantity'] * coin['coin']['price']
        wallet['balance'] = balance
    return jsonify(wallets), 200


@app.route('/wallets', methods=['POST'])
def create_wallet():

    name = request.form.get('name')
    if not name:
        return jsonify({'error': "no name provided"}), 400
    wallet = Wallet.query.filter_by(name=name).first()
    if wallet:
        return jsonify({'error': "a wallet with the given name already exists"}), 400
    wallet = Wallet(name=name)
    db.session.add(wallet)
    db.session.commit()
    return jsonify({'id': wallet.id, 'name': wallet.name, 'balance': 0, 'coins': [], 'created_at': wallet.created_at, 'updated_at': wallet.updated_at}), 201


@app.route('/wallets/<int:wallet_id>', methods=['PUT'])
def edit_wallet_name(wallet_id):

    name = request.form.get('name')
    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if not wallet:
        return jsonify({'error': "not found"}), 404
    if not name:
        return jsonify({'error': "no name provided"}), 400
    wallet = Wallet.query.filter_by(name=name).first()
    if wallet:
        return jsonify({'error': "a wallet with the given name already exists"}), 400
    wallet.name = name
    db.session.commit()
    return jsonify({'id': wallet.id, 'name': wallet.name, 'balance': wallet.balance, 'coins': wallet.coins, 'created_at': wallet.created_at, 'updated_at': wallet.updated_at}), 200



@app.route('/wallets/<int:wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):

    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if not wallet:
        return jsonify({'error': "not found"}), 404
    db.session.delete(wallet)
    db.session.commit()
    return jsonify({'id': wallet.id, 'name': wallet.name, 'balance': wallet.balance, 'coins': wallet.coins, 'created_at': wallet.created_at, 'updated_at': wallet.updated_at}), 200


@app.route('/coins', methods=['GET'])
def get_coins():

    coins = Coin.query.all()
    coins = [coin.to_dict() for coin in coins]
    return jsonify({'coins': coins}), 200


@app.route('/coins', methods=['POST'])
def create_coin():

    name = request.form.get('name')
    symbol = request.form.get('symbol')
    price = request.form.get('price')
    if not name:
        return jsonify({'error': "no name provided"}), 400
    if not symbol:
        return jsonify({'error': "no symbol provided"}), 400
    if not price:
        return jsonify({'error': "no price provided"}), 400
    coin = Coin.query.filter_by(name=name).first()
    if coin:
        return jsonify({'error': "a coin with the given name already exists"}), 400
    coin = Coin.query.filter_by(symbol=symbol).first()
    if coin:
        return jsonify({'error': "a coin with the given symbol already exists"}), 400
    coin = Coin(name=name, symbol=symbol, price=price)
    db.session.add(coin)
    db.session.commit()
    return jsonify({'id': coin.id, 'name': coin.name, 'symbol': coin.symbol, 'price': coin.price, 'created_at': coin.created_at, 'updated_at': coin.updated_at}), 201


@app.route('/wallets/<int:wallet_id>/add_coin', methods=['POST'])
def add_and_edit_coin_to_wallet(wallet_id):

    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if not wallet:
        return jsonify({'error': "not found"}), 404
    coin_id = request.form.get('coin_id')
    if not coin_id:
        return jsonify({'error': "no coin_id provided"}), 400
    coin = Coin.query.filter_by(id=coin_id).first()
    if not coin:
        return jsonify({'error': "invalid coin_id"}), 404
    quantity = request.form.get('quantity')
    if not quantity:
        return jsonify({'error': "no quantity provided"}), 400
    wallet_coin = WalletCoin.query.filter_by(wallet_id=wallet_id, coin_id=coin_id).first()
    if wallet_coin:
        wallet_coin.quantity = quantity
        db.session.commit()
        return jsonify({'id': wallet_coin.id, 'name': wallet_coin.name, 'balance': wallet_coin.balance, 'coins': wallet_coin.coins, 'created_at': wallet_coin.created_at, 'updated_at': wallet_coin.updated_at}), 200
    wallet_coin = WalletCoin(wallet_id=wallet_id, coin_id=coin_id, quantity=quantity)
    db.session.add(wallet_coin)
    db.session.commit()
    return jsonify({'id': wallet_coin.id, 'name': wallet_coin.name, 'balance': wallet_coin.balance, 'coins': wallet_coin.coins, 'created_at': wallet_coin.created_at, 'updated_at': wallet_coin.updated_at}), 200


@app.route('/wallets/<int:wallet_id>/delete_coin', methods=['DELETE'])
def delete_coin_from_wallet(wallet_id):

    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if not wallet:
        return jsonify({'error': "not found"}), 404
    coin_id = request.form.get('coin_id')
    if not coin_id:
        return jsonify({'error': "no coin_id provided"}), 400
    coin = Coin.query.filter_by(id=coin_id).first()
    if not coin:
        return jsonify({'error': "invalid coin_id"}), 400
    wallet_coin = WalletCoin.query.filter_by(wallet_id=wallet_id, coin_id=coin_id).first()
    if not wallet_coin:
        return jsonify({'error': "the wallet does not contain the given coin"}), 400
    db.session.delete(wallet_coin)
    db.session.commit()
    return jsonify({'id': wallet_coin.id, 'name': wallet_coin.name, 'balance': wallet_coin.balance, 'coins': wallet_coin.coins, 'created_at': wallet_coin.created_at, 'updated_at': wallet_coin.updated_at}), 200


@app.route('/coins/<int:coin_id>', methods=['PUT'])
def edit_coin(coin_id):

    coin = Coin.query.filter_by(id=coin_id).first()
    if not coin:
        return jsonify({'error': "not found"}), 404
    name = request.form.get('name')
    symbol = request.form.get('symbol')
    price = request.form.get('price')
    if not name:
        return jsonify({'error': "no name provided"}), 400
    if not symbol:
        return jsonify({'error': "no symbol provided"}), 400
    if not price:
        return jsonify({'error': "no price provided"}), 400
    coin = Coin.query.filter_by(name=name).first()
    if coin:
        return jsonify({'error': "a coin with the given name already exists"}), 400
    coin = Coin.query.filter_by(symbol=symbol).first()
    if coin:
        return jsonify({'error': "a coin with the given symbol already exists"}), 400
    coin.name = name
    coin.symbol = symbol
    coin.price = price
    coin.updated_at = datetime.now()
    db.session.commit()
    return jsonify({'id': coin.id, 'name': coin.name, 'symbol': coin.symbol, 'price': coin.price, 'created_at': coin.created_at, 'updated_at': coin.updated_at}), 200


@app.route('/coins/<int:coin_id>', methods=['DELETE'])
def delete_coin(coin_id):
    coin = Coin.query.filter_by(id=coin_id).first()
    if not coin:
        return jsonify({'error': "not found"}), 404
    db.session.delete(coin)
    db.session.commit()
    return jsonify({'id': coin.id, 'name': coin.name, 'symbol': coin.symbol, 'price': coin.price, 'created_at': coin.created_at, 'updated_at': coin.updated_at}), 200