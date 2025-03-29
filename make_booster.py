#DOES NOT INCLUDE SPECIAL RARITY CARDS IDK WHAT THEY ARE

import json
import random
import os
from datetime import datetime

from scryfall_api import make_default_cards_json

CARD_FILE = 'cards/default_cards.json'
rarity_List = ('common', 'uncommon', 'rare', 'mythic')
slot_Seven = ['common', 'list']
list_Rarity = ['common','uncommon', 'rare', 'mythic', 'Special Guests']
set_Codes_With_Guests = ['lci','mkm','otj','mh3','blb','dsc','fdn','dft','tdm']

if not os.path.exists(CARD_FILE):
    print('Missing Card File, downloading from scryfall...')
    make_default_cards_json()

with open(CARD_FILE, 'r', encoding='utf-8') as file:
    jdata = json.load(file)

#Get Full set code list and delete copies
set_code_list = []

for i in jdata:
    set_code_list.append(i['set'])

set_code_list = list(set(set_code_list))
set_code_list.sort()
#print(f"Number of unique sets: {len(setcodelist)}")


#Get Full set name list and delete copies
set_name_list = []
for i in jdata:
    set_name_list.append(i['set_name'])
set_name_list = list(set(set_name_list))
set_name_list.sort()
#print(f"Number of unique set names: {len(setNames)}")


#Function to get set names and associated set codes
def get_set_dict():
    setDict = {}

    for i in set_name_list:
        for j in jdata:
            if i == j['set_name']:
                setDict[i] = j['set']
                break
    return setDict

#Call and print the set code for a given set name
sets = get_set_dict()
#print(sets['Time Spiral'])

#Get all cards in a set and return a list of them
def get_cards_in_set(set_code: str) -> list:
    cards = []
    for i in jdata:
        if i['set'] == set_code:
            cards.append(i)
    return cards

'''
timespiral_cards = get_cards_in_set(sets['Time Spiral'])
print(timespiral_cards)
print(len(timespiral_cards))
'''

#Get all commons in a set and return a list of them
def get_rarity_cards_in_set(set_code: str, rarity: str) -> list:
    cards = []
    for i in jdata:
        if i['set'] == set_code:
            if i['rarity'] == rarity:
                if i['border_color'] not in ('borderless', 'yellow'):
                    if i['nonfoil']:
                        if i['promo'] is False:
                            if i.get('promo_types') == None :
                                if i['name'] not in ('Forest', 'Plains', 'Island', 'Mountain', 'Swamp'):
                                    cards.append(i)
    return cards

#Get all lands in a set and return a list of them
def get_lands_in_set(set_code: str) -> list:
    cards = []
    for i in jdata:
        if i['set'] == set_code:
            if i['type_line'] in ('Basic Land — Forest', 'Basic Land — Plains', 'Basic Land — Island', 'Basic Land — Mountain', 'Basic Land — Swamp'):
                cards.append(i)
    return cards

#Get all non-foil wildcards in a set and return a list of them
def get_nonfoil_wildcards_in_set(set_code: str, rarity: str) -> list:
    cards = []
    for i in jdata:
        if i['set'] == set_code:
            if i['rarity'] == rarity:
                if i['nonfoil']:
                    cards.append(i)
    return cards

#Get all foil wildcards in a set and return a list of them
def get_foil_wildcards_in_set(set_code: str, rarity: str) -> list:
    cards = []
    for i in jdata:
        if i['set'] == set_code:
            if i['rarity'] == rarity:
                if i['foil'] == True:
                    cards.append(i)
    return cards

