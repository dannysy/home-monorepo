import time

import docker
import pytest
import pytest_asyncio
from httpx import AsyncClient

from core.data_base.database import get_engine, get_session, get_session_maker
from core.data_base.settings import get_config
from core.data_base.utils import innit_db, drop_database, truncate_db
from core.main import app


@pytest.fixture(scope="session")
async def test_client():
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


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
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    await truncate_db(get_engine())
    session_maker = get_session_maker()
    session = session_maker(autoflush=False, autocommit=False)

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
