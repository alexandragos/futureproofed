###############################################################################
# TEST : script for data Engineer, FUTUREPROOFED                              #
# Candidate : Alexandra Gossart (interview on 25/06, test taken on 29/06)     #
# This script takes as imput 'B' for Belgium or 'S' for Spain                 #
###############################################################################

import json								# write to JSON format (readable by REST API)
import gspread								# to access google sheets
import sys  								# to specify the country

#sequence to access the google sheet (using Google API)
from oauth2client.service_account import ServiceAccountCredentials       #  this is general
scope = ['https://spreadsheets.google.com/feeds']                        #  this is general
credentials = ServiceAccountCredentials.from_json_keyfile_name('./test-futureproofed-ee4a234a4e10.json', scope)  # this is document specific : need to have created a .json key and shared the google sheet to this email address
gc = gspread.authorize(credentials)

#define the country of interest (now there are two separate googe sheets documents, better would be to have the same document but seperate sheets ('Feuille' with each the same structure)
country = str(sys.argv[1])
if country is 'B': 
	spreadsheet_key= '1Aam7C5Kni6s1dmCQXAP2pRm_rPrdrNVx4N_Sfa3YqQk'         # this is specific : need to change if different spreadsheet 
	name='BELGIUM'
elif country is 'S': 
	spreadsheet_key = '15IGhFL_3sOr2WHE9d4GCQuNKqXPDS58eyj-DPiZkabI'
	name='SPAIN'

# Open the right google sheet 'Feuille' (in case there are several (i.e., different countries--> this can be adapted))
book = gc.open_by_key(spreadsheet_key)
worksheet = book.worksheet("Feuille 1")


# Here we start the 'real' work :-)

# MEASURE 1 (M1) : SOLAR PANELS  
# 1.OUTCOMES
# 1.A INVESTMENT/unit (euro)
invest_unit = int(worksheet.cell(10,8,value_render_option='UNFORMATTED_VALUE').value)

# 1.B. SAVINGS/unit (euro)
gem_besp_inst = int(worksheet.cell(11,8 ,value_render_option='UNFORMATTED_VALUE').value)
# print(gem_besp_inst)

#1.C. Carbon saving/unit (ton CO2)
red_ton_CO2 = float(worksheet.cell(13,8,value_render_option='UNFORMATTED_VALUE').value)
#print(red_ton_CO2)

# MEASURE2 (M2) : MOBILITY MODAL SHIFT
##########################################
# 2. OUTCOMES
# 2.A INVESTMENT TOTAL (euro)
invest_cost = int(worksheet.cell(38,8).value)              
#print(invest_cost)

# 2.B. SAVINGS/unit (euro/km)
red_km_eur =  round(float(worksheet.cell(31,10,value_render_option='UNFORMATTED_VALUE').value),9)
# print(besp_brnd_km_2020)

# 3.B. Carbon saving /unit (ton CO2)
red_unit_CO2 = round(float(worksheet.cell(40,10,value_render_option='UNFORMATTED_VALUE').value),9)

# Here we write all the calculated measures into a .json format to be easily readable in REST API. 
# Two categories : measure 1 (solar panels, id = M1) and measure 2 (mobility shift, id = M2);
# both are calculated and written for Belgium (B) or Spain (S), depending on the argument passed

measures = {
        "M1":{
	    "Country" : name,
  	    "Measure" : "Solar panels", 
            "Investment_per_unit_eur": invest_unit,
            "Unit ": "number of households",
            "savings_per_unit_eur": gem_besp_inst,
            "Yearly_carbon_emission_curbed_per_unit_in_ton" : red_ton_CO2,
            "Assumptions" :["10% of households have PV",
                           "investing cost/installation is excluding taxes and premiums but including installation and inspection",
                           "Household and city emissions are based on scenario for 2020",
                           "vermogen is based on VEA 2013"
                           ]
              },    
       "M2":{
            "Country" : name,
            "Measure" : "Modal shift transport",
            "Investment_per_km": invest_cost,
            "Units": "kilometers",
            "savings_per_km_euro": red_km_eur,
            "Yearly_carbon_emission_curbed_per_km_in_ton" :red_unit_CO2 ,
            "Assumptions" :["reductie voertuigkilometer door personenwagens in 2020 door maatregel : FASTRACE (BAU2020)",
                            "gemiddelde vlootemissiefactor CO2 voor personenwagens (diesel/benzine) in 2020 : FASTRACE (BAU2020)",
                            "aantal voertuigkilometer door personenwagens in 2020 : enkel op lokale en gewestwegen "]
             },
           }

# write in JSON format

with open(name+"_measures.json", "w") as write_file:     # we then have 'BELGIUM_measures.json' or 'SPAIN_measures.json' and each of these contain the two mesures that can be retrieved individually
    json.dump(measures,write_file)


# for peronal use only : making sure that the output is right

with open(name+"_measures.json", "r") as read_file:
    data = json.load(read_file)
measures = data.get("M2")
print(measures)