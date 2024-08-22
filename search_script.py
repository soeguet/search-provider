#!/usr/bin/env python3

import os
import re
import subprocess
import urllib.parse
from typing import Tuple

import requests

git_username = os.getenv("GITHUB_USERNAME", default="")


def get_query() -> str:
    result = subprocess.run(
        ["zenity", "--entry", "--title=Search", "--text=Enter your search query:", "--width=600", "--height=100",
         "--entry-text=", ], capture_output=True, text=True, )
    return result.stdout.strip()


def open_url(passed_url: str) -> None:
    subprocess.run(["xdg-open", passed_url])


def is_url(s: str) -> re.Match[str] | None:
    url_pattern = re.compile(r"^(https?://)" r"(([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,})" r"(:\d+)?(/.*)?$", re.IGNORECASE, )
    return url_pattern.match(s)


def is_short_url(passed_url: str) -> bool:
    if not is_url(passed_url):
        domain_pattern = re.compile(r"^[\w-]+\.[a-zA-Z]{2,}$", re.IGNORECASE)
        match = domain_pattern.match(passed_url)

        if match:
            return True

    return False


def main_function(passed_query: str) -> Tuple[str, str]:
    if passed_query == "":
        return "", ""

    ## prefix: url
    if passed_query.startswith("url "):
        return "url", passed_query[4:].strip()

    ## prefix: gg
    elif passed_query.startswith("gg "):
        search_term = passed_query[3:]
        return "url", f"https://www.google.com/search?q={urllib.parse.quote(search_term)}",

    elif passed_query == "gpt":
        return "url", "https://chatgpt.com/?model=gpt-4o"

    ## prefix: gpt
    elif passed_query.startswith("gpt "):
        search_term = passed_query[4:]
        return "url", f"https://chatgpt.com/?q={urllib.parse.quote(search_term)}"

    ## prefix: git
    elif passed_query == "git" or passed_query == "git .":
        return "url", f"https://github.com/{git_username}"


    elif passed_query == "git?":
        return "git", ""

    elif passed_query.startswith("git "):
        if "/" in passed_query:
            return "url", f"https://github.com/{passed_query[4:]}"
        else:
            return "url", f"https://github.com/{git_username}/{passed_query[4:]}"

    ## URL check
    # full url
    elif is_url(passed_query):
        return "url", passed_query
    # short url
    elif is_short_url(passed_query):
        return "url", f"https://{passed_query}"

    ## check for short URL
    ## else pass to google search
    else:
        return "url", f"https://www.google.com/search?q={urllib.parse.quote(passed_query)}"


def handle_git() -> list[tuple[str, str]]:
    github_repos_url: str = f"https://api.github.com/users/{git_username}/repos"
    response: requests.Response = requests.get(github_repos_url)
    repos: list[dict] = response.json()

    repo_info: list[tuple[str, str]] = [(repo["full_name"], repo["html_url"]) for repo in repos]

    return repo_info


def prepare_git_zenity_args(repo_info) -> list[str]:
    zenity_command_w_args = ["zenity", "--list", "--column=Repository", "--column=URL", "--width=600", "--height=400",
                             "--hide-column=URL", "--separator=|", ]
    for repo in repo_info:
        zenity_command_w_args.extend([repo[0], repo[1]])

    return zenity_command_w_args


def call_git_zenity(repo_info, zenity_command_w_args) -> None:
    try:
        selected_repo = subprocess.check_output(zenity_command_w_args, text=True).strip()

        if selected_repo:
            command = next((repo[1] for repo in repo_info if repo[0] == selected_repo), None)

            if command:
                subprocess.run(["xdg-open", command])

    except subprocess.CalledProcessError as e:
        ## simply return
        print(e)
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