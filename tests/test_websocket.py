import pytest


def test_ws_send_get_message(ws_client):
    with (
            ws_client.websocket_connect('/ws/1') as websocket1,
            ws_client.websocket_connect('/ws/2') as websocket2
        ):
        websocket1.send_text('hey')
        data1 = websocket1.receive_text()
        data2 = websocket2.receive_text()
    assert data1 == 'You say: hey'
    assert data2 == 'Client #1 says: hey'

def test_ws_left_chat(ws_client):
    with ws_client.websocket_connect('/ws/1') as websocket1:
        with ws_client.websocket_connect('/ws/2') as websocket2:
            pass
        data1 = websocket1.receive_text()
    assert data1 == 'Client #2 left the chat'
