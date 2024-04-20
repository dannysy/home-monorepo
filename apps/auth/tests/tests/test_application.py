import pytest

from sqlalchemy import select
from core.const import AppType
from core.units.application.model import AppModel
from core.units.application.schema import ReceivedAppReg, SendAppReg, ReceivedAppUpd


async def test_register_app(test_client, db_session):
    send_msg = ReceivedAppReg(
        app_type=AppType.customer,
        device_info="android",
        app_version=1
    )
    response = await test_client.post("/app/register", content=send_msg.json())
    assert response.status_code == 200
    response = SendAppReg.model_validate_json(response.content)
    app = (await db_session.execute(select(AppModel).where(AppModel.id == response.id))).scalar()
    assert type(app) is AppModel


@pytest.fixture
async def app(db_session) -> AppModel:
    obj = AppModel(
        app_type=AppType.customer,
        app_version=1,
        device_info='android'
    )
    db_session.add(obj)
    await db_session.commit()
    return obj


async def test_update_app(test_client, db_session, app: AppModel):
    send_msg = ReceivedAppUpd(
        sender_app_id=app.id,
        device_info="ios",
        app_version=2
    )
    response = await test_client.post("/app/update", content=send_msg.json())
    assert response.status_code == 200
    app = (await db_session.execute(select(AppModel).where(AppModel.id == app.id))).scalar()
    assert app.device_info == send_msg.device_info
    assert app.app_version == send_msg.app_version


async def test_not_exist_app(test_client, db_session):
    # TODO: не получается со стороны сервера вернуть ошибку клиенту
    send_msg = ReceivedAppUpd(
        sender_app_id=1,
        device_info="ios",
        app_version=2
    )
    response = await test_client.post("/app/update", j=send_msg.json())
    assert response.status_code == 400
    # app = (await db_session.execute(select(AppModel).where(AppModel.id == app.id))).scalar()
    # assert app.device_info == send_msg.device_info
    # assert app.app_version == send_msg.app_version
