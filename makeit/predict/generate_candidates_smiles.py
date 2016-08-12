# Import relevant packages
from __future__ import print_function
from global_config import USE_STEREOCHEMISTRY
import argparse
import numpy as np     	      	   # for simple calculations
import os                          # for saving
import sys
import rdkit.Chem as Chem
import makeit.retro.transformer as transformer 
from makeit.retro.canonicalization import SmilesFixer
from pymongo import MongoClient    # mongodb plugin
import re
import time

def main(template_collection = 'lowe_refs_general_v3', reaction_collection = 'lowe_1976-2013_USPTOgrants_reactions',
		candidate_collection = 'candidates', USE_REACTIONSMILES = True, mincount = 4, n_max = 50, seed = None, 
		outfile = '.', singleonly = True, check = True):

	from rdkit import RDLogger
	lg = RDLogger.logger()
	lg.setLevel(4)

	client = MongoClient('mongodb://guest:guest@rmg.mit.edu/admin', 27017)
	db = client['askcos_transforms']
	templates = db[template_collection]
	Transformer = transformer.Transformer()
	Transformer.load(templates, mincount = mincount, get_retro = False, get_synth = True)
	print('Out of {} database templates,'.format(templates.count()))
	print('Loaded {} templates'.format(Transformer.num_templates))
	Transformer.reorder()
	print('Sorted by count, descending')

	db = client['reaction_examples']
	reactions = db[reaction_collection]

	db = client['prediction']
	candidates = db[candidate_collection]

	if check:
		done_ids = [doc['reaction_id'] for doc in candidates.find(
			{'reaction_collection': reaction_collection, 'found': True}
		)]

	else:
		done_ids = []

	# Define generator
	class Randomizer():
		def __init__(self, seed, done_ids = []):
			self.done_ids = done_ids
			np.random.seed(seed)
			if outfile:
				with open(os.path.join(outfile, 'seed.txt'), 'w') as fid:
					fid.write('{}'.format(seed))
		def get_rand(self):
			'''Random WITHOUT replacement'''
			while True:
				doc = reactions.find({'products': {'$size': 1}, \
					'products.0.smiles': {'$not': re.compile('.*\..*')},
					'random': { '$gte': np.random.random()}}).sort('random', 1).limit(1)[0]
				if doc['_id'] in self.done_ids: continue
				self.done_ids.append(doc['_id'])
				yield doc

	if seed == None:
		seed = np.random.randint(10000)
	else:
		seed = int(seed)
	randomizer = Randomizer(seed, done_ids = done_ids)
	generator = enumerate(randomizer.get_rand())

	smilesfixer = SmilesFixer()

	# LOGGING
	flog = open('GENERATE_CANDIDATES_LOG_{}.txt'.format(seed), 'w')
	flog.write('mincount: {}\n'.format(mincount))
	flog.write('number of templates: {}\n'.format(Transformer.num_templates))

	try:
		for i, reaction in generator:

			# LOGGING
			start_time = time.time()

			if i == n_max: 
				break

			print('#########')
			print('## RXN {}'.format(i))
			print('#########')

			if bool(USE_REACTIONSMILES):
				rxn_smiles = reaction['reaction_smiles'].split(' ')[0]
				all_smiles = [smilesfixer.fix_smiles(x) for x in rxn_smiles.split('>')[0].split('.')]
				mol = Chem.MolFromSmiles(rxn_smiles.split('>')[2])
			else:
				all_smiles =  [smilesfixer.fix_smiles(x['smiles']) for x in reaction['reactants']]
				if 'catalysts' in reaction:
					all_smiles += [smilesfixer.fix_smiles(x['smiles']) for x in reaction['catalysts']] 
				if 'spectators' in reaction:
					all_smiles += [smilesfixer.fix_smiles(x['smiles']) for x in reaction['spectators']] 
				mol = Chem.MolFromSmiles(reaction['products'][0]['smiles'])

			# LOGGING
			n_reactant_atoms = sum([len(Chem.MolFromSmiles(x).GetAtoms()) for x in all_smiles])
			print('Number of reactant atoms: {}'.format(n_reactant_atoms))
			if n_reactant_atoms > 200:
				print('Skipping huge molecule!')
				continue

			if mol:
				[x.ClearProp('molAtomMapNumber') for x in mol.GetAtoms()] # remove atom mapping
				print('REACTANTS: {}'.format('.'.join(all_smiles)))
				print('PRODUCT: {}'.format(Chem.MolToSmiles(mol, isomericSmiles = USE_STEREOCHEMISTRY)))
				target_smiles = smilesfixer.fix_smiles(Chem.MolToSmiles(mol, isomericSmiles = USE_STEREOCHEMISTRY))
				result = Transformer.perform_forward('.'.join(all_smiles), progbar = True, singleonly = singleonly)

			found_true = False
			for product in result.products:
				if target_smiles in product.smiles_list:
					found_true = True
			if found_true:
				print('True product found!')
			else:
				print('True product not found...')
			print('{} candidates'.format(len(result.products)))

			# Prepare doc and insert
			doc = {
				'reaction_collection': reaction_collection,
				'reaction_id': reaction['_id'],
				'reactant_smiles': '.'.join(all_smiles),
				'product_smiles_candidates': ['.'.join(product.smiles_list) for product in result.products],
				'product_smiles_true': target_smiles,
				'found': found_true,
				'num_candidates': len(result.products),
			}
			res = candidates.insert(doc)

			# # MEMORY LEAK DEBUG
			# Transformer.tracker.print_diff()

			# LOGGING
			end_time = time.time()
			print('time: {}'.format(end_time - start_time))
			unique_candidates = len(set([max(product.smiles_list, key = len) for product in result.products]))
			print('unique candidates using longest prod: {}'.format(unique_candidates))
			flog.write('{}\t{}\t{}\t{}\t{}\n'.format(i, n_reactant_atoms, len(result.products), unique_candidates, end_time - start_time))

	except Exception as e:
		print('Error! {}'.format(e))

	flog.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', type = bool, default = False,
						help = 'Verbose printing; defaults to False')
	parser.add_argument('-n', '--num', type = int, default = 50,
						help = 'Maximum number of records to examine; defaults to 50')
	parser.add_argument('--reaction_collection', type = str, default = 'lowe_1976-2013_USPTOgrants_reactions',
						help = 'Collection of reaction_examples to use; defaults to lowe_1976-2013_USPTOgrants_reactions')
	parser.add_argument('--template_collection', type = str, default = 'lowe_refs_general_v3',
						help = 'Collection of templates to use; defaults to lowe_refs_general_v3')
	parser.add_argument('--candidate_collection', type = str, default = 'candidates', 
						help = 'Collection of candidates to write to; defaults to candidates')
	parser.add_argument('--seed', type = int, default = None,
						help = 'Seed for random number generator')
	parser.add_argument('--rxnsmiles', type = bool, default = True,
						help = 'Use reaction_smiles for species, not pre-parsed; defaults to true')
	parser.add_argument('--mincount', type = int, default = 4,
						help = 'Minimum template count to include in transforms; defaults to 4')
	parser.add_argument('--singleonly', type = bool, default = True,
						help = 'Whether to record major product only; defaults to True')
	parser.add_argument('--check', type = bool, default = True,
						help = 'Whether to check current collection to see if reaction example has been done')
	args = parser.parse_args()


	main(template_collection = args.template_collection, reaction_collection = args.reaction_collection,
		candidate_collection = args.candidate_collection, seed = args.seed, n_max = int(args.num), 
		mincount = int(args.mincount), USE_REACTIONSMILES = bool(args.rxnsmiles), singleonly = bool(args.singleonly),
		check = args.check)