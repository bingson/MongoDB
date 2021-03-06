#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
      
- if second level tag "k" value contains problematic characters, it should be ignored

- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
  
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]  
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
double_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
node_labels = ["id", "type", "visible"]
tag_labels = ["amenity", "cuisine", "name", "phone"]
pos_label = ["lat", "lon"]

def shape_element(element):
    node = {}
    node['created'] = {}
    node['pos'] = []
    node['address'] = {}
    node['node_refs'] = []
    

    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag 

        # first level tag processing
        keys = element.attrib.keys()
        for label in node_labels:
            if label in keys: node[label] = element.attrib[label]
        for label in pos_label:
            if label in keys: node['pos'].append(float(element.get(label)))
        for label in CREATED:   
            if label in keys: node['created'].update({label:element.get(label)})
          
        # tag children processing
        for item in element:
            if item.tag == "nd": node["node_refs"].append(item.get('ref'))          
            elif item.tag == "tag":
                k = item.get('k')
                if re.search(problemchars,k): continue             
                elif "addr:" in k.strip()[0:5]:
                    if re.search(double_colon,k): continue
                    node['address'].update({k[5:]:item.get('v')})
            else:
                for label in tag_labels:
                    if label == k: node[label] = item.get('v') 
                        
        # housekeeping to remove empty dictionaries or arrays
        if len(node['pos']) == 0: del node['pos']         
        if len(node['created']) == 0: del node['created']  
        if len(node['address']) == 0: del node['address']
        if len(node['node_refs']) == 0: del node['node_refs']
        
        return node
    else:  
        return None
        
def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in) # adds json to input file name
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

def test(): 
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('L6-5_example.osm', True)
    pprint.pprint(data)
    

if __name__ == "__main__":
    test()


'''