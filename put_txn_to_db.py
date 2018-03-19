'''
port data from all txn files downloaded by get_txns.py into a sqlite database
(since data is larger than RAM)

--- requirements ---
1. install sqlite3: sudo apt get install sqlite3
2. create a database
3. In the sqlite console, create a table named transactions:

CREATE TABLE transactions (
 txn_hash TEXT PRIMARY KEY,
 add_contract TEXT,
 blockNumber INTEGER NOT NULL,
 confirmations INTEGER NOT NULL,
 contractAddress TEXT,
 cumulativeGasUsed INTEGER,
 add_from TEXT,
 add_to TEXT,
 gas INTEGER,
 gasPrice INTEGER,
 gasUsed INTEGER,
 txn_input TEXT,
 isError INTEGER,
 nonce INTEGER,
 timeStamp INTEGER,
 transactionIndex INTEGER,
 txreceipt_status txreceipt_status,
 value INTEGER
 );

Note that, decided not to store blockhash. If want it, add one column.

Then use the blow python script to import data to the table
You can delete ./temp/ after done.
'''

# WARNING: currently writing to sqlite3 db quite slow (about 3-4 hours), need >8G RAM
# Originally used pandas.dataframe.to_sql to insert data, one call per json file, extremely slow, more than 10 hours.
# Alternatively, used odo, but seem not improving a lot and brought other issues
# Current solution: concatenate tables into bigger csv files saved to disk, then write to sqlite (reduce # of calls to insert to db)
# TODO: can be more efficient


# /home/yunyi/virtual_env/smct/bin/python3
import json
import pandas as pd
import os
import sqlite3
from tqdm import tqdm
from odo import odo
from sqlalchemy.exc import IntegrityError
#from timeout import timeout # debug


#DATABASE = 'sqlite:////home/yunyi/ethereum.db::transactions'
DATABASE = '/home/yunyi/ethereum.db'

def parse_to_df(txn_file):  
	with open(txn_file) as fp:
		parsed_json = json.load(fp)
    	
	res_len = len(parsed_json['result'])
	if res_len <= 0:
		return 0
	else:
		df = pd.DataFrame(parsed_json['result'])
		df = df.drop('blockHash', 1)

		# have to rename columns to advoid sql keywords
		# the df column names have to match exactly the table column names in db
		df.rename(columns={'from':'add_from', 'to':'add_to', \
							'input':'txn_input', 'hash':'txn_hash'}, inplace=True)
		
		# add a column for the contract address
		# the value should be the same as either the add_from or add_to,
		# and contractAddres when the transaction is contract creation 
		df['add_contract']=txn_file[23:65]
		
		return df


def append_dfs(directory, out_dir, max_row_count):
	df = pd.DataFrame([])
	count = 0
	print('concatenate data to csv...')
	for filename in tqdm(os.listdir(directory)):
			
		if filename.endswith(".json"):
			current_df = parse_to_df(directory+filename)
			if current_df.shape[0]>max_row_count:
				current_df.to_csv(out_dir+'chunk_'+str(count)+'.csv', index=False)
				count+=1
			elif df.shape[0]>max_row_count:
				df.to_csv(out_dir+'chunk_'+str(count)+'.csv', index=False)
				count+=1
				df = pd.DataFrame([])
			else:
				df = df.append(current_df)
		else:
			continue
	print('done.')



def put_all_files_to_db(directory):
	conn = sqlite3.connect(DATABASE)

	for filename in tqdm(os.listdir(directory)):
		if filename.endswith(".csv") and filename.startswith("temp"):
			print(filename)
			df = pd.read_csv(filename)
			
			# string to numeric
			# >>> np.finfo('float64').max
			# 1.7976931348623157e+308
			# >>> np.iinfo('int64').max
			# 9223372036854775807			
			df.blockNumber = pd.to_numeric(df.blockNumber)
			df.confirmations = pd.to_numeric(df.confirmations)
			df.cumulativeGasUsed = pd.to_numeric(df.cumulativeGasUsed)
			df.gas = pd.to_numeric(df.gas)
			df.gasUsed = pd.to_numeric(df.gasUsed)
			df.isError = pd.to_numeric(df.isError)
			df.timeStamp = pd.to_numeric(df.timeStamp)
			df.transactionIndex = pd.to_numeric(df.transactionIndex)
			df.txreceipt_status = pd.to_numeric(df.txreceipt_status)
			df.nonce = pd.to_numeric(df.nonce)
			df[['value', 'gasPrice']] = df[['value', 'gasPrice']].astype(float)
			
			df.to_sql('transactions', conn, if_exists='append', index=False)
			
			''' using odo instead
			try:
				t = odo(df, DATABASE)
			except IntegrityError:
				continue
			'''

	 	
if __name__ == '__main__':
	append_dfs('./transactions/', './temp/', max_row_count=100000)
	put_all_files_to_db('./temp/')


