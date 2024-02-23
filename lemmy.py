from dataclasses import dataclass
from typing import Optional, Literal

import requests

# Specify the Lemmy instance URL
lemmy_url = "https://lemmy.world"

#  Specify the number of top posts to retrieve
num_posts = 5

# Make a GET request to the Lemmy API to get the top posts
response = requests.get(
    f"{lemmy_url}/api/v3/post/list", params={"limit": num_posts, "sort": "Hot"}
)


Sort = Literal["Top", "Hot"]


@dataclass
class Post:
    name: str
    score: int
    community: str
    sort: Sort
    url: Optional[str] = None
    image: Optional[str] = None
    content: Optional[str] = None


def parse_post(post, sort):
    return Post(
        name=post["post"]["name"],
        score=post["counts"]["upvotes"] - post["counts"]["downvotes"],
        community=post["community"]["title"],
        sort=sort,
        url=post["post"].get("url"),
        image=post["post"].get("thumbnail_url"),
        content=post["post"].get("body"),
    )


def lemmy_hot_posts(url, limit=3):
    response = requests.get(
        f"{url}/api/v3/post/list", params={"limit": limit, "sort": "Hot"}
    )
    return [parse_post(post, "Hot") for post in response.json()["posts"]]


def lemmy_top_posts(url, limit=3):
    response = requests.get(
        f"{url}/api/v3/post/list", params={"limit": limit, "sort": "TopDay"}
    )
    return [parse_post(post, "Top") for post in response.json()["posts"]]


@dataclass
class Posts:
    top: list[Post]
    hot: list[Post]

    def json(self):
        return dict(top=self.top, hot=self.hot)


def get_top_posts_and_hot_posts(*, url=lemmy_url, limit=3):
    top_posts = lemmy_top_posts(url, limit)
    hot_posts = lemmy_hot_posts(url, limit)
    return Posts(top=top_posts, hot=hot_posts)
