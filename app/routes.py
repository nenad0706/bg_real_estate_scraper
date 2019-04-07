from flask import Flask
from flask import render_template
from flask import request
from app import app
import pymongo
import math
import requests
import json
import copy
import datetime
import time
from .formats import *

# timestamp to json 

datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'

# structures and functions for formating links


structure2word = {
		'0.5': "garsonjera",
		'1.0': "jednosoban",
		'1.5': "jednoiposoban",
		'2.0': "dvosoban",
		'2.5': "dvoiposoban",
		'3.0': "trosoban",
		'3.5': "troiposoban",
		'4.0': "cetvorosoban",
		'4.5': "cetvoroiposoban",
		'5+': "petosoban i veci",
		'OTHER' : "ostalo"
}

def escape_url(text):
	text = text.lower()
	text = text.replace('ž','z')
	text = text.replace('č','c')
	text = text.replace('ć','c')
	text = text.replace('đ','dj')
	text = text.replace('š','s')
	text = text.replace(' ', '-')
	return text

def format_url(id, structure, street, municipality):
	structure = escape_url(structure2word[structure])
	street = escape_url(street)
	municipality = escape_url(municipality)
	return "https://cityexpert.rs/prodaja/stan/{}/{}-{}-{}".format(id, structure, street, municipality)

def conv_furnished(furnished):
	if furnished == "Unfurnished":
		return "Yes"
	elif furnished == "Furnished":
		return "No"
	elif furnished == "Semi furnished":
		return "Semi"
	else:
		return furnished

def conv_filed(filed):
	if filed == "Registered":
		return "Yes"
	elif filed == "Unregistered":
		return "No"
	else:
		return filed

# routes

@app.route('/')
@app.route('/index')
def index():
	client = pymongo.MongoClient("mongodb://0.0.0.0:27017")
	db = client["apt4sale_belgrade"]
	apts = db["apartment"]

	municipalites = apts.distinct("municipality")
	

	return render_template('index.html', municipalites=municipalites)


@app.route('/details')
def details():
	client = pymongo.MongoClient("mongodb://0.0.0.0:27017")
	db = client["apt4sale_belgrade"]
	apts = db["apartment"]

	municipality_name = request.args.get('m', type=str)
	page = request.args.get('p', default=1, type=int)
	results = list(apts.find( { "municipality": municipality_name}).sort("price", -1))

	n = len(results)
	pages = 1 + math.floor(n / 20)
	if page > pages:
		page = pages
	
	results = results[(page-1)*20:page*20]
	

	# pagination 

	pagination = {}
	
	
	pagination['current'] = '{}/{}'.format(page, pages)
	if page > 1:
		pagination['first'] = {'label': 'First', 'css_class': 'pag-en', 'url': '/details?m={}&p={}'.format(municipality_name, 1)}
		pagination['prev'] = {'label': '<', 'css_class': 'pag-en', 'url': '/details?m={}&p={}'.format(municipality_name, page-1)}
	else:
		pagination['first'] = {'label': 'First', 'css_class': 'pag-dis', 'url': '/details?m={}&p={}'.format(municipality_name, 1)}
		pagination['prev'] = {'label': '<', 'css_class': 'pag-dis', 'url': ''}

	if page < pages:
		pagination['last'] = {'label': 'Last', 'css_class': 'pag-en', 'url': '/details?m={}&p={}'.format(municipality_name, pages)}
		pagination['next'] = {'label': '>', 'css_class': 'pag-en', 'url': '/details?m={}&p={}'.format(municipality_name, page+1)}
	else:
		pagination['last'] = {'label': 'Last', 'css_class': 'pag-dis', 'url': '/details?m={}&p={}'.format(municipality_name, pages)}
		pagination['next'] = {'label': '>', 'css_class': 'pag-dis', 'url': ''}


	# normalize data

	for r in results:
		r['price'] = round(r['price'], 2)
		r['pricePerSize'] = round(r['pricePerSize'], 2)
		r['url'] = format_url(r['propId'], r['structure'], r['id'], r['municipality'])
		if r['structure'] == 'OTHER':
			r['structure'] = 'other'
		r['filed'] = conv_filed(r['filed'])
		r['furnished'] = conv_furnished (r['furnished'])

	municipality_details_list = apts.aggregate([
		{ 
			'$match': {"municipality": municipality_name}
		},
		{
			'$group': {
				'_id': 'null',
				'avg_price': { '$avg' : '$pricePerSize' },
				'count' : { '$sum':1 },
				'avg_size' : { '$avg' : '$size'}
			}
		},
	])
	municipality_details = list(municipality_details_list)[0]
	municipality_details['avg_price'] = round(municipality_details['avg_price'], 2)
	municipality_details['avg_size'] = round(municipality_details['avg_size'], 2)
	
	return render_template('details.html', mn=municipality_name, md=municipality_details, apts=results, pg=page, pag=pagination)


