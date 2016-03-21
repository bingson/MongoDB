#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
#import pprint
import re
import codecs
import json
#from collections import defaultdict

### Global Variables
# edit to alter cleaning behavior
apt_num = re.compile(r'(Suite|Ste)\s?([-0-9A-Z]+)')
addr_num = re.compile(r'([0-9]+)[^a-z]\s?')
no_prefix_num = re.compile(r'[0-9]')
postcode_num = re.compile('\d\d\d\d\d')
state_name = re.compile(r'nv|nevada', re.IGNORECASE) 
ave_pattern = re.compile(r'\s?Ave\.?\s|\sAve\.?$') 
blvd_pattern = re.compile(r'\s?Blvd\.?\s|\sBlvd\.?$') 
st_pattern = re.compile(r'\s?St\.?\s|\sSt\.?$')
rd_pattern = re.compile(r'\s?Rd\.?\s|\sRd\.?$')
dr_pattern = re.compile(r'\s?Dr\.?\s|\sDr\.?$')
ln_pattern = re.compile(r'\s?Ln\.?\s|\sLn\.?$')
mt_pattern = re.compile(r'\s?Mt\.?\s|\sMt\.?$')
pkwy_pattern = re.compile(r'\s?Pkwy\.?\s|\sPkwy\.?$')
s_pattern = re.compile(r'\s?(?<!\S)S\.?\s|\s(?<!\S)S\.?$')
n_pattern = re.compile(r'\s?(?<!\S)N\.?\s|\s(?<!\S)N\.?$')
w_pattern = re.compile(r'\s?(?<!\S)W\.?\s|\s(?<!\S)W\.?$')
e_pattern = re.compile(r'\s?(?<!\S)E\.?\s|\s(?<!\S)E\.?$')
east_pattern = re.compile(r'(East[^\w]|East$)')
west_pattern = re.compile(r'(West[^\w]|West$)')
south_pattern = re.compile(r'(South[^\w]|South$)')
north_pattern = re.compile(r'(North[^\w]|North$)')
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
double_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# edit to alter json element creation
created = ["version", "changeset", "timestamp", "user", "uid"] # choose which tag attributes are transferred to json file
node_labels = ["id", "type"]
tag_labels = ["amenity", "cuisine", "name", "phone", "website", "opening_hours"]
pos_labels = ["lat", "lon"]
case_ignore = ['MMS', 'NV', 'AZ', 'a', 'an', 'of', 'the', 'is', 'AFB', 'RTC', 'US'] # exceptions for capitalize_first_letter function


def shape_element(element):
    '''
    cleans data constructs the json datafile with the processed data.
    
    '''
    # initialize desired json node architecture
    node = {}
    node['created'] = {}
    node['pos'] = []
    node['address'] = {}
    node['node_refs'] = []
    if element.tag == "node" or element.tag == "way":
        
        # tag processing
        node['type'] = element.tag 
        keys = element.attrib.keys()
        for item in node_labels:
            if item in keys: node[item] = element.attrib[item]  # assigns value from corresponding key
        for item in pos_labels:
            if item in keys: node['pos'].append(float(element.get(item)))
        for item in created:   
            if item in keys: node['created'].update({item:element.get(item)})
                
        # tag child processing
        for item in element:
            if item.tag == "nd" : node["node_refs"].append(item.get('ref'))          
            elif item.tag == "tag":
                k = item.get('k')
                v = item.get('v')
                if re.search(problemchars,k): continue             
                elif k.startswith("addr:"):
                    if re.search(double_colon,k): continue 
                    elif k.endswith("street"): 
                        cleaned_data, node = update_street(v, node)
                        if len(cleaned_data) > 0 : node['address'].update({"street" : cleaned_data}) 
                    elif k.endswith("city"): 
                        cleaned_data, node = update_city(v, node)
                        if len(cleaned_data) > 0 : node['address'].update({"city" : cleaned_data})
                    elif k.endswith("postcode"): 
                        cleaned_data, node = update_postcode(v, node)
                        if len(cleaned_data) > 0 : node['address'].update({"postcode" : cleaned_data})
                    elif k.endswith("state"): 
                        cleaned_data, node = update_state(v, node)
                        if len(cleaned_data) > 0 : node['address'].update({"state" : cleaned_data})
                    elif k.endswith("housename"): 
                        cleaned_data, node = update_housename(v, node)
                        if len(cleaned_data) > 0 : node['address'].update({"housename" : cleaned_data})
                    elif k.endswith("housenumber"): 
                        cleaned_data, node = update_housenumber(v, node)
                        if len(cleaned_data) > 0 : node['address'].update({"housenumber" : cleaned_data})
                    else: 
                        node['address'].update({k[5:] : v})
                else:
                    for item in tag_labels:
                        if item == k: node[item] = v 
                        
        # remove empty dictionaries or arrays
        if len(node['pos']) == 0 : del node['pos']         
        if len(node['created']) == 0 : del node['created']  
        if len(node['address']) == 0 : del node['address']
        if len(node['node_refs']) == 0 : del node['node_refs']
            
        return node
        
    else: return None

    
