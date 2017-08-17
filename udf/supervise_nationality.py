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
    VERB = frozenset(["be"])
    VERB_POS = frozenset(["VB", "VBP", "VBZ", "VBD", "VBG", "VBN"])
    MAX_DIST = 20

    # Common data objects
    person_end_idx = min(person_end, place_end)
    place_start_idx = max(person_begin, place_begin)
    place_end_idx = max(person_end,place_end)
    intermediate_pos = pos_tags[person_end_idx+1:place_start_idx]
    intermediate_lemmas = lemmas[person_end_idx+1:place_start_idx]
    intermediate_ner_tags = ner_tags[person_end_idx+1:place_start_idx]
    tail_lemmas = lemmas[place_end_idx+1:]
    born_in = BornPlaceLabel(person_id=person_id, place_id=place_id, label=None, type=None)

    # Rule: Candidates that are too far apart
    if len(intermediate_lemmas) > MAX_DIST:
        yield born_in._replace(label=-1, type='neg:far_apart')

    # Rule: Candidates that have another nationality in between
    if 'MISC' in intermediate_ner_tags:
        yield born_in._replace(label=-1, type='neg:another_nationality_between')
        
	# Rule: Candidates that have another nationality in between
    if 'PERSON' in intermediate_ner_tags:
        yield born_in._replace(label=-1, type='neg:another_person_between')

    # Rule: Sentences that contain "born" in between
    #         (<P1>)([ A-Za-z]+)(wife|husband)([ A-Za-z]+)(<P2>)
    if len(VERB.intersection(intermediate_lemmas)) > 0:
        yield born_in._replace(label=2, type='pos:be_between')
        
	if  and len(VERB_POS.intersection(intermediate_pos)) > 1:
		yield born_in._replace(label=-1, type='pneg:other verbs')