def get_List_Card(set_code: str):
    cards = []
    if set_code in set_Codes_With_Guests:
        rarity = random.choices(list_Rarity, weights = [37.52, 37.52, 6.24, 6.24, 12.48])
    else:
        rarity = random.choices(list_Rarity, weights=[42.87, 42.87, 7.13, 7.13, 0])
    for i in jdata:
        if rarity != ['Special Guests']:
            if i['set'] == 'plst':
                if i['rarity'] == rarity[0]:
                    cards.append(i)
        else:
            # sorts Special Guests by set
            lci_Special_Guests = list(map(str, (range(1, 19)))) + ['17b', '17c', '17d', '17e', '17f']
            mkm_Special_Guests = list(map(str, (range(19, 29))))
            otj_Special_Guests = list(map(str, (range(29, 39))))
            mh3_Special_Guests = list(map(str, (range(39, 49))))
            blb_Special_Guests = list(map(str, (range(54, 64))))
            dsc_Special_Guests = list(map(str, (range(64, 74))))
            fdn_Special_Guests = list(map(str, (range(74, 84))))
            dft_Special_Guests = list(map(str, (range(84, 94))))
            tdm_Special_Guests = list(map(str, (range(104, 119))))
            #Finds all the Special Guests for a given set
            if i['set'] == 'spg':
                if set_code == 'lci':
                    if i['collector_number'] in lci_Special_Guests:
                        cards.append(i)
                elif set_code == 'mkm':
                    if i['collector_number'] in mkm_Special_Guests:
                        cards.append(i)
                elif set_code == 'otj':
                    if i['collector_number'] in otj_Special_Guests:
                        cards.append(i)
                elif set_code == 'mh3':
                    if i['collector_number'] in mh3_Special_Guests:
                        cards.append(i)
                elif set_code == 'blb':
                    if i['collector_number'] in blb_Special_Guests:
                        cards.append(i)
                elif set_code == 'dsc':
                    if i['collector_number'] in dsc_Special_Guests:
                        cards.append(i)
                elif set_code == 'fdn':
                    if i['collector_number'] in fdn_Special_Guests:
                        cards.append(i)
                elif set_code == 'dft':
                    if i['collector_number'] in dft_Special_Guests:
                        cards.append(i)
                elif set_code == 'tdm':
                    if i['collector_number'] in tdm_Special_Guests:
                        cards.append(i)
    return cards

#makes a Play Booster
def make_play_booster(set_code: str):
    booster = []
    common_Sheet = make_Card_Sheet(set_code, 'common')
    uncommon_Sheet = make_Card_Sheet(set_code, 'uncommon')
    common_Start_Card = random.choice(common_Sheet)
    start_Index = common_Sheet.index(common_Start_Card)
    card_To_Add = 0
    #get commons
    for i in range(7):
        if i != 6:
            if card_To_Add + start_Index <= len(common_Sheet) - 1:
                booster.append(common_Sheet[start_Index + card_To_Add])
                card_To_Add += 1
            else:
                start_Index = 0
                card_To_Add = 0
                booster.append(common_Sheet[start_Index])
                card_To_Add += 1
        else:
            card_Seven = random.choices(slot_Seven, weights = [87.5, 12.5])
            if card_Seven == ['common']:
                if card_To_Add + start_Index <= len(common_Sheet) - 1:
                    booster.append(common_Sheet[start_Index + card_To_Add])
                else:
                    start_Index = 0
                    booster.append(common_Sheet[start_Index])
            else:
                booster.append(random.choice(get_List_Card(set_code)))
    #get uncommons
    uncommon_Start_Card = random.choice(uncommon_Sheet)
    start_Index = uncommon_Sheet.index(uncommon_Start_Card)
    for i in range(3):
        if card_To_Add + start_Index <= len(uncommon_Sheet) - 1:
            booster.append(uncommon_Sheet[start_Index + card_To_Add])
            card_To_Add += 1
        else:
            start_Index = 0
            card_To_Add = 0
            booster.append(uncommon_Sheet[start_Index])
            card_To_Add += 1
    #get rare/mythic rare
    rare_For_Pack = random.choices(rarity_List, weights=[0, 0, 87.5, 12.5])
    if rare_For_Pack == ['rare']:
        rare_Sheet = make_Card_Sheet(set_code, 'rare')
        booster.append(random.choice(rare_Sheet))
    else:
        mythic_Sheet = make_Card_Sheet(set_code, 'mythic')
        booster.append(random.choice(mythic_Sheet))
    #get land
    booster.append(random.choice(get_lands_in_set(set_code)))
    #get non-foil wildcard
    rarity_For_Wild_NF = random.choices(rarity_List, weights = [33.3, 36.7, 17.5, 7.5])
    booster.append(random.choice(get_nonfoil_wildcards_in_set(set_code, rarity_For_Wild_NF[0])))
    #get foil wildcard
    rarity_For_Wild_F = random.choices(rarity_List, weights = [33.3, 36.7, 17.5, 7.5])
    booster.append(random.choice(get_foil_wildcards_in_set(set_code, rarity_For_Wild_F[0])))

    return booster

