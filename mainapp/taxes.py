from bs4 import BeautifulSoup
import requests
from .config import tax_url

def tax_bracket(salary):
    r = requests.get(tax_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    split_list = str(soup).split('Marginal Rates:')[1].split('for married couples filing jointly')
    single = {}
    for i in split_list:
        try:
            i_rate = i.index('%')
            i_single = i.index('$')
            income = i[i_single+1:i.find(' ',i_single)].replace(',','')
            rate = i[i_rate-2:i_rate]
            single[str(income)] = rate
        except ValueError:
            break

    for key in single.keys():
        if int(key) >= int(salary):
            continue
        else:
            break
    return single[key]


