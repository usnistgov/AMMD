README
06/09/2017

program: bulk_upload.py

author(s): 
	Philippe Dessauw, 
	Benjamin Long

history:
    05/2017    - created by PD
    06/09/2017 - modified by BJL to accomodate complete-reload and database-clearing scenarios

usage: 
  
  python bulk_upload.py <xsd_filename> <xsd_dirname> <xml_dirname> <scenario=1..3>
    
	- supports the following scenarios:
        
		scenario 1. load-all-xml-and-xsd: bulk upload of both schema and xml files for the first time
            
			EXAMPLE: 
				$ python bulk_upload.py am_schema_R1.xsd schema xmlFiles 1

        
		scenario 2. reload-all-xml-and-xsd: remove existing schema/xml-files and reload schema/xml files 
		           (for case when set of xml files has changed)
            
			EXAMPLE: 
				$ python bulk_upload.py am_schema_R1.xsd schema xmlFiles 2
               
			   NOTE: This removes all existing xml files from database.

        
		scenario 3. remove-xsd-and-all-xml-only: removes existing schema/xml-files only.
            
			EXAMPLE: 
				$ python bulk_upload.py am_schema_R1.xsd schema xmlFiles 3
				