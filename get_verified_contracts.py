'''
fetch a list all verified smart contracts from Etherscan
On Feb 20 4:34pm, there are 622 pages, a total Of 15550 verified contract source codes found
usage: modify the startPage and endPage as you want
'''

from time import sleep
import requests

if __name__ == '__main__':

	startPage = 502
	endPage = 622

	for i in range(startPage,endPage+1):
		url = 'https://etherscan.io/contractsVerified/'+str(i)
		r = requests.get(url,timeout=1)
		print('getting page ', i, 'status code: ', r.status_code)

		with open('verified_contracts_' + str(i) + '.html', 'w') as f:
			f.write(r.text)

		sleep(5)
	

