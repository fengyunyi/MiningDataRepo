'''
fetch source code of verified smart contracts from Etherscan

usage: modify line 31 and 32 to specify start and end (index) of contract address

'''

from time import sleep
from bs4 import BeautifulSoup
from tqdm import tqdm

import requests
import pandas as pd

def get_all_address(path_csv='verified_contracts.csv'):
	df = pd.read_csv(path_csv)
	return df['Address'].str[:42].tolist()

def parse_save_source(r, addr, directory):
	soup = BeautifulSoup(r.content, "html.parser")
	source_place = soup.find('pre', attrs={'class':'js-sourcecopyarea'})
	if source_place:
		with open(directory + str(addr) + '.sol', 'w') as f:
			f.write(source_place.get_text())
	else:
		print(i,'Contract at {} failed, parsing/saving errors'.format(address_list[i]))
	
	

if __name__ == '__main__':

	start = 0
	end = 0
	my_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
	headers = {'user-agent': my_user_agent}
	timeout = 0.5
	
	
	address_list = get_all_address()
	print('number of contracts to be downloaded: ', len(address_list))
	
	for i in tqdm(range(start, end+1)):
		url = 'https://etherscan.io/address/' + address_list[i] + '#code'
		
		while timeout <= 6:
			try:
				r = requests.get(url, headers=headers, timeout=timeout)
				break
			except requests.Timeout as e:
				print(i,'Contract at {} failed, time out. Trying again'.format(address_list[i]))
				sleep(5)
				timeout *= 2
					
		success = r.status_code == 200
		if success:
			parse_save_source(r, address_list[i], 'contract_source (over 10 thousand files)/')

		else: 
			print(i,'Contract at {} failed, unknown reason, skiped'.format(address_list[i]))
		

		if i % 500 == 0:
			sleep(100)
		else:
			sleep(3)
	

