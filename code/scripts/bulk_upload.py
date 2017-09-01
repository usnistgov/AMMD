""" Script to import all AM data into a Curator Core architecture
program: bulk_upload.py
author(s): Philippe Dessauw, Benjamin Long
history:
    05/2017    - created by PD
    06/09/2017 - modified by BJL to accomodate complete-reload and database-clearing scenarios
description:
    - supports the following scenarios
        1. load-all-xml-and-xsd:   bulk upload of both schema and xml files for the first time
        2. reload-all-xml-and-xsd: remove existing schema/xml-files and reload schema/xml files (for case when set of xml files has changed)
            WARNING: This removes all existing xml files from database, and thus, may not be desired.
               NOTE: The 3rd option is usually preferred to this one; instead of removing all + re-uploading a new
                     set of xml files, just upload the new/different set of xml files
        3. remove-xsd-and-all-xml-only: removes existing schema/xml-files only.
"""
from os.path import join
from os import listdir
import requests
import json
import sys
from pymongo import MongoClient

# Script parameters
from rest_framework.status import HTTP_201_CREATED


def get_schema_id( xsd_fname='am_schema_R1.xsd' ):
    user_name = "admin"
    user_pwd = "admin"
    mdcs_url = "http://127.0.0.1:8000"
    c={'host':'localhost:27017','db':'mgi','username':'mgi','password':'mgi','options':'w=1'}
    client = MongoClient('mongodb://{username}:{password}@{host}/{db}?{options}'.format(**c))
    db = client.mgi
    r = db.template.find_one({'filename':xsd_fname})
    if ( r==None):
        print '- error: requested schema [' + str(xsd_fname) + '] does not exist in database'
        results = db.template.find()
        if ( results != None ):
            if ( len(results) != 0 ):
                print '  - here is a list of all available schemas that are in the database:'
                for r in results:
                    if ( r==None ): continue
                    print '     filename = ' + str(r['filename'])
                    print '     _id      = ' + str(r['_id'])
                    print '     version  = ' + str(r['version'])
                    print '     hash     = ' + str(r['hash'])
                    print ' --- '
            else:
                print '- status: there are currently no schemas in the database.'
        print '- status: done.'
        exit()
    else:
        if ( '_id' ) in r:
            return r['_id']['$oid']
        else:
            print '- status: there are currently no schemas'
            print '- status: done.'
            exit()

def process( scenario=1, xsd_fname='am_schema_R1.xsd', xsd_dirname='schema', xml_dirname='xmlFiles'):

    print '- status: executing scenario ['+str(scenario)+']'

    user_name = "admin"
    user_pwd = "admin"
    mdcs_url = "http://127.0.0.1:8000"
    template_upload_url = "/rest/templates/add"
    xml_upload_url = "/rest/curate"

    xsd_filename = xsd_fname
    xsd_data_filepath = join(xsd_dirname, xsd_filename)
    xml_data_dirpath = xml_dirname
    template_id = ''

    if ( scenario==2 or scenario==3 ):
        # remove entries from DB
        print '- status: removing schema and xml-files from database'
        c={'host':'localhost:27017','db':'mgi','username':'mgi','password':'mgi','options':'w=1'}
        client = MongoClient('mongodb://{username}:{password}@{host}/{db}?{options}'.format(**c))
        db = client.mgi
        result = db.template.remove({})
        result = db.template_version.remove({})
        result = db.xmldata.remove({})

        if ( scenario == 3 ):
            return

    if ( scenario==1 or scenario==2):
        # Uploading AM curation schema
        print '- status: opening schema file [' + str(xsd_filename) + ']'
        with open(join(xsd_data_filepath), "r") as template_file:
            template_content = template_file.read()

            url = mdcs_url + template_upload_url
            data = {
                "title": "am_schema",
                "filename": xsd_filename,
                "content": template_content
            }

            print '- status: uploading schema'
            response = requests.post(url, data, auth=(user_name, user_pwd))
            response_code = response.status_code
            response_content = json.loads(response.text)

            print '- status: getting schema id'
            template_id = str(response_content['_id']['$oid'])

            if response_code == HTTP_201_CREATED:
                print "AM schema has been uploaded"
            else:
                raise Exception("A problem occured when uploading the schema (Error " + response_code + ")")

    if ( scenario==1 or scenario==2 ):
        # Uploading all XML data
        print '- status: uploading xml files from xml path [' + xml_dirname + ']'
        for xml_filename in listdir(xml_data_dirpath):
            with open(join(xml_data_dirpath, xml_filename), "r") as xml_file:
                xml_content = xml_file.read()

                url = mdcs_url + xml_upload_url
                data = {
                    "title": xml_filename,
                    "schema": template_id,
                    "content": xml_content
                }
                print '- status: curating/uploading xml file [' + str(xml_filename) + ']'
                response_str = requests.post(url, data, auth=(user_name, user_pwd))
                response_code = response_str.status_code
                response = json.loads(response_str.text)

                if response_code == HTTP_201_CREATED:
                    print '- status: ' + response["title"] + " has been uploaded"
                else:
                    print '- error: ' + "Upload failed with status code " + str(response_code) + ": " + response["message"]

def main(argv):

    if ( len(argv) < 5 ):
        print '''
USAGE: python bulk_upload.py <xsd_filename> <xsd_dirname> <xml_dirname> <scenario=1..3>
    - supports the following scenarios:
        scenario 1. load-all-xml-and-xsd: bulk upload of both schema and xml files for the first time
            EXAMPLE: python bulk_upload.py am_schema_R1.xsd schema xmlFiles 1

        scenario 2. reload-all-xml-and-xsd: remove existing schema/xml-files and reload schema/xml files (for case when set of xml files has changed)
            EXAMPLE: python bulk_upload.py am_schema_R1.xsd schema xmlFiles 2
               NOTE: This removes all existing xml files from database.

        scenario 3. remove-xsd-and-all-xml-only: removes existing schema/xml-files only.
            EXAMPLE: python bulk_upload.py am_schema_R1.xsd schema xmlFiles 3
        '''
        return
    else:
        # 0             1               2             3             4
        #bulk_upload.py <xsd_filename> <xsd_dirname> <xml_dirname> <scenario=1..3>
        process(scenario=int(argv[4]),xsd_fname=argv[1],xsd_dirname='schema',xml_dirname='xmlFiles')

    print '- status: done.'

if ( __name__ == '__main__' ):
    main(sys.argv)