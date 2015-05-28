# This application parses a csv file containing hardware info on
# company leases, searches the webportal, and drops relevant data
# into a separate csv for the location given. 


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sys import stdin
import time
import datetime
import calendar


##################################################
################ assets thread ###################
##################################################

from collections import deque
import threading

active = 1
assets = deque([])
assetsOut = deque([])
dataReady = deque([])

def csvDataWriter():
	with open('user.csv','w') as csv:
		while(active):
			if len(dataReady)>0:
				if len(assetsOut)>0:
					csv.write(str(assetsOut.popleft()))
					dataReady.popleft()
		csv.flush()
	return 1;

t = threading.Thread(target=csvDataWriter)
t.start()

##################################################
############## end assets thread #################
##################################################



url = ''
with open('url','r') as u:
	url = url.readline().strip()

browser = webdriver.Firefox()
# browser = webdriver.PhantomJS('C:\phantomjs-2.0.0-windows\\bin\phantomjs.exe')

with open('credentials','r') as c:
	login = c.read().strip().split('\n')
	c.flush()

def waitForPageById(element, seconds=15):
	try:
		element = WebDriverWait(browser, seconds).until(
			EC.presence_of_element_located((By.ID, element))
		)
		return 1;
	except:
		print ('Failed to load page')
		return 0;

# pull asset info from provided csv sheet
assetkeys = []
with open('assetkeys','r') as ak:
	for key in ak.readline().split(','):
		assetkeys.append(key)
def getAssetInfo():
	
	print 'Collecting information on assets:'

	with open('assetsToSearch.csv','r') as assetsToSearch:
		for line in assetsToSearch.readlines():	
			
			lineCols = line.split(',')
			if (len(lineCols) < 10):
				print ('Error reading line: '+line)
				continue

			newAsset = dict.fromkeys(assetkeys)
			newAsset['custnum'] = lineCols[0]
			newAsset['type'] = lineCols[1]
			newAsset['model'] = lineCols[2]
			newAsset['serial'] = lineCols[3]
			newAsset['userid'] = lineCols[4]
			newAsset['status'] = lineCols[5]
			newAsset['startdate'] = lineCols[6]
			newAsset['eoldate'] = lineCols[7]
			newAsset['descript'] = lineCols[8]
			newAsset['ogcn'] = lineCols[9]
			

			#see PyAMInsert.manageassets for calendar interaction

			if not '' in newAsset['userid']:
				print('User already found for asset')
				continue

			if not '' in newAsset['status']:
				print('Location already found for asset')
				continue

			assets.append(newAsset)

	print 'Finished reading asset sheet'
	print 'Total assets loaded: '+ str(len(assets))
	return 1;

def loginServiceCenter():

	browser.get(url)	
	if not waitForPageById('j_username',3):
		browser.get(url+'/maximo')


	# locate login and password forms
	loginform = browser.find_element_by_id('j_username')
	passwordform = browser.find_element_by_id('j_password')

	# type in user credentials
	loginform.send_keys(login[0])
	passwordform.send_keys(login[1])

	# log in using given credential
	loginbutton = browser.find_element_by_id('loginbutton')
	loginbutton.click() 

	return 1;

def openAssetManager():
	if waitForPageById('mx106_anchor_1'):
		browser.find_element_by_id('mx106_anchor_1').click()

	time.sleep(3)

	#minimize leasing end table
	if waitForPageById('mx203'):
		browser.find_element_by_id('mx203').click()
	return 1;


def queryAsset(asset, loadErr=0):
	print('queryAsset('+str(asset)+')')

	time.sleep(2)

	print('Page loaded')
	deviceNameQuery = browser.find_element_by_id('BEDEVICENAME@461488')
	print('Element found')
	deviceNameQuery.send_keys(asset['serial'])
	deviceNameQuery.send_keys(Keys.RETURN)
	print('Keys sent')
	
	time.sleep(2)

	try:
		# browser.find_element_by_partial_link_text(asset['serial']).click()
		browser.find_element_by_partial_link_text('0440').click()
		return 1;
	except:
		return 0;

def searchAssetEntry(asset):
	print('searchAssetEntry('+str(asset)+')')

	if not waitForPageById('mx444'):
		return 0; 

	# retrieve initial elements (no lease info yet)
	print('Retrieving serialNumber')
	serialNumber = browser.find_element_by_id('mx395').get_attribute('value')
	print('Retrieving location')
	location = browser.find_element_by_id('mx480').get_attribute('value')
	print('Retrieving userName')
	userName = browser.find_element_by_id('mx506').get_attribute('value')
	print('Clicking Start Center')
	browser.find_element_by_id('mx53').click()

	if asset['serial'] in serialNumber:
		if '0440' in location:
			print('Returned valid userName')
			return userName;

	# end searchAssetEntry function
	print ('Return invalid userName : Not found')
	return 'Not found';

##################################################
############### main functionality ###############
##################################################

# parse csv for asset data
if not getAssetInfo():
	active = 0

# login to service center
if not loginServiceCenter():
	active = 0

openAssetManager()
print('Asset manager loaded')

# verify location, then append asset info to new spreadsheet with updated information
# for asset in assets:
while len(assets)>0:
	asset = assets.popleft()
	if queryAsset(asset):
		userName = searchAssetEntry(asset)
		if 'Not found' in userName:
			print('Continuing')
			continue
		else:
			asset['userid']=userName
			asset['status']='Auburn Hills'
			strAsset = ''
			strAsset += asset['custnum']
			strAsset += ','
			strAsset += asset['type']
			strAsset += ','
			strAsset += asset['model']
			strAsset += ','
			strAsset += asset['serial']
			strAsset += ','
			strAsset += asset['userid']
			strAsset += ','
			strAsset += asset['status']
			strAsset += ','
			strAsset += asset['startdate']
			strAsset += ','
			strAsset += asset['eoldate']
			strAsset += ','
			strAsset += asset['descript']
			strAsset += ','
			strAsset += asset['ogcn']
			strAsset += '\n'

			dataReady.append(1)
			assetsOut.append(strAsset)
			print(strAsset)

	time.sleep(3)


time.sleep(1)
active = 0

# exit browser
browser.quit()