#makes a sheet of cards
def make_Card_Sheet(set_code: str, rarity: str):
    sheet = get_rarity_cards_in_set(set_code, rarity)
    sheet_Length = len(sheet)
    columns = factoring_Easy_Peasy(sheet_Length)
    rows = sheet_Length//columns
    collation = collation_Sim(rows,columns,sheet)
    return collation

#find the factors with the smallest difference
def factoring_Easy_Peasy(length: int):
    factors= []
    differences = []
    factor_To_Send: int
    for i in range(length):
        if i != 0:
            if length % i == 0 and length/i not in factors:
                factors.append(i)
    for i in range (len(factors)):
        differences.append(length // factors[i])
    index_For_Factor = differences.index(min(differences))
    factor_To_Send = factors[index_For_Factor]
    return factor_To_Send

#Simulates the manufacturing process of cards
#pretends the cards are placed in a grid and takes the first card in the last row and stacks
#the card above it on top, and does this from 3-5 times before moving to the next column,
#then it stacks those piles where the left is the bottom and the right is the top,
#the process then repeats until all the rows have been stacked
def collation_Sim(rows: int, columns: int,sheet):
    sheet_Length = len(sheet) - 1
    collation = []
    rows_Per_Column = random.randint(3, 5)
    row_To_Stop = rows_Per_Column
    current_Row = 0
    while current_Row <= rows - 1:
        current_Column = 0
        while current_Column <= columns - 1:
            for i in range(row_To_Stop - current_Row):
                collation.append(sheet[sheet_Length - (((current_Row + 1) * (columns)) + current_Column + 1)])
                current_Row += 1
            current_Column += 1
            current_Row = row_To_Stop - rows_Per_Column
        current_Row = row_To_Stop
        rows_Per_Column = random.randint(3, 5)
        row_To_Stop = row_To_Stop + rows_Per_Column
        if row_To_Stop > rows:
            rows_Per_Column = rows - (row_To_Stop - rows_Per_Column)
            row_To_Stop = rows
    return collation

# Creates a booster pack and saves it to a json file
def export_play_booster(set_code: str):
    # Makes set_code case-insensitive
    set_code = set_code.casefold()
    # Makes the booster pack
    booster = make_play_booster(set_code)

    # Creates a unique filename, so you don't overwrite any boosters you've made
    time_now = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    JSON_NAME = f"boosters/{set_code} Booster {time_now}.json"

    # Saves the booster pack to a json file
    with open(JSON_NAME, 'w', encoding='utf-8') as file:
        # json.dump([card for card in booster], file, indent=4, ensure_ascii=False)
        json.dump(booster, file)

    print(f'Exported Booster Pack to {JSON_NAME}')

#The Clayton booster function, uses lower_sets and casefold to be case insensitive
def make_clayton_booster(set_code: str, booster_type: str) -> list[dict] | None:
    #Makes set_code and booster_type case-insensitive
    set_code = set_code.casefold()
    booster_type = booster_type.casefold()
    # This checks if the provided set_code is a valid set
    if set_code not in sets.values():
        #Raise an Exception if the set_name is invalid
        raise Exception(f"Invalid set set code: {set_code}")
    else:
        match booster_type:
            case 'play':
                #Call the make play booster function, case insensitive
                return make_play_booster(set_code)

        #Raise an exception if the booster_type is invalid
        raise Exception(f"Invalid booster type: {booster_type}")

#This will only run when you run this file, before it was running it whenever make_booster or clayton_booster were used in another file
if __name__ == '__main__':
    #Examples
    #print(sets)
    #print(make_play_booster('dft'))
    b = make_clayton_booster('dft', 'play')
    with open('test.json', 'w') as outfile:
        json.dump(b, outfile, indent=4)
    #print(get_cards_in_set('war'))
    #print(get_cards_in_set(sets['Guilds of Ravnica']))
    #print(make_Card_Sheet_Common('Aetherdrift'))
    print(make_play_booster('blb'))

    #hi