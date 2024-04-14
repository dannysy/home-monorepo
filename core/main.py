from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def ws_example(websocket: WebSocket):
    print('SERVER:', websocket.headers)
    await websocket.accept()
    await websocket.send_json({'msg': 'First message'})
    await websocket.receive_json()
