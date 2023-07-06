from dataclasses import dataclass
from collections import defaultdict
from typing import Optional

DICTIONARY_FILE_PATH = "cedict_ts.u8"

@dataclass
class Metadata:
    max_runs: int

@dataclass
class DictEntry:
    """
    Each individual item in a dictionary
    """
    simplified: str
    traditional: str
    pronunciation: str
    meanings: list[str]
    metadata: Optional[Metadata]

class Dictionary:
    def __init__(self, raw_dict_content: list[str], use_runs=False):
        self._dict: defaultdict[str, Optional[DictEntry]] = defaultdict(lambda: None)

        filtered_dict_contents = [line for line in raw_dict_content if not line.startswith("#")]
        self.initialise_dict(filtered_dict_contents)
        self._use_runs = use_runs
        if use_runs:
            self.add_metadata()

    @staticmethod
    def parse_into_entry(line: str) -> DictEntry:
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

        return DictEntry(simplified, traditional, pronunciation_cleaned, meanings, None)

    def initialise_dict(self, filtered_dict_contents: list[str]):
        for line in filtered_dict_contents:
            entry = Dictionary.parse_into_entry(line)
            self._dict[entry.simplified] = entry
    
    def add_metadata(self):
        for key, value in self._dict.items():
            if len(key) > 0 and (first_char := value.simplified[0]) in self._dict:
                first_char_entry = self.get_dictionary_word(first_char)
                first_char_entry.metadata = Metadata(max(
                    first_char_entry.metadata.max_runs if first_char_entry.metadata else 1, len(value.simplified)
                ))
    
    def get_contents(self) -> defaultdict[str, Optional[DictEntry]]:
        return self._dict

    def get_dictionary_word(self, word: str) -> Optional[DictEntry]:
        return self._dict[word]
    
    def define_sentence(self, sentence: str) -> list[DictEntry]:
        entries = []

        i = 0
        sentence_len = len(sentence)
        while (i < sentence_len):
            if (curr_word := self.get_dictionary_word(sentence[i])):
                if self._use_runs and (character_metadata := curr_word.metadata):
                    max_runs = character_metadata.max_runs
                    best_candidate = curr_word
                    j = 1

                    while ((end_range := i + j) <= sentence_len + 1 and j < max_runs):
                        if (new_candidate := self.get_dictionary_word(sentence[i:end_range])):
                            best_candidate = new_candidate
                        j += 1

                    entries.append(best_candidate)
                    i += len(best_candidate.simplified)
                else:
                    entries.append(curr_word)
                    i += 1
            else:
                i += 1
        return entries

def get_full_dict(use_runs=True) -> Dictionary:
    with open(DICTIONARY_FILE_PATH) as file:
        lines = [line.rstrip() for line in file]
        dict = Dictionary(lines, use_runs)

        return dict

if __name__ == "__main__":
    with open("cedict_ts.u8") as file:
        lines = [line.rstrip() for line in file]
        dict = Dictionary(lines, True)

        sentence = "新转来的也迟到"
        ls = dict.define_sentence(sentence)
        print(sentence)
        for l in ls:
            print(l.simplified, "(", l.pronunciation,")", ": ", "; ".join(l.meanings), sep="")
