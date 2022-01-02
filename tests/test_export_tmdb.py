import json
import pathlib

import httpx
import pytest
import respx
import typer
from typer.testing import CliRunner

from src.export_tmdb import export_popular_movies
from src.utils import read_json

export_tmdb_app = typer.Typer()
export_tmdb_app.command()(export_popular_movies)
runner = CliRunner()

POPULAR_MOVIES_PATH = (
    pathlib.Path(__file__)
    .parent.joinpath("fixtures")
    .joinpath("popular_movies_route_response.json")
)


@pytest.fixture
def tmdb_mock():
    with respx.mock(base_url="https://api.themoviedb.org") as router:
        mock_popular_movies_route(router)
        yield router


def mock_popular_movies_route(router: respx.MockRouter) -> respx.MockRouter:
    with open(POPULAR_MOVIES_PATH) as popular_movies_file:
        popular_movies_json = json.load(popular_movies_file)

    route = router.get("/3/movie/popular", name="popular_movies")
    route.return_value = httpx.Response(httpx.codes.OK, json=popular_movies_json)

    return router


def test_export_tmdb(tmdb_mock: respx.MockRouter, tmp_path: pathlib.Path):
    output_path = tmp_path / "tmdb.json"

    result = runner.invoke(
        export_tmdb_app,
        ["--output-path", output_path],
        env={"TMDB_API_KEY": "TMDB_API_KEY"},
    )
    assert result.exit_code == 0
    assert read_json(output_path)
