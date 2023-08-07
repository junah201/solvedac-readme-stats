from dataclasses import dataclass
from typing import Optional
import json
import requests
from bs4 import BeautifulSoup


@dataclass
class UserData:
    username: str
    arena_tier: int
    arena_rating: int
    arena_max_tier: int
    arena_max_rating: int
    arena_match_count: int
    arena_recent_performance: Optional[int] = None


def get_user_data(username: str) -> Optional[UserData]:
    """Get user data from solved.ac"""
    url = f"https://solved.ac/api/v3/user/show?handle={username}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        user = UserData(
            username=data["handle"],
            arena_tier=data["arenaTier"],
            arena_rating=data["arenaRating"],
            arena_max_tier=data["arenaMaxTier"],
            arena_max_rating=data["arenaMaxRating"],
            arena_match_count=data["arenaCompetedRoundCount"],
        )
    except KeyError:
        return None

    user.arena_recent_performance = get_recent_performance(username)

    return user


def get_recent_performance(username: str) -> Optional[int]:
    """Get recent performance from solved.ac
    Since it is directly crawled from "https://solved.ac/profile/{username}/arena",
    if the API is exposed later, it must be changed.
    """
    url = f"https://solved.ac/profile/{username}/arena"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    row_data = soup.select_one("script#__NEXT_DATA__")

    if not row_data:
        return None

    data = json.loads(row_data.text)

    contests_info = data["props"]["pageProps"]["contests"]
    contests_info = data.get("props", {}).get(
        "pageProps", {}).get("contests", None)

    if not contests_info:
        return None

    if contests_info["count"] == 0:
        return None

    recent_performance = contests_info["items"][0]["performance"]

    return int(recent_performance)


tier_table = {
    0: "Unrated",
    1: "C",
    2: "C+",
    3: "B",
    4: "B+",
    5: "A",
    6: "A+",
    7: "S",
    8: "S+",
    9: "SS",
    10: "SS+",
    11: "SSS",
    12: "SSS+",
}


def arena_tier_to_text(tier: int) -> str:
    """Convert arena tier to text"""

    return tier_table.get(tier, None)


@dataclass
class TierInfo:
    tier: str
    min_rating: int
    max_rating: int
    color: str


tier_info_table = {
    "Unrated": TierInfo("Unrated", 0, 1, "#C5C5C5"),
    "C": TierInfo("C", 0, 400, "#69513E"),
    "C+": TierInfo("C+", 400, 800, "#69513E"),
    "B": TierInfo("B", 800, 1000, "#36437E"),
    "B+": TierInfo("B+", 1000, 1200, "#36437E"),
    "A": TierInfo("A", 1200, 1400, "#E8A22F"),
    "A+": TierInfo("A+", 1400, 1600, "#E8A22F"),
    "S": TierInfo("S", 1600, 1800, "#86DA6E"),
    "S+": TierInfo("S+", 1800, 2000, "#86DA6E"),
    "SS": TierInfo("SS", 2000, 2200, "#619FE1"),
    "SS+": TierInfo("SS+", 2200, 2400, "#619FE1"),
    "SSS": TierInfo("SSS", 2400, 2600, "#DB1B3C"),
    "SSS+": TierInfo("SSS+", 2600, 3000, "#DB1B3C"),
}


def get_tier_info(tier: str) -> TierInfo:
    """Get tier info"""

    return tier_info_table.get(tier, None)


def performance_to_tier(performance: int) -> TierInfo:
    """Get performance to tier info"""

    for tier in tier_info_table.values():
        if tier.min_rating <= performance <= tier.max_rating:
            return tier

    return None
