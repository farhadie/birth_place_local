#!/usr/bin/env python
from deepdive import *

@tsv_extractor
@returns(lambda
        mention_id       = "text",
        mention_text     = "text",
        doc_id           = "text",
        sentence_index   = "int",
        begin_index      = "int",
        end_index        = "int",
    :[])
def extract(
        doc_id         = "text",
        sentence_index = "int",
        tokens         = "text[]",
        ner_tags       = "text[]",
	):
	"""
	Finds phrases that are continuous words tagged with NATIONALITY.
	"""
	num_tokens = len(ner_tags)
	# find all first indexes of series of tokens tagged as MICS
	first_indexes = (i for i in xrange(num_tokens) if ner_tags[i] == "MISC" and (i == 0 or ner_tags[i-1] != "MISC"))
	for begin_index in first_indexes:
		end_index = begin_index
		# generate a mention identifier
		mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, begin_index, end_index)
		mention_text = " ".join(map(lambda i: tokens[i], xrange(begin_index, end_index)))
		# Output a tuple for each Nationality phrase
		yield [
			mention_id,
			mention_text,
			doc_id,
			sentence_index,
			begin_index,
			end_index,
		]
