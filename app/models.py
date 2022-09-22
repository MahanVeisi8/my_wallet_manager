from datetime import datetime
from app import db


class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True, unique=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    coins = db.relationship('WalletCoin', cascade='all, delete')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'coins': self.coins
        }


class Coin(db.Model):
    __tablename__ = 'coins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True, unique=True)
    symbol = db.Column(db.String(255), nullable=False, index=True, unique=True)
    price = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    wallets = db.relationship('WalletCoin', cascade='all, delete')


class WalletCoin(db.Model):
    __tablename__ = 'wallet_coin'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.ForeignKey('wallets.id'))
    coin_id = db.Column(db.ForeignKey('coins.id'))
    quantity = db.Column(db.Numeric, nullable=False)
    coin = db.relationship('Coin', back_populates='wallets')
    wallet = db.relationship('Wallet', back_populates='coins')
