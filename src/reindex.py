import json
from pathlib import Path
from urllib.parse import urljoin

import httpx
import typer
from dynaconf import settings

from src.utils import read_json

readable_file_args = {
    "exists": True,
    "file_okay": True,
    "dir_okay": False,
    "writable": False,
    "readable": True,
    "resolve_path": True,
}


def reindex(
    documents_path: Path = typer.Argument(
        ..., help="Path to json documents to reindex", **readable_file_args
    ),
    analysis_path: Path = typer.Option(None, **readable_file_args),
    mappings_path: Path = typer.Option(None, **readable_file_args),
):
    documents = read_json(documents_path)
    analysis_settings = read_json(analysis_path) if analysis_path else {}
    mappings_settings = read_json(mappings_path) if mappings_path else {}

    index_settings = construct_index_settings(analysis_settings, mappings_settings)
    index_url = urljoin(settings.ELASTICSEARCH_URL, settings.ELASTICSEARCH_INDEX_NAME)

    httpx.delete(index_url)
    httpx.put(index_url, json=index_settings)

    bulk_url = urljoin(settings.ELASTICSEARCH_URL, "_bulk")
    bulk_request_content = construct_bulk_request_content(documents)
    httpx.post(
        bulk_url,
        content=bulk_request_content,
        headers={"content-type": "application/json"},
    )


def construct_index_settings(analysis_settings: dict, mappings_settings: dict) -> dict:
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "index": {
                "analysis": analysis_settings,
            },
        }
    }
    if mappings_settings:
        index_settings["mappings"] = mappings_settings
    return index_settings


def construct_bulk_request_content(documents: list) -> bytes:
    bulk_request_data = []
    for document in documents:
        add_command = {
            "index": {
                "_index": settings.ELASTICSEARCH_INDEX_NAME,
                "_type": "movie",
                "_id": document["id"],
            }
        }
        bulk_request_data.append(json.dumps(add_command))
        bulk_request_data.append(json.dumps(document))
    return ("\n".join(bulk_request_data) + "\n").encode("utf-8")


if __name__ == "__main__":
    typer.run(reindex)
