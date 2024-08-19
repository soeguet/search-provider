#!/usr/bin/env python3

import os
import subprocess
from typing import Tuple
import urllib.parse
import re


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
        
        git_username = os.getenv("github_username", default="")
        
        if query == "git .":
            return "url", f"https://github.com/{git_username}"

        elif query == "git":
            # todo
            return "url", f"https://github.com/{git_username}"

        else:
            if '/' in query:
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


if __name__ == "__main__":

    query = get_query()
    url = main_function(query)

    if url[0] == "url":
        open_url(url[1])
 #   elif url[0] == "git":
  #      handle_git(url[1])
