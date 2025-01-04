import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')

BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')


def test_create_wallet():
    url = f'{BASE_URL}/api/v1/wallets/'
    data = {
        "wallet_uuid": 'test',
        "initial_balance": 1000.0
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert 'uuid' in response.json().keys()
    assert 'initial_balance' in response.json().keys()
    assert response.json()['uuid'] == 'test' and response.json()['initial_balance'] == 1000.0


def test_deposit_to_wallet():
    wallet_uuid = "test"
    url = f'{BASE_URL}/api/v1/wallets/{wallet_uuid}/operation'
    data = {
        "operation_type": "DEPOSIT",
        "amount": 500.0
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "DEPOSIT successful"}


def test_withdraw_from_wallet():
    wallet_uuid = "test"
    url = f'{BASE_URL}/api/v1/wallets/{wallet_uuid}/operation'
    data = {
        "operation_type": "WITHDRAW",
        "amount": 250.0
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "WITHDRAW successful"}


def test_get_balance():
    wallet_uuid = "test"
    url = f'{BASE_URL}/api/v1/wallets/{wallet_uuid}'
    response = requests.get(url)
    assert response.status_code == 200
    assert 'balance' in response.json().keys()
    assert response.json()['balance'] == 1250.0


def test_delete_wallet():
    wallet_uuid = "test"
    url = f'{BASE_URL}/api/v1/wallets/{wallet_uuid}'
    response = requests.delete(url)
    assert response.status_code == 200
    assert response.json() == {"message": f"Wallet {wallet_uuid} deleted successfully"}
