"""fetch transactions of verified smart contracts from Etherscan API

API doc: https://etherscan.io/apis#accounts

Required input file: verified_contracts.csv that stores the addresses of contracts

Usage: modify line 31 and 32 to specify start and end (index) of contract address
if there are failed contracts, record the addresses and fix them later
replace YourApiKeyToken with your token

Todo: none

Note: Etherscan API request requires parameters in specified order
a rate limit of 5 requests/sec (exceed and you will be blocked) -> sleep at least 0.2 sec

"""

from time import sleep
from tqdm import tqdm
import json
import requests
import pandas as pd


def try_request_get(limit, url, payload, timeout):
	# A wrapper of the request.get() function
	# It enables re-submission of a failed request
	# limit: the upper bound of times we can try
	k = 0
	while k < limit:
		try:
			r = requests.get(url, params=payload, timeout=timeout)
			sleep(0.2)
			if r.status_code == 200:
				return r

		except requests.Timeout:
			print('time out. Trying again...')
			k += 1
			sleep(1)
	return 0


def get_all_address(path_csv='verified_contracts.csv'):
	df = pd.read_csv(path_csv)
	return df['Address'].str[:42].tolist()


def fetch_transactions(url, module, startblock, endblock, offset, address_list,
					   start, end, my_api_key, timeout, limit, isInternal=False):
	# fetch page by page until no result return

	if isInternal:
		txn_type = 'txlistinternal'
		folder_name = 'transactions_internal/int_txn_'
	else:
		txn_type = 'txlist'
		folder_name = 'transactions/nor_txn_'


	for i in tqdm(range(start, end+1)):

		# start from the 1st page
		page = 1
		payload = (('module', module), ('action', txn_type), ('address', address_list[i]),
				   ('startblock', startblock), ('endblock', endblock), ('page', page), ('offset', offset),
				   ('sort', 'asc'), ('apikey', my_api_key))

		r_1 = try_request_get(limit, url, payload, timeout)
		if r_1 != 0:
			this_dic = r_1.json() # dictionary object
			if len(this_dic['result']) <= 0:  # no transaction at all
				print('no transaction at {}, passed'. format(address_list[i]))
				continue
		else:
			print('time out, reached request limit for {}, passed'.format(address_list[i]))
			continue

		# there are more pages to download, stop until reacching an empty page
		while True:
			page += 1
			payload = (('module', module), ('action', txn_type), ('address', address_list[i]),
					   ('startblock', startblock), ('endblock', endblock), ('page', page), ('offset', offset),
					   ('sort', 'asc'), ('apikey', my_api_key))
			r = try_request_get(limit, url, payload, timeout)
			if r == 0:
				print('Contract at {} Page {} failed, time out, reached limit. passed'.format(address_list[i], page))
				break
			else:
				current_res = r.json()['result']
				if len(current_res) <= 0: # no centent in this page(previous page is the last page)
					break
				this_dic['result'].extend(current_res)

		# done all pages
		# print('done contract {}'.format(address_list[i]))
		# print('number of transactions for {}: {}'.format(address_list[i], len(this_dic['result'])))
		with open(folder_name + str(address_list[i])+ '.json', 'w') as f:
			json.dump(this_dic, f)

if __name__ == '__main__':

	
	my_api_key = 'YourApiKeyToken'
	timeout = 2
	url = 'http://api.etherscan.io/api'
	modu = 'account'
	startblock = 0
	endblock = 99999999
	off_set = 5000  # how many record per page (request)
	lim = 5

	address_list = get_all_address()
	start = 0
	end = len(address_list) - 1

	# Getting normal transactions
	print('Getting normal txns of smart contracts ......')
	fetch_transactions(url, modu, startblock, endblock, off_set, address_list,
					   start, end, my_api_key, timeout, lim, False)

	print('\n')

	# Getting internal transactions
	print('Getting internal txns of smart contracts......')
	fetch_transactions(url, modu, startblock, endblock, off_set, address_list,
					   start, end, my_api_key, timeout, lim, True)

	

		

	
	
	

