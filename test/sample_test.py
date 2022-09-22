import json
import unittest
import sqlite3
import time
from datetime import datetime, timedelta
from dateutil import parser
from flask_migrate import upgrade
from app import app, db


tz = -time.timezone + (3600 if time.daylight != 0 else 0)


class AppTest(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        with app.app_context():
            upgrade()

    def tearDown(self):
        self.ctx.pop()

    def test_get_wallets_zero_balance(self):
        now = datetime.now()
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w1", "{now}", "{now}")')
        response = self.client.get('/wallets')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(response_json), 1)
        wallet = response_json[0]
        self.assertEqual(wallet['id'], 1)
        self.assertEqual(wallet['name'], 'w1')
        self.assertEqual(float(wallet['balance']), 0)
        self.assertEqual(wallet['coins'], [])
        actual_created_at = int(datetime.timestamp(parser.parse(wallet['created_at']))) - tz
        expected_created_at = int(datetime.timestamp(now))
        self.assertEqual(actual_created_at, expected_created_at)

        now = datetime.now()
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w2", "{now}", "{now}")')
        response = self.client.get('/wallets')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(response_json), 2)
        wallet = response_json[1]
        self.assertEqual(wallet['id'], 2)
        self.assertEqual(wallet['name'], 'w2')
        self.assertEqual(float(wallet['balance']), 0)
        self.assertEqual(wallet['coins'], [])

        actual_created_at = int(datetime.timestamp(parser.parse(wallet['created_at']))) - tz
        expected_created_at = int(datetime.timestamp(now))
        self.assertEqual(actual_created_at, expected_created_at)

        actual_updated_at = int(datetime.timestamp(parser.parse(wallet['updated_at']))) - tz
        expected_updated_at = int(datetime.timestamp(now))
        self.assertEqual(actual_updated_at, expected_updated_at)

    def test_get_wallets_non_zero_balance(self):
        now = datetime.now()
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w1", "{now}", "{now}")')
        db.engine.execute(f'INSERT INTO coins (name, symbol, price, created_at, updated_at) VALUES ("Bitcoin", "BTC", "45000", "{now}", "{now}")')
        db.engine.execute(f'INSERT INTO wallet_coin (wallet_id, coin_id, quantity) VALUES (1, 1, 2)')
        response = self.client.get('/wallets')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(response_json), 1)
        wallet = response_json[0]
        self.assertEqual(wallet['id'], 1)
        self.assertEqual(wallet['name'], 'w1')
        self.assertEqual(float(wallet['balance']), 90000)

        actual_created_at = int(datetime.timestamp(parser.parse(wallet['created_at']))) - tz
        expected_created_at = int(datetime.timestamp(now))
        self.assertEqual(actual_created_at, expected_created_at)

        actual_updated_at = int(datetime.timestamp(parser.parse(wallet['updated_at']))) - tz
        expected_updated_at = int(datetime.timestamp(now))
        self.assertEqual(actual_updated_at, expected_updated_at)

        self.assertEqual(len(wallet['coins']), 1)
        coin = wallet['coins'][0]
        self.assertEqual(coin['id'], 1)
        self.assertEqual(coin['name'], 'Bitcoin')
        self.assertEqual(coin['symbol'], 'BTC')
        self.assertEqual(float(coin['price']), 45000)

        actual_created_at = int(datetime.timestamp(parser.parse(coin['created_at']))) - tz
        expected_created_at = int(datetime.timestamp(now))
        self.assertEqual(actual_created_at, expected_created_at)

        actual_updated_at = int(datetime.timestamp(parser.parse(coin['updated_at']))) - tz
        expected_updated_at = int(datetime.timestamp(now))
        self.assertEqual(actual_updated_at, expected_updated_at)

    def test_create_wallet_successful(self):
        response = self.client.post('/wallets', data={'name': 'w3'})
        now = datetime.utcnow()
        self.assertEqual(response.status_code, 201)
        rows = list(db.engine.execute(f'SELECT * FROM wallets'))
        self.assertEqual(len(rows), 1)
        wallet = rows[0]
        self.assertEqual(wallet[0], 1)
        self.assertEqual(wallet[1], 'w3')

        actual_created_at = int(datetime.timestamp(parser.parse(wallet[2])))
        expected_created_at = int(datetime.timestamp(now))
        self.assertAlmostEqual(actual_created_at, expected_created_at, delta=3)

        actual_updated_at = int(datetime.timestamp(parser.parse(wallet[3])))
        expected_updated_at = int(datetime.timestamp(now))
        self.assertAlmostEqual(actual_updated_at, expected_updated_at, delta=3)

    def test_create_wallet_no_name_provided(self):
        response = self.client.post('/wallets')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json,
            {'error': 'no name provided'}
        )

    def test_create_wallet_duplicate_name(self):
        now = datetime.now()
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w11", "{now}", "{now}")')

        response = self.client.post('/wallets', data={'name': 'w11'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json,
            {'error': 'a wallet with the given name already exists'}
        )

    def test_edit_wallet_successful(self):
        now = datetime.now() + timedelta(hours=-5)
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w11", "{now}", "{now}")')

        response = self.client.put('/wallets/1', data={'name': 'w12'})

        self.assertEqual(response.status_code, 200)
        
        wallet = json.loads(response.get_data(as_text=True))
        self.assertEqual(wallet['id'], 1)
        self.assertEqual(wallet['name'], 'w12')
        self.assertEqual(float(wallet['balance']), 0)
        self.assertEqual(wallet['coins'], [])
        actual_created_at = int(datetime.timestamp(parser.parse(wallet['created_at']))) - tz
        expected_created_at = int(datetime.timestamp(now))
        self.assertEqual(actual_created_at, expected_created_at)

        actual_updated_at = int(datetime.timestamp(parser.parse(wallet['updated_at'])))
        expected_updated_at = int(datetime.timestamp(datetime.now()))
        self.assertAlmostEqual(actual_updated_at, expected_updated_at, delta=5)

    def test_edit_wallet_no_name_provided(self):
        now = datetime.now()
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w11", "{now}", "{now}")')

        response = self.client.put('/wallets/1')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json,
            {'error': 'no name provided'}
        )

    def test_edit_wallet_not_found(self):
        response = self.client.put('/wallets/1')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json,
            {'error': 'not found'}
        )

    def test_delete_wallet_successful(self):
        now = datetime.now() + timedelta(hours=-7)
        db.engine.execute(f'INSERT INTO wallets (name, created_at, updated_at) VALUES ("w11", "{now}", "{now}")')

        response = self.client.delete('/wallets/1')

        self.assertEqual(response.status_code, 200)
        
        wallet = json.loads(response.get_data(as_text=True))
        self.assertEqual(wallet['id'], 1)
        self.assertEqual(wallet['name'], 'w11')
        self.assertEqual(float(wallet['balance']), 0)
        self.assertEqual(wallet['coins'], [])
        actual_created_at = int(datetime.timestamp(parser.parse(wallet['created_at']))) - tz
        expected_created_at = int(datetime.timestamp(now))
        self.assertEqual(actual_created_at, expected_created_at)

        actual_updated_at = int(datetime.timestamp(parser.parse(wallet['updated_at']))) - tz
        expected_updated_at = int(datetime.timestamp(now))
        self.assertAlmostEqual(actual_updated_at, expected_updated_at, delta=5)

        rows = list(db.engine.execute(f'SELECT * FROM wallets'))
        self.assertEqual(len(rows), 0)

    def test_delete_wallet_not_found(self):
        response = self.client.delete('/wallets/1')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json,
            {'error': 'not found'}
        )

    def tearDown(self):
        for table in reversed(db.metadata.sorted_tables):
            db.engine.execute(table.delete())
        db.session.commit()
        db.session.remove()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        db.engine.execute('DROP TABLE alembic_version')
