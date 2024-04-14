import time

import docker
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport

from core.data_base.init import innit_db
from core.main import app
from data_base.database import get_engine, get_session
from data_base.settings import get_config
from data_base.utils import drop_database, truncate_db


@pytest.fixture(scope="session")
async def ws_test_client():
    # https://github.com/PacktPublishing/Building-Data-Science-Applications-with-FastAPI-Second-Edition/blob/917a8030e3df10378d26be03465c1560c9f8e3d9/tests/conftest.py#L7
    async with AsyncClient(base_url='http://test', transport=ASGIWebSocketTransport(app)) as client:
        yield {'url': 'http://test/ws', 'client': client}


@pytest.fixture(scope="session")
def postgres_docker_container():
    if not get_config().postgresql_image:
        yield None
        return

    dsn = get_config().dsn

    container = docker.from_env().containers.run(
        image=get_config().postgresql_image,
        auto_remove=True,
        environment=dict(
            POSTGRESQL_USERNAME=dsn.hosts()[0]["username"],
            POSTGRESQL_PASSWORD=dsn.hosts()[0]["password"],
            POSTGRESQL_DATABASE=dsn.path[1:]
        ),
        ports={"5432/tcp": dsn.hosts()[0]["port"]},
        healthcheck={
            "test": ["CMD-SHELL", "pg_isready -U $POSTGRESQL_USERNAME -d $POSTGRESQL_DATABASE"],
            "interval": 500_000_000,
            "retries": 10
        },
        detach=True,
        remove=True,
    )

    while docker.APIClient().inspect_container(container.name)["State"]["Health"]["Status"] != "healthy":
        time.sleep(2)

    try:
        yield container
    finally:
        container.stop()


@pytest_asyncio.fixture(scope="session")
async def init_database(postgres_docker_container):
    db_url = await innit_db()
    try:
        yield
    finally:
        await drop_database(db_url)


@pytest_asyncio.fixture(scope="function")
async def db_session(init_database):
    await truncate_db(get_engine())

    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    # https://github.com/sqlalchemy/sqlalchemy/issues/5811
    # nested = await connection.begin_nested()
    # session = get_session_maker()(bind=connection, autoflush=False, autocommit=False)
    session = get_session()
    def conftest_get_session():
        try:
            yield session
        finally:
            return

    app.dependency_overrides[get_session] = conftest_get_session
    try:
        yield session
    finally:
        await session.aclose()
        app.dependency_overrides = {}
