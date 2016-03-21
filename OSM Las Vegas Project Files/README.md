# MongoDB Data Wrangling Project

>Choose any area of the world in https://www.openstreetmap.org and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap (OSM) data for a part of the world that you care about. **See Project Grading Rubric [[link]](goo.gl/ITAEdv)**

For this project I chose the Las Vegas because it’s a medium sized city famous for its many casinos, providing readily available reference data I can use to check OSM accuracy and completeness. 

##### 0_create_sample_osm.py

* creates smaller OSM file for testing/debugging purposes.

##### 1_audit_data.py
* assorted auditing functions to find errors in crowd sourced OSM data
* creates text files that printout various auditing dictionaries (e.g. tag_audit.txt)

##### 2_clean_and_convert_data.py 
* convert from OSM XML data to JSON format 
* contains cleaning routines to fix problems identified in the audit step. See P3_Vegas_OSM_DataWrangling_Project.pdf for a description of the cleaning functions.

##### 3_mongo_queries.py
* assortment of mongoDB querries exploring the cleaned json file.



