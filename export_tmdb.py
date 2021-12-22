import json
from pathlib import Path
from typing import Optional

import typer
import httpx


def export_popular_movies(
    api_key: str = typer.Argument(..., envvar="TMDB_API_KEY"),
    from_page: int = typer.Option(1, min=1, max=1000),
    to_page: int = typer.Option(1, min=1, max=1000),
    language: str = typer.Option(
        "en-US",
        help="ISO 639-1 value to display translated data for the fields that support it.",
    ),
    region: Optional[str] = typer.Option(
        None, help="ISO 3166-1 code to filter release dates. Must be uppercase."
    ),
    output_path: Path = typer.Option(
        "tmdb.json",
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
    ),
):
    params = {
        "api_key": api_key,
        "language": language,
        "region": region,
    }

    movies = []
    for page in range(from_page, to_page + 1):
        params.update({"page": str(page)})
        response = httpx.get(
            "https://api.themoviedb.org/3/movie/popular", params=params
        )
        movies_page = response.json()["results"]
        movies += movies_page

    with open(output_path, mode="w") as output_file:
        json.dump(movies, output_file, indent=4, sort_keys=True, ensure_ascii=False)


if __name__ == "__main__":
    typer.run(export_popular_movies)
