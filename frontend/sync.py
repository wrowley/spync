import argparse
import os
import json
import sys

HERE = os.path.dirname(__file__)
BASE = os.path.join(HERE, '..', '..')

sys.path.append(BASE)

import spync

def spync_json(json_file, remove_dst_only_files):
	with open(json_file) as fp:
		json_blob = json.load(fp)

	#TODO: validate JSON

	syncer = spync.Syncer(json_blob)

	syncer.sync(remove_dst_only_files)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    'mapping_file',
	    help='a JSON file which contains a set of tuples of the form ...')
	parser.add_argument(
	    '--brutal', '-b',
	    action='store_true',
	    help='removes destination files that are not in their corresponding'
	         'source locations')
	args = parser.parse_args()

	spync_json(args.mapping_file, args.brutal)
