#!/usr/bin/env python
from deepdive import *
import random
from collections import namedtuple

BornPlaceLabel = namedtuple('BornPlaceLabel', 'person_id, place_id, label, type')

@tsv_extractor
@returns(lambda
        person_id   = "text",
        place_id   = "text",
        label   = "int",
        rule_id = "text",
    :[])
# heuristic rules for finding positive/negative examples of born_in relationship mentions
def supervise(
        person_id="text", person_begin="int", person_end="int",
        place_id="text", place_begin="int", place_end="int",
        doc_id="text", sentence_index="int", sentence_text="text",
        tokens="text[]", lemmas="text[]", pos_tags="text[]", ner_tags="text[]",
        dep_types="text[]", dep_token_indexes="int[]",
    ):

    # Constants
    BORN = frozenset(["bear"])
    PROPOSITION = frozenset(["in"])
    NEGATIVE = frozenset(["graduate", "live", "play", "die", "attend", "move"])#complete more
    MAX_DIST = 30

    # Common data objects
    person_end_idx = min(person_end, place_end)
    place_start_idx = max(person_begin, place_begin)
    place_end_idx = max(person_end,place_end)
    intermediate_lemmas = lemmas[person_end_idx+1:place_start_idx]
    intermediate_ner_tags = ner_tags[person_end_idx+1:place_start_idx]
    tail_lemmas = lemmas[place_end_idx+1:]
    born_in = BornPlaceLabel(person_id=person_id, place_id=place_id, label=None, type=None)

    # Rule: Candidates that are too far apart
    if len(intermediate_lemmas) > MAX_DIST:
        yield born_in._replace(label=-1, type='neg:far_apart')

    # Rule: Candidates that have a third person in between
    if 'LOCATION' in intermediate_ner_tags:
        yield born_in._replace(label=-1, type='neg:another_place_between')

    # Rule: Sentences that contain "born in" in between
#    if len(BORN.intersection(intermediate_lemmas) and PROPOSITION.intersection(intermediate_lemmas)) > 0:
#        yield born_in._replace(label=1, type='pos:born_in_between')

    # Rule: Sentences that contain "born" in between
    #         (<P1>)([ A-Za-z]+)(wife|husband)([ A-Za-z]+)(<P2>)
    if len(BORN.intersection(intermediate_lemmas)) > 0:
        yield born_in._replace(label=2, type='pos:born_between')

    # Rule: Sentences that contain familial relations:
    #         (<P1>)([ A-Za-z]+)(brother|stster|father|mother)([ A-Za-z]+)(<P2>)
    if len(NEGATIVE.intersection(intermediate_lemmas)) > 0:
        yield born_in._replace(label=-2, type='neg:other_verbs_between')