def capitalize_first_letter(s, exceptions):
    '''
    The cleaning function capitalizes the first letter of each word in the input string 
    (while other letters are converted to lower case)  as long as the word does not appear 
    in the exceptions array. Words that appear in the exceptions array will remain unaltered.
    '''
    word_list = re.split(' ', s)       
    formatted_word_list = []
    for i in word_list:
        try:
            if i in exceptions or i[0].isdigit(): formatted_word_list.append(i) # i[0].isdigit() -> exclude '3rd' or '4th' street elements
            else: formatted_word_list.append(i[0].upper() + i[1:].lower())
        except: continue
    return " ".join(formatted_word_list)
    

def capture_numbers(string, node): 
    '''
    Suite and building numbers were in the street field. For uniformity, I moved this 
    data into new address sub fields.
    '''
    string = string.strip()
    if re.search(apt_num, string): 
        orig1 = string
        apt_data = re.search(apt_num, string).group()
        string = string.replace(apt_data, '')
        string = string.strip('.,# ')
        clean_apt_num = apt_data.strip('Suite')
        node['address'].update({'captured_suite_num' : clean_apt_num})
        print "(new suite number) " + orig1 + " -> " + clean_apt_num
    if re.search(addr_num, string):
        orig2 = string
        if "Highway" not in string: 
            streetnumber = re.search(addr_num, string).group().strip()
            node['address'].update({'captured_addr_num' : streetnumber}) # check if this number refers to a suite or house number
            string = string.replace(streetnumber, '')
            string = string.strip('#.,')
            print "(new address number) " + orig2 + " -> " + streetnumber
            return string, node
    else: 
        return string, node
    return string, node
  
  
def update_street(street_addr, node, housename = 0):
    '''
    conducts a variety of cleaning and replacement functions for addr:street values
    '''
    capitalized = capitalize_first_letter(street_addr, case_ignore)
    cleaned_data, node = capture_numbers(capitalized, node) # save and reassign apt, suite, or housenumber contained in street value
    address_buffer = blvd_pattern.sub(r' Boulevard ', cleaned_data)
    address_buffer = ave_pattern.sub(r' Avenue ', address_buffer)
    address_buffer = st_pattern.sub(r' Street ', address_buffer)
    address_buffer = rd_pattern.sub(r' Road ', address_buffer)
    address_buffer = dr_pattern.sub(r' Drive ', address_buffer)
    address_buffer = ln_pattern.sub(r' Lane ', address_buffer)
    address_buffer = mt_pattern.sub(r' Mount ', address_buffer)
    address_buffer = pkwy_pattern.sub(r' Parkway ', address_buffer)
    address_buffer = s_pattern.sub(r' South ', address_buffer)
    address_buffer = n_pattern.sub(r' North ', address_buffer)
    address_buffer = w_pattern.sub(r' West ', address_buffer)
    address_buffer = e_pattern.sub(r' East ', address_buffer)  
    address_buffer = move_direction(address_buffer)
    address_buffer = re.sub('\s+', ' ', address_buffer) 
    address_buffer = address_buffer.strip()
    if housename == 1 and address_buffer != street_addr: print "[update_housename] ", street_addr +" -> "+ address_buffer
    elif address_buffer != street_addr: print "[update_street] ", street_addr +" -> "+ address_buffer
    return address_buffer, node
    
    
