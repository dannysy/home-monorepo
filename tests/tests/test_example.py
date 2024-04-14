from httpx_ws import aconnect_ws


async def test_app(ws_test_client):
    async with aconnect_ws(**ws_test_client) as websocket:
        msg = await websocket.receive_json()
        print('CLIENT:', msg)
        await websocket.close()
