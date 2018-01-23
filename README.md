# Additive Manufacturing Material Database

The Additive Manufacturing Materials Database (AMMD) is built using the NIST Material Data Curation System (MDCS) as a backend with structure provided by NIST’s AM schema. Providing a collaboration platform, the database is set to evolve through the open data access and material data sharing among the AM community. As data sets continue to accumulate, it becomes possible to establish new correlations between processes, materials, and parts.

The schema, or data structure, provides the backbone of the AMMD. The relationships created by the structure are essential to supporting meaningful data curation and data retrieval. As the AMMD matures through iterations, it is the data structure that will need to evolve to support the development of meaningful relationships that can be used to query the database.

Since part design information and test data are linked to individual builds, we structure the data sets into three types of main entities, as shown in Figure 1. The first entity type “amMaterial” captures vendor  material information. The second type of entity “amMachine” captures AM machine information. The data captured by these two types are independent of specific builds and can be provided by material vendors and machine owners. The third type of database entity “amBuild” captures the information related to a specific AM build, including part and specimen design, pre-process, in-process and post process information, as well as test information.

#Installation

To install and run the AMMD on your machine (also read ammd-v1.6.txt):

. Pick the instruction notes for your operating system, inside the docs folder,
. Follow the installation instructions,
. Make sure that the python packages and software that you are installing, match the versions listed in the document Required Python Packages and Required Software