def update_city(city_string, node):
    '''
    Captures state information in addr:city
    then fixes inconsistent capitalization
    '''
    city_no_state, node = update_state_second_source(city_string, node)
    cleaned_city_string = capitalize_first_letter(city_no_state, case_ignore).strip(',. ')
    if cleaned_city_string != city_string: print "[update_city] ", city_string +" -> "+ cleaned_city_string
    return cleaned_city_string, node


def update_postcode(postcode_string, node):
    '''
    Captures state information in addr:postcode
    and uses regular expression to find a 5 digit match for the postal code value, 
    then strips the rest
    '''
    postcode_no_state, node = update_state_second_source(postcode_string, node)
    cleaned_postcode_string =  re.search(postcode_num, postcode_no_state).group()
    if cleaned_postcode_string != postcode_string: print "[update_postcode] " + postcode_string + " -> " + cleaned_postcode_string
    return cleaned_postcode_string, node


def update_state(state_string, node):
    '''
    standardizes state values to two letter abbreviations such as NV or AZ
    '''
    cleaned_state_string =  state_string.upper().replace('NEVADA', 'NV')
    if cleaned_state_string != state_string: 
        print "[update_state] "+ state_string + " -> "+ cleaned_state_string
    return cleaned_state_string, node
 
   
def update_state_second_source(tgt_string, node):
    '''
    Scrapes input string for state data
    '''
    orig = tgt_string
    if re.search(state_name, tgt_string): 
        state_label = re.search(state_name, tgt_string).group()
        tgt_string = tgt_string.replace(state_label, '')
        node['address'].update({'state' : 'NV'})
        print "(new state) " + orig + " ->  NV"
    return tgt_string, node


def update_housename(housename, node):
    '''
    reuses update_street cleaning function and removes duplicate information if already contained in street
    '''
    cleaned_housename, node = update_street(housename, node, 1)
    try:
        if cleaned_housename in node['address']['street'] and len(cleaned_housename) > 5: 
            print "[update_housename] " + cleaned_housename + " -> *del duplicate street value in housename"
            return "", node
        else: return cleaned_housename, node
    except: return cleaned_housename, node
    
    
def update_housenumber(housenumber, node):
    '''
    cleans value and deletes duplicate value if already contained in housenumber.
    '''
    cleaned_data = housenumber.strip('# ')
    try:    
        if 'captured_addr_num' in node['address'].keys(): 
            if cleaned_data == node['address']['captured_addr_num']:
                del node['address']['captured_addr_num']
                print "[update_housenumber] " + cleaned_data + " -> *delete duplicate captured_addr_num"
            return cleaned_data, node
        else: return cleaned_data, node
    except: return cleaned_data, node


def move_direction(string):
    '''
    Moves direction prefixes (North, South, East, West) to the beginning of the string
    '''
    if re.search(east_pattern, string): string = "East " + east_pattern.sub(r'', string)
    if re.search(west_pattern, string): string = "West " + west_pattern.sub(r'', string)
    if re.search(south_pattern, string): string = "South " + south_pattern.sub(r'', string)
    if re.search(north_pattern, string): string = "North " + north_pattern.sub(r'', string)
    else: return string
    return string

def process_map(file_in, pretty = False):
    '''
    writes json file
    '''
    file_out = "{0}.json".format(file_in) 
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


if __name__ == "__main__":
#    data = process_map('test.osm', True)
#    data = process_map('las-vegas_nevada.osm', True)
    data = process_map('vegas_sample_region.osm', True)
