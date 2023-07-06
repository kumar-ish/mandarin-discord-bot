from collections import defaultdict
from typing import Optional
from dataclasses import dataclass
from random import random
import datetime

CHENGYU_PATH = "data/chengyu.tsv"


def ordinal(num) -> str:
    xd = defaultdict(
        lambda: "th",
        {
            0: "th",
            1: "st",
            2: "nd",
            3: "rd",
        },
    )
    return str(num) + xd[num]


@dataclass
class Chengyu:
    rank: str
    idiom: str
    hsk: Optional[str]


class ChengyuGenerator:
    def __init__(
        self,
        raw_chengyus: list[str],
        start_date: datetime.datetime = datetime.datetime.now(),
        days_limit: int = 200,
        desired_chengyus: int = 2,
    ):
        self._chengyus = list(map(ChengyuGenerator.parse_chengyu, raw_chengyus))
        self._start_date = start_date
        assert days_limit <= len(raw_chengyus) / 2
        self._days_limit = days_limit
        self._num_chengyus = desired_chengyus

    @staticmethod
    def parse_chengyu(raw_chengyu: str) -> Chengyu:
        # Format is: rank, idiom, frequency (in their dataset), (Optional) HSK level
        # We know the rank from the position in index
        raw_rank, idiom, _, hsk = raw_chengyu.split("\t")
        rank = raw_rank[:-1]  # raw rank has trailing semicolon
        return Chengyu(rank, idiom, hsk if hsk else None)

    def set_num_chengyus(self, num_chengyus: int) -> bool:
        if 1 <= num_chengyus <= 5:
            self._num_chengyus = num_chengyus
            return True
        else:
            return False

    def todays_chengyus(self) -> tuple[str, list[Chengyu]]:
        # Returns one Chengyus from the start of the list if within date range; and remaining desired more
        today = datetime.datetime.now()
        from_start = (today - self._start_date).days

        ret = []

        if from_start < self._days_limit:
            msg = (
                f"We're on the {ordinal(from_start)} day of Chengyus; here is rank #{from_start + 1} of the Chengyu list"
                f"{(' & ' + str(remaining) + ' more') if (remaining := self._num_chengyus - 1) > 0 else ''}:"
            )
            ret.append(self._chengyus[from_start])
        else:
            msg = f"Here's {self._num_chengyus} Chengyus!"

        while len(ret) < self._num_chengyus:
            rng = random()
            index = int(rng * (len(self._chengyus) - self._days_limit))
            ret.append(self._chengyus[self._days_limit + index])

        return (msg, ret)


def get_chengyu_generator() -> ChengyuGenerator:
    with open(CHENGYU_PATH) as f:
        lines = [line.rstrip("\n") for line in f]
        lines = lines[1:]
        c = ChengyuGenerator(lines)

    return c


if __name__ == "__main__":
    pass
