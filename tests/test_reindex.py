import pathlib
from urllib.parse import urljoin

import httpx
import typer
from dynaconf import settings
from typer.testing import CliRunner

from src.reindex import reindex

reindex_app = typer.Typer()
reindex_app.command()(reindex)
runner = CliRunner()

EXPORTED_MOVIES_PATH = (
    pathlib.Path(__file__).parent.joinpath("fixtures").joinpath("exported_movies.json")
)


def test_reindex():
    result = runner.invoke(reindex_app, [str(EXPORTED_MOVIES_PATH)])
    assert result.exit_code == 0, result.stdout

    index_url = urljoin(settings.ELASTICSEARCH_URL, settings.ELASTICSEARCH_INDEX_NAME)
    httpx.post(urljoin(index_url, "_refresh"))

    response = httpx.get(
        urljoin(index_url, f"_cat/indices/{settings.ELASTICSEARCH_INDEX_NAME}"),
        params={"format": "json"},
    )
    assert response.json()[0]["docs.count"], response.text
