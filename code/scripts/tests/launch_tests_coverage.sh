#!/bin/bash
coverage run --source=mgi,api,user_dashboard,explore_tree,schema_viewer,utils/XSDhash ./manage.py test mgi/ api/ user_dashboard/ explore_tree/ schema_viewer/ utils/XSDhash/ --liveserver=localhost:8082 --no-selenium

