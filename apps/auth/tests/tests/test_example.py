

async def test_app(test_client, db_session):
    response = await test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {'kek': 1}


