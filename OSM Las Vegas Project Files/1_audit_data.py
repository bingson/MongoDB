#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

### Global Variables

# lower = re.compile(r'^([a-z]|_)*$')
lower = re.compile(r'^([a-zA-Z0-9]|_|-)*$')
lower_colon = re.compile(r'^([a-zA-Z0-9]|_|-)*:([a-zA-Z0-9]|_|-)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
apt_num = re.compile(r'(#| suite | ste)\s?([0-9]+)', re.IGNORECASE)
# street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_type_re = re.compile(r'\S+\.', re.IGNORECASE)
all_tag_types = defaultdict(int)
tag_key_type = {"lower": 0, "lower_colon":  0, "problemchars": 0, "other": 0}
tag_value_set = defaultdict(set)
tag_count_set = defaultdict(int)
addr_parent_dict = defaultdict(int)
street_types = defaultdict(int)
way_fieldtypes_count = defaultdict(int)
node_fieldtypes_count = defaultdict(int)
nd_fieldtypes_count = defaultdict(int)
tag_fieldtypes_count = defaultdict(int)
tag_other_value_set = defaultdict(set) 
tag_other_count_set = defaultdict(int)
tag_other_fieldtypes_count = defaultdict(int)

### Audit Functions
def audit_elements(element):
    ''' 
    audit_fieldtypes() counts the occurence of datatypes within the values associated
    with each attribute key.
    
    Sample output
    =============
    ("key attribute name<dtype of value attribute>", frequency count)
    e.g. "Node"
        ("timestamp<type 'str'>", 8975)
        ("changeset<type 'int'>", 8975)
        ("user<type 'str'>", 8975)
        ("id<type 'int'>", 8975)
        ("version<type 'int'>", 8975)
        ("uid<type 'int'>", 8975)
    
    '''     
    if element.tag == "way":
        for attribute in element.attrib.items(): # attribute[0] = key, attribute[1] = value
            fieldtype = get_fieldtype(attribute[1])
            way_fieldtypes_count[attribute[0] + str(fieldtype)] +=1
            for item in element: audit_tag_child(item)
            
    if element.tag == "node":
        for attribute in element.attrib.items(): 
            fieldtype = get_fieldtype(attribute[1])
            node_fieldtypes_count[attribute[0] + str(fieldtype)] +=1
            for item in element: audit_tag_child(item)
            
    if element.tag == "nd":
        for attribute in element.attrib.items(): 
            fieldtype = get_fieldtype(attribute[1])
            nd_fieldtypes_count[attribute[0] + str(fieldtype)] +=1
            
    return nd_fieldtypes_count, node_fieldtypes_count, way_fieldtypes_count
            
            
def audit_tag_child(element):
    '''
    For valid tags (filtered through regular expression matches or for loop constraints) 
    creates two dictionaries: one for the set of values and another for the frequency of 
    those values. 
    
    Both dictionaries can be passed to the create_audit_file function to produce 
    a audit text file to help survey the data. See create_audit_file for more details
    
    Sample output
    =============
    
    tag_value_set:
    ('addr:state',  set(['CA', 'AZ', 'nv', 'NV', 'Nevada']))

    tag_count_set:
    defaultdict(<type 'int'>, {'CA' : 18, 'AZ' : 32, 'nv' : 8, 'NV' : 2310, 'Nevada' : 44})
    
    '''
    
    if element.tag == "tag" or element.tag == "way":
        
#        lower_query = ["name", "amenity"]
        lower_query = [] # change to choose what data to audit
        lower_colon_query = ["addr"] # change to choose what data to audit
        k = element.get("k")
        v = element.get("v")
        
        if re.search(lower,k): 
            tag_key_type['lower'] +=1
            for c in lower_query:
                if c in k :
                    tag_value_set[k].add(v)  # gather unique values
                    tag_count_set[v] += 1
                    
        elif re.search(lower_colon,k):
            tag_key_type['lower_colon'] += 1
            if is_street_name(element): audit_street_type(street_types, v)
            for c in lower_colon_query:
                if c in k: 
                    tag_value_set[k].add(v)  # gather unique values
                    tag_count_set[v] += 1
#                    tag_value_set[k].add(type(v))  # creates a set of datatypes 
#                    tag_count_set[type(v)] += 1
                    
        elif re.search(problemchars,k): 
            tag_key_type['problemchars'] += 1
            
        else: 
            tag_key_type['other'] +=1
            tag_other_value_set[k].add(v) 
            tag_other_count_set[v] += 1 
            fieldtype = get_fieldtype(v)
            tag_other_fieldtypes_count[k + str(fieldtype)] +=1
    
    return tag_value_set, tag_count_set, tag_other_value_set, tag_other_count_set, tag_other_fieldtypes_count


def create_audit_file(txt_fname, value_set, value_count, max_set_count = 20):
    '''
    creates a textfile of value counts for above defined tags from outputs of
    the audit_tag_child functions
    
    Sample output
    =============
    Frequency x value of k = addr:state
      18 x CA
      32 x AZ
      8 x nv
      2310 x NV
      44 x Nevada
    
    '''
    with open(txt_fname, 'w') as f:
        for a in value_set.items(): 
            title = "\nFrequency x value of k = %s\n" %(a[0])
            f.write(title)
            set_size = len(a[1])
            
            if max_set_count > set_size:            
                for b in a[1]:
                    try: f.write('  %s x %s\n' %(str(value_count[b]),str(b)))
                    except: f.write('  unwritable value\n')
            else: 
                count = 0
                for b in a[1]:
                    if count < max_set_count: 
                        try: f.write('  %s x %s\n' %(str(value_count[b]),str(b)))
                        except: 
                            f.write('  unwritable value\n')
                            print title
                            print '  %s x %s' %(value_count[b], b) 
                        count += 1
                    else: continue
                f.write(" *Showing first %s of larger set: %s max_set_count < %s set_size \n" %(max_set_count,max_set_count, set_size))
                continue
            
def get_fieldtype(field):
    '''
    returns the data type of input value
    '''
    if field in ['NULL', '']:
        return type(None)
    if field[0] == '{':
        return list
    try:
        int(field)
        return int
    except:
        try:
            float(field)
            return float
        except:
            return str


def audit_street_type(street_types, street_name):
    '''
    constructs a dictionary of street abbreviations and their frequencies
    
    Sample output
    =============
    
    Ave.: 38
    Blvd.: 26
    Dr.: 8
    E.: 22
    Ln.: 8
    Mt.: 8
    N.: 6
    S.: 32
    W.: 38
    '''
    m = street_type_re.search(street_name) 
    if m:
        street_type = m.group()
        street_types[street_type] += 1


def print_sorted_dict(d):
    '''
    prints dictionary in order of greatest value to least
    '''
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 
        
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")


def audit_data(filename):
    for _, element in ET.iterparse(filename):
        audit_elements(element)
        all_tag_types[element.tag] += 1
    count = 0    
    for i in tag_count_set.items():
        if count == 9:
            pprint.pprint(i)
        count += 1

            
    create_audit_file(r"tag_audit.txt", tag_value_set, tag_count_set) 
    create_audit_file(r"tag_other_audit.txt", tag_other_value_set, tag_other_count_set) 
    print_sorted_dict(street_types)
    
    
if __name__ == "__main__":
    audit_data('vegas_sample_region.osm')
#    audit_data('las-vegas_nevada.osm')
    
