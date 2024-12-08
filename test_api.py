import requests
from flask_jwt_extended import get_jwt

ENDPOINT = "http://127.0.0.1:5000"


def test_can_call_endpoint():
    call_endpoint_response = requests.get(ENDPOINT)
    assert call_endpoint_response.status_code == 200


def test_can_user_log_in():
    payload = create_user_payload()
    user_log_in_response = requests.post(ENDPOINT, json=payload)
    assert user_log_in_response.status_code == 200

    data_user_log_in_response = user_log_in_response.json()
    assert data_user_log_in_response["access_token"] != ""
    
def test_can_admin_log_in():
    payload = create_admin_payload()
    admin_log_in_response = requests.post(ENDPOINT, json=payload)
    assert admin_log_in_response.status_code == 200

    data_admin_log_in_response = admin_log_in_response.json()
    assert data_admin_log_in_response["access_token"] != ""

#def test_user_is_not_admin():
    


def create_user_payload():
    return {
        "username": "usuario1",
        "password": "1234"
    }

def create_admin_payload():
    return {
        "username": "admin",
        "password": "admin"
    }