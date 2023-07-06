from dataclasses import dataclass
from collections import defaultdict
from typing import Optional

DICTIONARY_FILE_PATH = "cedict_ts.u8"


@dataclass
class Metadata:
    max_runs: int


@dataclass
class WordEntry:
    """Each word"""

    simplified: str
    traditional: str


@dataclass
class Interpretation:
    """Each possible interpretation of a word"""

    pronunciation: str
    meanings: list[str]


@dataclass
class DictEntry:
    """Each individual listing in a dictionary (including the word)"""

    word: WordEntry
    interpretations: list[Interpretation]
    metadata: Optional[Metadata]


class Dictionary:
    def __init__(self, raw_dict_content: list[str], use_runs=False):
        self._dict: defaultdict[str, Optional[DictEntry]] = defaultdict(lambda: None)

        filtered_dict_contents = [
            line for line in raw_dict_content if not line.startswith("#")
        ]
        self.initialise_dict(filtered_dict_contents)
        self._use_runs = use_runs
        if use_runs:
            self.add_metadata()

    @staticmethod
    def parse_line(line: str) -> tuple[WordEntry, DictEntry]:
        ## Format of lines is
        # Traditional Simplified [pin1 yin1] /gloss; gloss; .../gloss; gloss; .../

        # e.g.
        # 皮實 皮实 [pi2 shi5] /(of things) durable/(of people) sturdy; tough/
        traditional, line = line.split(" ", 1)
        simplified, line = line.split(" ", 1)

        # Raw: [...]; cleaned: ...
        pronunciation_raw, line = line.split(" /", 1)
        pronunciation_cleaned = pronunciation_raw[1:-1]

        # `line`` is currently in format: meaning1/meaning2/.../
        # (trailing / at the end)
        meanings = line.split("/")[:-1]

        return (
            WordEntry(simplified, traditional),
            Interpretation(pronunciation_cleaned, meanings),
        )

    def initialise_dict(self, filtered_dict_contents: list[str]):
        for line in filtered_dict_contents:
            word_entry, interpretation = Dictionary.parse_line(line)
            if dict_entry := self._dict[word_entry.simplified]:
                dict_entry.interpretations.append(interpretation)
            else:
                self._dict[word_entry.simplified] = DictEntry(
                    word_entry, [interpretation], None
                )

    def add_metadata(self):
        for key, value in self._dict.items():
            if len(key) > 0 and (first_char := value.word.simplified[0]) in self._dict:
                first_char_entry = self.get_dictionary_word(first_char)
                first_char_entry.metadata = Metadata(
                    max(
                        first_char_entry.metadata.max_runs
                        if first_char_entry.metadata
                        else 1,
                        len(value.word.simplified),
                    )
                )

    def get_contents(self) -> defaultdict[str, Optional[DictEntry]]:
        return self._dict

    def get_dictionary_word(self, word: str) -> Optional[DictEntry]:
        return self._dict[word]

    def define_sentence(self, sentence: str) -> list[DictEntry]:
        entries = []

        i = 0
        sentence_len = len(sentence)
        while i < sentence_len:
            if curr_word := self.get_dictionary_word(sentence[i]):
                if self._use_runs and (character_metadata := curr_word.metadata):
                    max_runs = character_metadata.max_runs
                    best_candidate = curr_word
                    j = 1

                    while (end_range := i + j) <= sentence_len + 1 and j < max_runs:
                        if new_candidate := self.get_dictionary_word(
                            sentence[i:end_range]
                        ):
                            best_candidate = new_candidate
                        j += 1

                    entries.append(best_candidate)
                    i += len(best_candidate.word.simplified)
                else:
                    entries.append(curr_word)
                    i += 1
            else:
                i += 1
        return entries


def stringify_sentence(definitions: list[DictEntry]) -> Optional[str]:
    if not definitions:
        return None
    NEW_LINE = "\n"
    TAB = "\t"

    WORDS_SEPARATOR = NEW_LINE + "---" + NEW_LINE
    LEADING_WHITESPACE_DEFINITION = NEW_LINE + TAB
    LEADING_WHITESPACE_INTERPRETATION = NEW_LINE + TAB + TAB

    interpretation_stringify = (
        lambda y: y.pronunciation
        + LEADING_WHITESPACE_INTERPRETATION
        + LEADING_WHITESPACE_INTERPRETATION.join(y.meanings)
    )
    definition_stringify = (
        lambda x: x.word.simplified
        + ": "
        + LEADING_WHITESPACE_DEFINITION
        + LEADING_WHITESPACE_DEFINITION.join(
            map(
                interpretation_stringify,
                x.interpretations,
            )
        )
    )
    return WORDS_SEPARATOR.join(
        map(
            definition_stringify,
            definitions,
        )
    )


def get_full_dict(use_runs=True) -> Dictionary:
    with open(DICTIONARY_FILE_PATH) as file:
        lines = [line.rstrip() for line in file]
        dict = Dictionary(lines, use_runs)

        return dict


if __name__ == "__main__":
    pass