@app.route('/scrape')
def scrape():

	log = {}
	log['too_fast'] = False

	client = pymongo.MongoClient("mongodb://0.0.0.0:27017")
	db = client["apt4sale_belgrade"]
	general_data = db["general_data"]
	apts = db["apartment"]

	now_time = datetime.datetime.now()
	coll_lts = general_data.find_one({'name':'last_time_scraped'})
	if general_data.find_one({'name':'last_time_scraped'}) is None:
		general_data.insert_one({'name':'last_time_scraped', 'timestamp':now_time.strftime(datetimeFormat)})
	else:
		last_time_scraped_str = coll_lts['timestamp']
		last_time_scraped = datetime.datetime.strptime(last_time_scraped_str, datetimeFormat)
		diff = now_time - last_time_scraped
		if diff.total_seconds() < 1800:
			log['success'] = False
			log['message'] = "Scraper did its job less than 30 minutes ago."
			log['found_in_db'] = 0
			log['fetched_new'] = 0
			log['too_fast'] = True
			log['last_time_scraped'] = last_time_scraped_str
			return render_template('scrape.html', log=log)

	
	found_in_db = 0
	fetched_new = 0
	cUrl = 'https://cityexpert.rs/api/Search/'

	current_page = 1

	page = json.loads(requests.post(cUrl, data=data.format(current_page), headers=headers).text)
	result = page["result"]

	apts.create_index([('propId', pymongo.ASCENDING)], unique=True)

	while len(result) > 0:

		# transform data
		for element in result:
			for key_to_delete in keys_to_delete:
				del element[key_to_delete]
			# replace _ with / in floor
			if "_" in element["floor"]:
				element["floor"] = element["floor"].replace("_", "/")
			# filed id to registered string
			if element["filed"] <= len(filed_dict):
				element["filed"] = filed_dict[element["filed"]]
			# furnished id to furnished string
			if element["furnished"] <= len(furnished_dict):
				element["furnished"] = furnished_dict[element["furnished"]]
			
			# db insert
			rlist = apts.find_one({'propId': element['propId']})
			if rlist is None:
				fetched_new += 1
				element_copy = copy.deepcopy(element)
				apts.insert_one(element_copy)
			else:
				found_in_db += 1
		
		current_page = current_page + 1
		page = requests.post(cUrl, data=data.format(current_page), headers=headers).json()
		result = page["result"]


	log['found_in_db'] = found_in_db
	log['fetched_new'] = fetched_new
	last_time_scraped_str = coll_lts['timestamp']
	if fetched_new + found_in_db == 0:
		log['last_time_scraped'] = last_time_scraped_str
		log['success'] = False
		log['message'] = "Oh no! Scraper did not find any data."
	else:
		log['last_time_scraped'] = last_time_scraped_str
		now_time = datetime.datetime.now()
		general_data.update_one({'name':'last_time_scraped'}, {'$set': {'timestamp': now_time.strftime(datetimeFormat)}})
		log['success'] = True
		log['message'] = "Scraping successful."

	return render_template('scrape.html', log=log)
