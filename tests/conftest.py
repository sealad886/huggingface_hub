import abc
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ContextManager, Optional

import pytest

from _pytest.fixtures import SubRequest
from huggingface_hub.hf_api import HfApi

from .testing_constants import ENDPOINT_STAGING, TOKEN, USER
from .testing_utils import repo_name


@pytest.fixture
def fx_repo_id(request: SubRequest) -> None:
    # TODO: docstring
    request.cls.repo_name = repo_name(prefix=_get_test_name(request)[-50:])
    request.cls.repo_id = f"{USER}/{request.cls.repo_name}"


@pytest.fixture
def fx_cache_dir(request: SubRequest, fx_repo_id: None) -> None:
    # TODO: docstring
    with TemporaryDirectory(prefix=_get_test_name(request)) as cache_dir:
        repo_cache_dir = Path(cache_dir) / request.cls.repo_name
        repo_cache_dir.mkdir(parents=True, exist_ok=True)
        request.cls.cache_dir = repo_cache_dir
        request.cls.cache_dir_str = str(repo_cache_dir)
        yield


@pytest.fixture
def fx_api_disconnected(request: SubRequest) -> None:
    # TODO: docstring and test
    request.cls._api = HfApi(endpoint=ENDPOINT_STAGING)


@pytest.fixture
def fx_api_connected(request: SubRequest) -> None:
    # TODO: docstring and test
    request.cls._api = HfApi(endpoint=ENDPOINT_STAGING)
    request.cls._token = TOKEN
    request.cls._api.set_access_token(TOKEN)


@pytest.fixture
def fx_create_tmp_repo(request: SubRequest, fx_api_connected: None, fx_repo_id: None):
    # TODO: docstring
    """Return contextmanager to handle tmp repo creation/deletion."""

    @contextmanager
    def _create_tmp_repo(cls, repo_type: Optional[str] = None) -> None:
        request.cls._api.create_repo(
            token=request.cls._token,
            repo_id=request.cls.repo_id,
            repo_type=repo_type,
        )
        yield request.cls.repo_id
        request.cls._api.delete_repo(
            token=request.cls._token,
            repo_id=request.cls.repo_id,
            repo_type=repo_type,
        )

    request.cls.create_tmp_repo = _create_tmp_repo


@pytest.mark.usefixtures("fx_repo_id")
class RepoIdFixture(abc.ABC):
    # TODO: docstring and test
    repo_name: str
    repo_id: str


@pytest.mark.usefixtures("fx_cache_dir")
class CacheDirFixture(abc.ABC):
    # TODO: docstring and test
    cache_dir: Path
    cache_dir_str: str


@pytest.mark.usefixtures("fx_create_tmp_repo")
class CreateTmpRepoFixture(abc.ABC):
    # TODO: docstring and test
    create_tmp_repo: ContextManager


def _get_test_name(request: SubRequest) -> str:
    """Return the test name from the pytest Request object.

    Example: in `test_cache_dir_works` -> returns `cache_dir_works`.
    """
    name = request.function.__name__
    if name.startswith("test_"):
        name = name[5:]
    return name