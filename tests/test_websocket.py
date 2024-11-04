import pytest


def test_ws_send_get_message_private_chat(ws_client):
    with (
            ws_client.websocket_connect('/ws/1/2') as websocket1,
            ws_client.websocket_connect('/ws/2/1') as websocket2
        ):
        websocket1.send_text('hey')
        data1 = websocket1.receive_text()
        data2 = websocket2.receive_text()
    assert data1 == 'You say: hey'
    assert data2 == '1 says: hey'

def test_ws_send_get_message_common_chat(ws_client):
    with (
            ws_client.websocket_connect('/ws/1/common') as websocket1,
            ws_client.websocket_connect('/ws/2/common') as websocket2
        ):
        websocket1.send_text('hey')
        data1 = websocket1.receive_text()
        data2 = websocket2.receive_text()
    assert data1 == 'You say: hey'
    assert data2 == '1 says: hey'

def test_ws_left_chat_private_chat(ws_client):
    with ws_client.websocket_connect('/ws/1/2') as websocket1:
        with ws_client.websocket_connect('/ws/2/1') as websocket2:
            pass
        data1 = websocket1.receive_text()
    assert data1 == '2 left the chat'

def test_ws_left_chat_common_chat(ws_client):
    with ws_client.websocket_connect('/ws/1/common') as websocket1:
        with ws_client.websocket_connect('/ws/2/common') as websocket2:
            pass
        data1 = websocket1.receive_text()
    assert data1 == '2 left the chat'
