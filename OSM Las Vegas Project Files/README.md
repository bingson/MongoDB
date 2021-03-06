# MongoDB Data Wrangling Project

>Choose any area of the world in https://www.openstreetmap.org and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap (OSM) data for a part of the world that you care about. 

For this project I chose Las Vegas because it’s a medium sized city famous for its many casinos, providing readily available reference information that I can use to check OSM accuracy and completeness. 

### Contents

##### P3_Vegas_OSM_DataWrangling_Project.pdf
* description of cleaning methods
* overview of data
* ideas for using geospatial data

##### 0_create_sample_osm.py

* creates smaller OSM file for testing/debugging purposes.

##### 1_audit_data.py
* assorted auditing functions to find errors in crowdsourced OSM data
* creates text files summarising audit data (e.g. tag_audit.txt)

##### 2_clean_and_convert_data.py 
* convert from OSM XML data to JSON format and upload to a MongoDB database
* contains cleaning routines to fix problems identified in the audit step. 

##### 3_mongo_queries.py
* assorted mongoDB querries summarising the cleaned json file.



