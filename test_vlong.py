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
################################
# 1.OUTCOMES
# 1.A INVESTMENT/unit (euro)
avg_cost = int(worksheet.cell(10,4).value)              
vrmg = int(worksheet.cell(7,8).value)
invest_unit = avg_cost*vrmg

# 1.B. SAVINGS/unit (euro)
volhr = int(worksheet.cell(8,4).value)
gem_besp_inst = volhr * vrmg

#1.C.  Carbon saving/unit (ton CO2)
#get nr of installatie first
Hshld_nr_2020 = int(worksheet.cell(5,4).value)
bkm_pv = worksheet.cell(4,8).value
bkm_pv=float(bkm_pv[0:2])/100                           	 # !!! update if the factor is lower than 10 or higher than 99 %
inst_nr=int(Hshld_nr_2020*bkm_pv)

# get ton CO2 reduction/installatie
emfct_sc2020 = worksheet.cell(13,4).value
emfct_sc2020 = float(emfct_sc2020.replace(',', '.'))   		 # attention ',' are used instead of '.' for decimal numbers --> need to change
vollasthr = int(worksheet.cell(8,4).value)
gem_besp_inst = vrmg*vollasthr 
red_ton_CO2 =(gem_besp_inst * emfct_sc2020)/1000


# MEASURE2 (M2) : MOBILITY MODAL SHIFT 
######################################
# 2. OUTCOMES
# 2.A INVESTMENT TOTAL (euro)
invest_cost = int(worksheet.cell(38,8).value)              

# 2.B. SAVINGS/unit (euro)
#expected change 
modal_change = worksheet.cell(22,4).value
modal_change = modal_change[0:3]
modal_change = float(modal_change.replace(',', '.'))/100

# number of km 2020
nr_rd_pas = worksheet.cell(24,4).value
nr_rd_pas = int(nr_rd_pas[0:9])
unr_rd_pas = worksheet.cell(25,4).value
unr_rd_pas = int(unr_rd_pas[0:9])
aant_vtg_km_2020 = nr_rd_pas + unr_rd_pas

#MWh reduction per type of fuel/diesel
eng_verbr = worksheet.cell(27,4).value
eng_verbr = float(eng_verbr.replace(',', '.'))
besp_mwh =  eng_verbr * (aant_vtg_km_2020 *modal_change)
tot_pas_dies =  worksheet.cell(32,4).value
tot_pas_dies=int(tot_pas_dies[0:6])
tot_pas_gas =  worksheet.cell(33,4).value
tot_pas_gas=int(tot_pas_gas[0:6])
frac_diesel = round(tot_pas_dies / (tot_pas_dies + tot_pas_gas),2)
diesel_eur_L = worksheet.cell(30,4).value
diesel_eur_L = float(diesel_eur_L.replace(',', '.'))
super98_eur_L = worksheet.cell(31,4).value
super98_eur_L = float(super98_eur_L.replace(',','.'))
besp_diesel = (frac_diesel * besp_mwh)
besp_super98 = round(besp_mwh,3) - besp_diesel    		# !!! does not correspond to the data in the excel sheet (the rest of the calculate therefore also)

# from MWh to L
gen_dies_engy = worksheet.cell(35,4).value
gen_dies_engy = float(gen_dies_engy.replace(',', '.'))
gen_dies_dens = worksheet.cell(34,4).value
gen_dies_dens = float(gen_dies_dens.replace(',', '.'))
gen_fuel_engy = worksheet.cell(37,4).value
gen_fuel_engy = float(gen_fuel_engy.replace(',', '.'))
gen_fuel_dens = worksheet.cell(36,4).value
gen_fuel_dens = float(gen_fuel_dens.replace(',', '.'))
besp_diesel_L = (besp_diesel * 3600/1000000000) * 1000000/gen_dies_engy/gen_dies_dens
besp_super98_L = (besp_super98 * 3600/1000000000) * 1000000/gen_fuel_engy/gen_fuel_dens

# total for both fuel/diesel, in euro
tot_besp_eur = diesel_eur_L * besp_diesel_L + super98_eur_L * besp_super98_L
tot_besp_km = modal_change * aant_vtg_km_2020                                       
red_km_eur = round(tot_besp_eur/ tot_besp_km,9)

#2.C.  Carbon saving/unit (ton CO2)
gem_vlootemis_CO2 = worksheet.cell(26,4).value
gem_vlootemis_CO2 = float(gem_vlootemis_CO2.replace(',', '.'))
tot_emiss_red_CO2_2020 = round(gem_vlootemis_CO2*tot_besp_km/1000000,9)
red_unit_CO2 = round(tot_emiss_red_CO2_2020/tot_besp_km /1000,9)

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