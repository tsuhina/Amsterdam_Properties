#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 17:17:36 2018
@author: mojtaba
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import csv

# data_set = pd.read_csv('Apartments_koopen.csv')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
quote_page = 'https://www.jaap.nl/koophuizen/noord+holland/groot-amsterdam/amsterdam'
page = requests.get(quote_page, verify=False, timeout=20)
soup = BeautifulSoup(page.content, "lxml")
A = []
Dataset = []
Dataset_address = []
Dataset_kenmerk = []
Dataset_woningwarde = []
Dataset_buurt = []
Dataset_inowner = []
for line in soup.find_all('span', class_='page-info'):
    A = line.text.strip().split('van')
    last_page = int(A[-1])

def address(soup2):
	for row2 in soup2.find_all('div', class_='detail-address'):
		#finding street name
		street = row2.find('div', class_= 'detail-address-street')
		street = street.text
		zipcode = row2.find('div', class_='detail-address-zipcity')
		try:
			zipcode = zipcode.text
			zipcode2 = re.search(r'^\d{4}\s*\w{2}', zipcode).group()
		except Exception:
			try:
				zipcode = street.split(',')[-1]
				zipcode2 = re.search(r'^\d{4}\s*\w{2}|\b\d{4}\s*\w{2}', zipcode).group()
			except:
				zipcode2 = "na"
		price = row2.find('div', class_='detail-address-price')
		price = price.text.strip().replace('€','')
		return street, zipcode2,price

def broker(soup2):
	for row3 in soup2.find_all('div', class_='detail-broker'):
		broker_name = row3.find('div', class_='broker-name')
		broker_name = broker_name.text
		return broker_name

def kenmerk(soup2):
	kenmerk = []
	for row in soup2.find_all('div', class_='detail-tab-content kenmerken'):
		for row2 in row.find_all('td', class_='value'):
			kenmerk.append(row2.text.strip().replace('€',''))
	return kenmerk

def woning(soup2):
	woning = []
	for row in soup2.find_all('div', class_='detail-tab-content woningwaarde'):
		for row2 in row.find_all('td', class_='value'):
			woning.append(row2.text.strip().replace('€',''))
		for row3 in row.find_all('td', class_='value-3-3'):
		    woning.append(row3.text.strip().replace('€',''))
	return woning

def buurt(soup2):
	buurt_target = []
	buurt_distance = []
	buurt_name = []
	buurt_dict = {}
	#buurt_dict = {'neighbourhood':[]}
	for row in soup2.find_all('table', class_='voorzieningen'):
		for row4 in row.find_all_next('div', class_='no-dots'):
			buurt_name.append(row4.text.strip())
		for row2 in row.find_all_next('td', class_='value-1-2'):
			buurt_target.append(row2.text.strip())
		for row3 in row.find_all_next('td', class_='value-2-2'):
			buurt_distance.append(row3.text.strip().replace('\xa0',' '))
		buurt_place = row.find_all('td', colspan='3')
		buurt_place = buurt_place[0].text.replace('Deze woning is gelegen in de buurt ','')
        

	for i in range(len(buurt_target)):
		buurt_dict[buurt_name[i]] = [buurt_target[i],buurt_distance[i], buurt_place]

	return buurt_dict

def inwoner(soup2):
	inwoner = []
	for row in soup2.find_all('table', class_='two-blocks'):
		for row2 in row.find_all('td', class_='value'):
			inwoner.append(row2.text.strip().replace('\t',''))
	return inwoner


for counter in range(1, last_page):
        print("The page number is:", counter)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        page = requests.get("https://www.jaap.nl/koophuizen/noord+holland/groot-amsterdam/amsterdam/p"+str(counter)
                            , verify=False, timeout=50)
        soup = BeautifulSoup(page.content, "lxml")
        #print(counter)
        # finding reviews-container since all the input located there
        for row in soup.find_all('a', class_='property-inner', href=True):
            buurt1 = {}
            inowner1 = []
            link = row.attrs['href']
            page2 = requests.get(link, verify=False, timeout=50)
            soup2 = BeautifulSoup(page2.content, "lxml")
            street, zipcode, price = address(soup2)
            broker_name = broker(soup2)
            kenmerken = kenmerk(soup2)
            woningwarde = woning(soup2)
            buurt1.clear()
            buurt1 = buurt(soup2)
            inwoner1 = inwoner(soup2)
            Address_set = [street, zipcode, price, broker_name]
            Kenmerk_set = [kenmerken]
            Woningwarde_set = [woningwarde]
            Buurt_set = [buurt1]
            Inwoner_set = [inwoner1]
            Dataset_address.append(Address_set)
            Dataset_kenmerk.append(kenmerken)
            Dataset_woningwarde.append(woningwarde)
            Dataset_buurt.append(buurt1)
            Dataset_inowner.append(inwoner1)

df_address = pd.DataFrame(Dataset_address, columns = ['Street', 'Zipcode', 'Price', 'Broker'])
df_kenmerk = pd.DataFrame(Dataset_kenmerk, columns = ['Type', 'Construction_year', 'Living_area', 'LOT', 'Plot', 'Other',
													  'Insulation','Heating', 'Energy_label', 'Energy_consumption',
													 'inside_maintenance_state', 'Rooms', 'Bedrooms', 'Sanitation', 'kitchen',
													 'outside_maintenace_state','outside_state_painting','Graden','view','Balcony', 'Garage',
													 'number_of_times_shown', 'number_of_times_shown_yesterday'])
df_woningwarde = pd.DataFrame(Dataset_woningwarde, columns = ['posted_date','current_price', 'original_price', 'changes_in_price', 'price',
															 'price_per_m2', 'times_in_sales',])
df_buurt = pd.DataFrame(Dataset_buurt, columns = ['Railway_station', 'gas_station', 'Fitness_center', 'Supermarket', 'Elementary_school',
												  'Day_care', 'High_school', 'Cafe','Video_store', 'GP', 'Dentistary', 'library', 'neighbourhood'])
df_inowner = pd.DataFrame(Dataset_inowner, columns = ['inhabitants','distribution_fm', 'population_density','Age_0-15',
													  'age_15-25','age_25-45','age_45-65','age_older','indigenous', 'western_allochtoon',
													  'none_western','household', 'household_single', 'household_wo_kids', 'household_with_kids',
													  'avg_person_per_household', 'perc_with_job', 'high_income', 'medium_income', 'low_income',
													  'income_avg', 'social_benefit'])

df_address.to_csv('houses_address.csv', sep = ',', encoding ='utf-8', index=False)
df_kenmerk.to_csv('houses_details.csv', sep = ',', encoding ='utf-8', index=False)
df_woningwarde.to_csv('houses_price.csv', sep = ',', encoding ='utf-8', index=False)
df_inowner.to_csv('houses_population.csv', sep = ',', encoding ='utf-8', index=False)
#df_buurt.to_csv('houses_neighborhood.csv', sep = ',', encoding ='utf-8', index=False)



 
order = ["treinstation","tankstation","supermarkt","basisschool","kinderopvang","middelbare school",
		 "café","videotheek","(huis)arts","tandarts", "fitnesscentrum","bibliotheek"]
with open('houses_neighborhood.csv', 'w', newline='') as f:
    dict_writer = csv.DictWriter(f, order)
    dict_writer.writeheader()
    dict_writer.writerows(Dataset_buurt)