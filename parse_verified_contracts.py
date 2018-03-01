'''
parse all html files downloaded by get_verified_contracts.py into a single .csv
'''

from bs4 import BeautifulSoup
import pandas as pd
import os



def convert_to_a_csv(directory, output_filename):
    # directory: a directory contains all the html files downloaded by get_verified_contracts.py
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".html") and filename.startswith("verified_contracts"):
            with open(filename) as fp:
                soup = BeautifulSoup(fp, "html.parser")
            this_data = parse_to_list(soup)
            data.extend(this_data)
        else:
            pass
    mydf = pd.DataFrame(data)
    mydf.columns = TABLE_COLUMNS
    
    # due to the constently updating webpages, there might be some duplicated rows
    mydf.drop_duplicates(keep='first')
    
    mydf.to_csv(output_filename, index=False)
    
    
def parse_to_list(soup):
    # soup: a BeautifulSoup instance
    table = soup.find('table', attrs={'class':'table table-hover '})
    table_body = table.find('tbody')
    data = []
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    return data
    
    
if __name__ == '__main__':
	TABLE_COLUMNS = ['Address', 'ContractName', 'Compiler', 'Balance', 'TxCount', 'DateVerified']
	convert_to_a_csv('./', 'verified_contracts.csv')
	
