# MDCS Settings

This document provides a list of settings specific to the MDCS. Additional information regarding settings can be found on the Django documentation and on the documentation of individual python packages.

## General Settings

**MDCS_URI:** *http://127.0.0.1:8000*

URI of the server.

**USE_EMAIL:** *True|False*

If True, emails will be triggered:

- By the request account feature (request, accept, deny).
- Enabling of the 'Reset Password' feature. The user will receive directions to reset their password in an email.

## MongoDB

**MONGO_MGI_USER:**

Set the user used by Django to connect to MongoDB.

**MONGO_MGI_PASSWORD:**

Set the password used by Django to connect to MongoDB.

**MGI_DB:**

Set the name of the collection used to store MDCS data.

**MONGODB_URI:**

Set the MongoDB connection URI.


## BLOB Hoster

**BLOB_HOSTER:** *GridFS*

Set the system that will host the large files.

**BLOB_HOSTER_URI:**

Set the URI of the server where the BLOB Hoster is running.

**BLOB_HOSTER_USER:**

Set the user to connect to the BLOB Hoster.

**BLOB_HOSTER_PSWD:**

Set the password to connect to the BLOB Hoster.


## Background Task

**USE_BACKGROUND_TASK:** *True|False*

If True:

- Use of Celery to send emails in background rather than synchronously.
- Enabling of the background harvesting for OAI-PMH.


## Template Customization

**CUSTOM_TITLE:**

Change the main title.

**CUSTOM_SUBTITLE:**

Change the subtitle.

**CUSTOM_ORGANIZATION:**

Change the name of the organization. 

**CUSTOM_URL:** 

Change the organization website URL.

**CUSTOM_NAME:**

Change the name of the application.

**CUSTOM_DATA:**

Change the name of the data stored in the system.

**CUSTOM_CURATE:**

Change the name of the 'Curate' section.

**CUSTOM_EXPLORE:**

Change the name of the 'Explore' section.

**CUSTOM_COMPOSE:**

Change the name of the 'Compose' section.


## OAI-PMH

**OAI_ADMINS:**

List of OAI-PMH administrators.

**HOST:**

IP of the Data Provider.

**OAI_HOST_URI:** *MDCS_URI*

URI of the Data Provider.

**OAI_NAME:** *CUSTOM_NAME + HOST*

Name of the Data Provider.

**OAI_DELIMITER:**:

OAI-PMH delimiter.

**OAI_DESCRIPTION:**

Description of the Data Provider.

**OAI_GRANULARITY:** *YYYY-MM-DDThh:mm:ssZ*

The finest harvesting granularity supported by the repository. 

**OAI_PROTOCOLE_VERSION:** *2.0*

the version of the OAI-PMH supported by the repository.

**OAI_SCHEME:** *oai* *'OAI-PMH ' + CUSTOM_NAME*

OAI-PMH scheme.

**OAI_REPO_IDENTIFIER:**

OAI-PMH repository identifier.

**OAI_SAMPLE_IDENTIFIER:**

Example of identifier for this repository.

**OAI_DELETED_RECORD:** *no|persistent|transient*

Levels of support for deleted records:

- *no*: The repository does not maintain information about deletions.
- *persistent*: The repository maintains information about deletions with no time limit.
- *transient*: The repository does not guarantee that a list of deletions is maintained persistently or consistently.


## XSD PARSER

**PARSER_MIN_TREE:** *True|False*

- If True, the parser will only generate the first levels of the XML Schema. 
- If set to False, may not work for XML schemas using recursive definitions.

**PARSER_IGNORE_MODULES:** *True|False*

If True, the parser will not generate the modules set in the XML Schema.

**PARSER_COLLAPSE:** *True|False*

If True, the form will allow to collapse/expand sections.

**PARSER_AUTO_KEY_KEYREF:** *True|False*

- If True, lookups will be done during the parsing to register key/keyref elements. 
- Set to False if uploaded XML Schemas are not making use of key/keyref elements.

**PARSER_IMPLICIT_EXTENSION_BASE:** *True|False*

- If True, the parser will display the base type and its extensions when polymorphic extensions are used. 
- Set to False to only display extensions.

**PARSER_DOWNLOAD_DEPENDENCIES:** *True|False*

If True, the parser will download dependencies (include/import) to render them in the form.

