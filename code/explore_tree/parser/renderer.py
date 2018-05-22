################################################################################
#
# File Name: views.py
# Application: explore_tree/renderer
# Purpose:
#
# Author:
#         Philippe Dessauw
#         philippe.dessauw@nist.gov
#
#         Guillaume Sousa Amaral
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from os.path import join
from django.template import Context, Template
from explore_tree.api.navigation.views import navigation_get
import query
from mgi.settings import BASE_DIR
from utils.xml_utils.projection import get_projection
from collections import OrderedDict#, deque #
from itertools import izip#

TEMPLATES_PATH = join(BASE_DIR, 'explore_tree', 'parser', 'templates')

number_of_doc=0#
mytab=[]#

nav_table={}
li_table={}

def render_navigation(navigation, template_id):

    """
    Build the navigation tree
    :param navigation:
        - navigation root
        - template id
    :return:
    """
    nav_tree_html = ""
    for navigation_id in navigation.children:
        navigation_child = navigation_get(navigation_id)
        global number_of_doc
        number_of_doc = 0

        with open(join(TEMPLATES_PATH, 'li.html'), 'r') as li_file:
            li_content = li_file.read()
            li_template = Template(li_content)
            name = navigation_child.name.split('#')[1] if '#' in navigation_child.name else navigation_child.name
            # there is a projection, get documents from database
            if 'projection' in navigation_child.options and navigation_child.options['projection'] is not None:
                context = {
                    'branch_id': navigation_id,
                    #'branch_name': namee,
                    'branches': render_documents(navigation_child, template_id),
                    'branch_name': name + str(get_number_of_doc())
                }
            else:
                context = {
                    'branch_id': navigation_id,
                    'branch_name': str(get_number_of_node_doc(navigation_id,name)),
                    'branches': render_navigation(navigation_child, template_id)
                }
            global number_of_doc

            mytab.append((navigation_id,number_of_doc))

            if 'view' in navigation_child.options and navigation_child.options['view'] is not None:
                context["branch_view"] = "true"
            if "hidden" in navigation_child.options and navigation_child.options["hidden"]:
                context["hidden"] = True
            nav_tree_html += li_template.render(Context(context))
            global nav_table
            nav_table[navigation_id]=context
            global li_table
            li_table[navigation_id]=li_template

    return nav_tree_html


def get_html_tree(navigation,template_id):
    """
    Modify the name of the node by adding the number of documents under each node
    :param request:
        - navigation root
        - template id
    :return:
    """
    doc_dict = {}
    dashtable=[]
    nav_tree_html=''
    global mytab
    for t in mytab:
        navigation_child = navigation_get(t[0])

        if t[0] in dashtable:
            doc_dict[t[0]]+=t[1]
        else:
            doc_dict[t[0]]=t[1]
            dashtable.append(t[0])

    get_doc_by_nodes(navigation,doc_dict)

    global nav_table
    for k,v in nav_table.iteritems():

        if "(" in v['branch_name']:
            pass
        else:
            value = v['branch_name'] +" ("+ str(doc_dict[k])+ ")"
            v['branch_name'] = value
    nav_tree_html = render_html_tree(navigation,template_id,nav_table)

    return nav_tree_html

def render_html_tree(navigation,template_id,navigation_table):
    """
    Renders the navigation tree that contains the number of docs under each node of the tree
    :param request:
        - navigation root
        - template id
        - table with the id of the navigation nodes
    :return:
    """
    nav_tree_html=""
    for navigation_id in navigation.children:
        navigation_child = navigation_get(navigation_id)

        with open(join(TEMPLATES_PATH, 'li.html'), 'r') as li_file:
            li_content = li_file.read()
            li_template = Template(li_content)
            # there is a projection, get documents from database
            if 'projection' in navigation_child.options and navigation_child.options['projection'] is not None:
                navigation_table[navigation_id]['branches']=render_documents(navigation_child, template_id)#,navigation_table)
            else:
                navigation_table[navigation_id]['branches']= render_navigation(navigation_child, template_id)

            if 'view' in navigation_child.options and navigation_child.options['view'] is not None:
                navigation_table[navigation_id]["branch_view"] = "true"
            if "hidden" in navigation_child.options and navigation_child.options["hidden"]:
                navigation_table[navigation_id]["hidden"] = True
            nav_tree_html += li_template.render(Context(navigation_table[navigation_id]))

    return nav_tree_html

def render_documents(navigation, template_id):
    """
    Build the documents in the navigation tree
    :param request:
        - navigation root
        - template id
    :return:
    """
    doc_tree_html = ""
    doc_and_content=[]
    global number_of_doc
    number_of_doc = 0
    try:
        # Get the navigation id
        navigation_id = str(navigation.id)

        # Get projection
        projection = navigation.options['projection']
        navigation_child = navigation_get(navigation_id)

        # get filters from parents
        filters = []
        while True:
            # add filter to the list of filters
            if 'filter' in navigation.options and navigation.options['filter'] is not None:
                filters.append(navigation.options['filter'])

            # if no parent, stops the filter lookup
            if navigation.parent is None:
                break
            else:  # if parent, continue the filter lookup at the parent level
                navigation = navigation_get(navigation.parent)

        # get the documents matching the query
        documents = query.execute_query(template_id, filters, projection)

        #number_of_doc = 0
        for document in documents:
            with open(join(TEMPLATES_PATH, 'li_document.html'), 'r') as li_file:
                li_content = li_file.read()
                li_template = Template(li_content)

                branch_name = get_projection(document)
                context = {
                    'branch_id': document['_id'],
                    "parent_id": navigation_id,
                    'branch_name': branch_name,
                }

                doc_tree_html += li_template.render(Context(context))
            #    doc_and_content.append((doc_tree,li_template.render(Context(context))))
                global number_of_doc
                number_of_doc +=1
    except Exception, e:
        with open(join(TEMPLATES_PATH, 'li_error.html'), 'r') as li_file:
            li_content = li_file.read()
            li_template = Template(li_content)

        context = {
            "error_message": e.message
        }

        doc_tree_html = li_template.render(Context(context))
    return doc_tree_html

def get_leaf_name(document):
    """
    Get the name of the document
    :param request:
        - dict
    :return:
    """
    key = next(reversed(document))
    try:
        myliste = document[key].items()
        i = len(myliste)
        mysecondliste = myliste[i-1]
        j = len(mysecondliste)
        return mysecondliste[j-1]
    except:
        return document[key]

def get_number_of_doc():
    """
    Write the number of documents under a leaf (node that contains documents)
    :param request:
    :return:
    """
    global number_of_doc
    if number_of_doc!=0:
        return " ("+str(number_of_doc)+")"
    else:
        return " (0)"

def get_number_of_node_doc(id_node, name):
    """
    Write the number of documents under a node that contains other nodes
    :param request:
        - id node
        - name of the document
    :return:
    """
    try:
        return " "+str(nav_table[id_node]['branch_name'])
    except:
        return name

def get_doc_by_nodes(node, dico):
    """
    Recursive function that calculates the number of docs under each node of the tree
    :param request:
        - node
        - dict
    :return:
    """
    try:# Type(node)=Navigation
        if node.children:
            node_doc = sum([get_doc_by_nodes(child_id, dico) for child_id in node.children])
            dico[node.id] = node_doc
            return node_doc
        else:
            return dico[node.id]

    except:#node=ID of a Navigation object
        nav_child = navigation_get(node)
        if nav_child.children:
            node_doc = sum([get_doc_by_nodes(child_id, dico) for child_id in nav_child.children])
            dico[node] = node_doc
            return node_doc
        else:
            return dico[node]
