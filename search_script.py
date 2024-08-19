#!/usr/bin/env python3

import os
import subprocess
from typing import Tuple
import urllib.parse
import re
import requests

git_username = os.getenv("GITHUB_USERNAME", default="")


def get_query() -> str:
    result = subprocess.run(
        [
            "zenity",
            "--entry",
            "--title=Search",
            "--text=Enter your search query:",
            "--width=600",
            "--height=100",
            "--entry-text=",
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def open_url(url) -> None:
    subprocess.run(["xdg-open", url])


def is_url(s: str) -> re.Match[str] | None:
    url_pattern = re.compile(
        r"^(https?://)" r"(([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,})" r"(:\d+)?(/.*)?$",
        re.IGNORECASE,
    )
    return url_pattern.match(s)


def is_short_url(url: str) -> bool:
    if not is_url(url):
        domain_pattern = re.compile(r"^[\w-]+\.[a-zA-Z]{2,}$", re.IGNORECASE)
        match = domain_pattern.match(url)

        if match:
            return True

    return False


def main_function(query: str) -> Tuple[str, str]:

    if query == "":
        return "", ""

    ## prefix: url
    if query.startswith("url "):
        return "url", query[4:].strip()

    ## prefix: gg
    elif query.startswith("gg "):
        search_term = query[3:]
        return (
            "url",
            f"https://www.google.com/search?q={urllib.parse.quote(search_term)}",
        )

    ## prefix: gpt
    elif query.startswith("gpt "):
        search_term = query[4:]
        return "url", f"https://chatgpt.com/?q={urllib.parse.quote(search_term)}"

    ## prefix: git
    elif query.startswith("git"):

        if query == "git ." or query == "git":
            return "url", f"https://github.com/{git_username}"

        if query == "git?":
            return "git", ""

        else:
            if "/" in query:
                return "url", f"https://github.com/{query[4:]}"
            else:
                return "url", f"https://github.com/{git_username}/{query[4:]}"

    ## URL check
    # full url
    elif is_url(query):
        return "url", query
    # short url
    elif is_short_url(query):
        return "url", f"https://{query}"

    ## check for short URL
    ## else pass to google search
    else:
        return "url", f"https://www.google.com/search?q={urllib.parse.quote(query)}"


def handle_git() -> list[tuple[str, str]]:
    url: str = f"https://api.github.com/users/{git_username}/repos"
    response: requests.Response = requests.get(url)
    repos: list[dict] = response.json()

    repo_info: list[tuple[str, str]] = [
        (repo["full_name"], repo["html_url"]) for repo in repos
    ]

    return repo_info


def prepare_git_zenity_args(repo_info) -> list[str]:
    zenity_args = [
        "zenity",
        "--list",
        "--column=Repository",
        "--column=URL",
        "--width=600",
        "--height=400",
        "--hide-column=URL",
        "--separator=|",
    ]
    for repo in repo_info:
        zenity_args.extend([repo[0], repo[1]])

    return zenity_args


def call_git_zenity(repo_info, zenity_args: list[str]):
    try:
        selected_repo = subprocess.check_output(zenity_args, text=True).strip()

        if selected_repo:
            url = next(
                (repo[1] for repo in repo_info if repo[0] == selected_repo), None
            )

            if url:
                subprocess.run(["xdg-open", url])

    except subprocess.CalledProcessError as e:
        ## simply return
        return


if __name__ == "__main__":

    query = get_query()
    url = main_function(query)

    if url[0] == "url":
        open_url(url[1])

    elif url[0] == "git":
        github_response = handle_git()
        zenity_args = prepare_git_zenity_args(github_response)
        call_git_zenity(github_response, zenity_args)
