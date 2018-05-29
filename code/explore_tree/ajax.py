""" Ajax calls for the exploration tree

"""
# -*- coding: utf-8 -*-
import json
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from explore_tree.api.models import Navigation, MyParser, MaxDepth, Node
from explore_tree.api.navigation.operations import retrieve_navigation_filters, get_navigation_node_for_document
from explore_tree.parser.renderer import get_projection#
from mgi.models import XMLdata
from mgi.models import Template#
from utils.json_parser.processview import processview, processviewdocidlist, process_cross_query, doc_to_query, ids_docs_to_query, ids_docs_to_querys
from parser import query
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.cache import caches

from xml.dom import minidom #
from xml.dom.minidom import parse, parseString, Document #
from lxml import etree#
import xml.etree.ElementTree as ET #
import xml.etree.cElementTree as ET#
from xml.etree.ElementTree import XMLParser, fromstring#,ElementTree

#from rest_framework.response import Response#
#from rest_framework import status#

#from cStringIO import StringIO##
#from django.core.servers.basehttp import FileWrapper##

#from mgi.models import find_content_by_id##

import collections
from collections import OrderedDict, deque #
from bson.objectid import ObjectId#

from itertools import izip, chain #
from copy import deepcopy#
from itertools import tee, izip

#from django.core import serializers##
#import random##
#import sys##
#from threading import Thread##
#import time

leaf_cache   = caches['leaf']
branch_cache = caches['branch']
link_cache   = caches['link']

my_result_to_dwld = []

list_of_ordered_dict = ''
list_of_ordered_dict_cross_docs = ''
my_listof_ordereddicts_tab = []
my_listof_ordereddicts_cross_docs_tab = []
query_and_results_tab = []
results_initial_doc = []
list_od_dwnld_files =[]
navigation_name_tab= []#''
my_tab = []
resultat = []


my_list_of_cross_results_f = []
my_list_of_tag_text_initialdoccurrent = []
mystring= "MYSTRINGG"
sz = 0

@cache_page(600 * 15)

# First function called when clicking on a document or a link in the tree
def load_view(request):
    """
    :param request:
    :return:
    """
    # nav_id parameter is mandatory, if it doesn't exist we delete other parameters to raise and error
    if "nav_id" not in request.POST:
        request.POST = {}

    node_id=''
    doc_id =''
    ref_node_id=''

    # if clicking on a document in the tree
    if "node_id" in request.POST and "doc_id" in request.POST:
        node_id = request.POST['node_id']
        doc_id  = request.POST['doc_id']
        leaf    = None
        nod_name = Navigation.get_name(node_id)
        indexx = (nod_name).rfind("#")
        node_name = nod_name[indexx+1:]
        c_id    = str(node_name) + '_' + str(doc_id)
        # Get the document from the cache if this one had ever been accessed
        if ( c_id in leaf_cache ):
            leaf = leaf_cache.get(c_id)
        # Else :Query the database, process the documents
        else:
            load_doc = load_leaf_view(request, doc_id)
            r = render(request, "explore_tree/components/view.html", load_doc)
            leaf_cache.set(c_id, r)
            leaf = r

        return leaf

    elif "node_id" in request.POST:
        node_id = request.POST['node_id']
        branch  = None

        if ( node_id in branch_cache ):
            branch = branch_cache.get(node_id)
        else:
            branch = __load_branch_view(request)
            branch_cache.set(node_id, branch)

        return  branch


    elif "ref_node_id" in request.POST and "doc_id" in request.POST:
        ref_node_id = request.POST['ref_node_id']
        doc_id      = request.POST['doc_id']
        c_id        = ref_node_id + '_' + doc_id
        link        = None

        if ( c_id in link_cache ):
            link = link_cache.get(c_id)
        else:
            link = __load_link_view(request)
            link_cache.set(c_id, link)
        return link

    else:
        error = {
            "message": "Request is malformed."
        }
        return HttpResponse(json.dumps(error), status=HTTP_400_BAD_REQUEST)

def load_leaf_view(request, docid):
    """ Load view for a leaf

    Parameters:
        -   request
        - doc id

    Returns:
    """

    navigation_name2=request.POST["node_id"]

    xml_document = XMLdata.get(docid)
    navigation_node = Navigation.objects.get(pk=request.POST["node_id"])

    # Display XML file if "projection_view" annotation is not configured
    if "projection_view" not in navigation_node.options:
        # TODO transform the XML into a data table
        return HttpResponse(json.dumps({}), HTTP_200_OK)

    projection_views = json.loads(navigation_node.options["projection_view"])

    view_data = {
        "header": xml_document.get("title"),
        "type": "leaf",
        "views": []
    }
    #Initialize parameters in order to download later some information
    my_listof_ordereddicts_cross_docs2 =[]
    query_and_results2 = []
    my_listof_ordereddicts2 = []
    resultat2 = []
    resultat3 = []
    my_list_of_cross_results = []
    # Send the annotation to the processor and collect the data
    for projection_view in projection_views:
        result_data = {
            "title": projection_view["title"],
            "data": None
        }

        # FIXME better handling of x-
        if "query" in projection_view.keys():

            my_projections = []
            # Get the names of the brakets which need to be displayed
            for value in projection_view["data"]:
                my_projections.append(value.get('path'))

            result_data["data"] = process_cross_query(request.POST["nav_id"], docid,
                                                      projection_view["query"], projection_view["data"])
            # Set the documents which must be queried
            doc_query_proc = {
                "_id": ObjectId(docid)
            }

            quiered_docs = doc_to_query(1)

            co_dict = {}

            for id_doc in quiered_docs:
                other_doc_query = {
                    "_id" : ObjectId(id_doc)
                }

                for projection in my_projections:

                    proj_co = {
                        my_projections[my_projections.index(projection)] : 1
                    }

                    res_co = XMLdata.executeQueryFullResult(other_doc_query,proj_co)

                    try:

                        doc_projco = get_projection(res_co[0])
                        s = str(my_projections[my_projections.index(projection)])
                        y = s.split(".")
                        attribute = y[len(y)-1]

                        result_cross = doc_projco
                        my_list_of_cross_results.append((attribute,result_cross))
                        global list_of_ordered_dict_cross_docs
                        list_of_ordered_dict_cross_docs = res_co
                        my_listof_ordereddicts_cross_docs2.append(res_co)
                        if "OrderedDict" in str(doc_projco):
                            pass
                        else:
                            querry_doc1 = query_and_results2[len(query_and_results2)-1]#.split(".")
                            querry_doc = (querry_doc1.split("."))
                            q_doc = querry_doc[len(querry_doc)-1]
                            resultat3.append((q_doc,doc_projco))
                    except:
                        res_co = ''

        else:
            my_projections = []
            for value in projection_view["data"]:
                my_projections.append(value.get('path'))
            id_doc_to_query = {
                "_id": ObjectId(docid)
            }

            for projection in my_projections:
                proj_co = {
                    my_projections[my_projections.index(projection)] : 1
                }

                res_co = XMLdata.executeQueryFullResult(id_doc_to_query,proj_co)
                query_and_results2.append(projection)
                try:
                    doc_projco = get_projection(res_co[0])
                    global list_of_ordered_dict
                    list_of_ordered_dict = res_co
                    my_listof_ordereddicts2.append(res_co)
                    results_initial_doc.append(doc_projco)

                    if "OrderedDict" in str(doc_projco):
                        pass
                    else:

                        querry_doc1 = query_and_results2[len(query_and_results2)-1]#.split(".")
                        querry_doc = (querry_doc1.split("."))
                        q_doc = querry_doc[len(querry_doc)-1]
                        resultat2.append((q_doc,doc_projco))
                except:
                    res_co = ''

            result_data["data"] = processview(request.POST["nav_id"], docid, projection_view["data"])
            my_result_to_dwld.append(result_data["data"])

        view_data["views"].append(result_data)
    my_node = str(get_node_name(navigation_name2))+"_"+str(request.POST["doc_id"])
    query_and_results_tab.append(query_and_results2)
    my_listof_ordereddicts_cross_docs_tab.append(my_listof_ordereddicts_cross_docs2)
    navigation_name_tab.append(navigation_name2)
    my_listof_ordereddicts_tab.append(my_listof_ordereddicts2)
    resultat.append(resultat2)

    my_list_of_cross_results_f.append(my_list_of_cross_results)
    my_tab.append(my_node)

    return view_data

def __load_branch_view(request):
    """ Load view for a branch

    :param request:
    :return:
    """
    # Retrieve the view annotation
    navigation_node = Navigation.objects.get(pk=request.POST["node_id"])
    filters = retrieve_navigation_filters(navigation_node)


    # FIXME modified query part to execute query directly
    documents = []
    query_documents = query.execute_query(filters, '{"_id": 1}')

    for query_doc in query_documents:
        documents.append(query_doc["_id"])
    # Display XML file if "projection_view" annotation is not configured
    if "view" not in navigation_node.options:
        error = {
            "message": "'cql:view' annotation does not exist for this branch."
        }

        return HttpResponse(json.dumps(error), HTTP_400_BAD_REQUEST)

    branch_views = json.loads(navigation_node.options["view"])

    name = navigation_node.name.split('#')[1] if '#' in navigation_node.name else navigation_node.name
    view_data = {
        "header": name,
        "type": "branch",
        "views": []
    }

    for branch_view in branch_views:
        result_data = {
            "title": branch_view["title"],
            "data": processviewdocidlist(request.POST["nav_id"], documents, branch_view["data"])
        }

        view_data["views"].append(result_data)

    return render(request, "explore_tree/components/view.html", view_data)


def __load_link_view(request):
    """ Load link view for a link

    :param request:
    :return:
    """
    ref_node_id = request.POST["ref_node_id"]


    reference_node = get_navigation_node_for_document(ref_node_id, request.POST["doc_id"])

    navigation_name2 = request.POST["ref_node_id"]#
    xml_document = XMLdata.get(request.POST["doc_id"])#
    try :
        if "projection_view" in reference_node.options and reference_node.options["projection_view"] is not None:
            projection_views = json.loads(reference_node.options["projection_view"])

            view_data = {
                "header": xml_document.get("title"),
                "type": "leaf",
                "views": []
            }

            my_listof_ordereddicts_cross_docs2 =[]#
            query_and_results2 = []#
            my_listof_ordereddicts2 = []#
            resultat2 = []
            resultat3 = []
            my_list_of_cross_results = []
            # Send the annotation to the processor and collect the data
            for projection_view in projection_views:
                result_data = {
                    "title": projection_view["title"],
                    "data": None
                }

                # FIXME better handling of x-queries
                if "query" in projection_view.keys():
                    my_projections = []#
                    # Get the names of the brakets which need to be displayed
                    for value in projection_view["data"]:#
                        my_projections.append(value.get('path'))#
                    result_data["data"] = process_cross_query(request.POST["nav_id"], request.POST["doc_id"],
                                                              projection_view["query"], projection_view["data"])
                    # Set the documents which must be queried
                    doc_query_proc = {
                        "_id": ObjectId(request.POST["doc_id"])
                    }

                    quiered_docs = doc_to_query(1)

                    co_dict = {}

                    for id_doc in quiered_docs:
                        other_doc_query = {
                            "_id" : ObjectId(id_doc)
                        }

                        for projection in my_projections:

                            proj_co = {
                                my_projections[my_projections.index(projection)] : 1
                            }

                            res_co = XMLdata.executeQueryFullResult(other_doc_query,proj_co)

                            try:

                                doc_projco = get_projection(res_co[0])
                                s = str(my_projections[my_projections.index(projection)])
                                y = s.split(".")
                                attribute = y[len(y)-1]

                                result_cross = doc_projco
                                my_list_of_cross_results.append((attribute,result_cross))
                                global list_of_ordered_dict_cross_docs
                                list_of_ordered_dict_cross_docs = res_co
                                my_listof_ordereddicts_cross_docs2.append(res_co)
                                if "OrderedDict" in str(doc_projco):
                                    pass
                                else:
                                    querry_doc1 = query_and_results2[len(query_and_results2)-1]#.split(".")
                                    querry_doc = (querry_doc1.split("."))
                                    q_doc = querry_doc[len(querry_doc)-1]
                                    resultat3.append((q_doc,doc_projco))
                            except:
                                res_co = ''
                else:
                    my_projections = []
                    for value in projection_view["data"]:
                        my_projections.append(value.get('path'))
                    id_doc_to_query = {
                        "_id": ObjectId(request.POST["doc_id"])
                    }

                    for projection in my_projections:
                        proj_co = {
                            my_projections[my_projections.index(projection)] : 1
                        }

                        res_co = XMLdata.executeQueryFullResult(id_doc_to_query,proj_co)
                        query_and_results2.append(projection)
                        try:
                            doc_projco = get_projection(res_co[0])
                            global list_of_ordered_dict
                            list_of_ordered_dict = res_co
                            my_listof_ordereddicts2.append(res_co)
                            results_initial_doc.append(doc_projco)
                            if "OrderedDict" in str(doc_projco):
                                pass
                            else:

                                querry_doc1 = query_and_results2[len(query_and_results2)-1]#.split(".")
                                querry_doc = (querry_doc1.split("."))
                                q_doc = querry_doc[len(querry_doc)-1]
                                resultat2.append((q_doc,doc_projco))
                        except:
                            res_co = ''
                    result_data["data"] = processview(request.POST["nav_id"], request.POST["doc_id"],
                                                      projection_view["data"])
                    my_result_to_dwld.append(result_data["data"])

                view_data["views"].append(result_data)

            my_node = str(get_node_name(navigation_name2))+"_"+str(request.POST["doc_id"])
            query_and_results_tab.append(query_and_results2)
            my_listof_ordereddicts_cross_docs_tab.append(my_listof_ordereddicts_cross_docs2)
            navigation_name_tab.append(navigation_name2)
            my_listof_ordereddicts_tab.append(my_listof_ordereddicts2)
            resultat.append(resultat2)

            my_list_of_cross_results_f.append(my_list_of_cross_results)
            my_tab.append(my_node)

            html_data = render(request, "explore_tree/components/view.html", view_data)
            doc_id = str(reference_node.pk) + "." + str(xml_document["_id"])

            return HttpResponse(json.dumps({"html": html_data.content, "doc_id": doc_id}), status=HTTP_200_OK)
        else:
            return HttpResponse(json.dumps({}), HTTP_200_OK)
    except:
        #"NOT FOUND"
    #else:
        return HttpResponse(json.dumps({}), HTTP_200_OK)

def download_file(request):
    """Return the xml tree in a string format

    :param request:
    :return:
    """
    xmlID = request.GET["doc_id"]
    xml = retrieve_xml(xmlID)
    return  etree.fromstring(xml)

def download_xml(request):
    """ Download the xml source file

    :param request:
    :return:
    """
    xmlID = request.GET["doc_id"]
    xmltree = retrieve_xml(xmlID)
    xml = etree.fromstring(xmltree)
    json_content = etree.tostring(xml,pretty_print=True)

    return HttpResponse(json_content, HTTP_200_OK)

def retrieve_xml(docID):
    """ Get the xml assiociated to the id

    :param request:
    :return:
    """
    xml_data = XMLdata.getXMLdata(docID)
    xml_dta = json.dumps(xml_data.items()[3][1],sort_keys=False)
    xml_d = json.loads(xml_dta, object_pairs_hook=OrderedDict) # Convert the ordered dict in dict
    xsdDocData = XMLdata.unparse(xml_d)
    xsdEncoded = xsdDocData.encode('utf-8')

    return xsdEncoded

def download_corrolated_xml(request):
    """ Download the displayed data

    :param request:
    :return:
    """
    alrdy_dwl = False
    index_i=''
    json_contents =""
    node_or_nav = str(get_node_name(request.GET["curent_node"]))+"_"+str(request.GET["doc_id"])
    try:
        j = my_tab.index(node_or_nav)

        my_listof_ordereddicts_cross_docs = my_listof_ordereddicts_cross_docs_tab[j]
        query_and_results = query_and_results_tab[j]
        listeof = my_list_of_cross_results_f[j]

        listeof = []
        lenliste = 0
        for l in my_list_of_cross_results_f:
            if lenliste == j:
                listeof = l
                break
            lenliste  +=1
        navigation_id = navigation_name_tab[j]

        navigation_name = get_node_name(navigation_id)
        my_listof_ordereddicts = my_listof_ordereddicts_tab[j]
        result_doc = resultat[j]
            #global listeof

        for i in list_od_dwnld_files:
            if i[0] == navigation_name and i[1] == request.GET["doc_id"]:
                alrdy_dwl = True
                index_i = list_od_dwnld_files.index(i)
                break
        if alrdy_dwl:
            #DOC has ever been dwld
            json_contents = list_od_dwnld_files[index_i][2]
        else:
            #DOC has never been dwld
            j2 = download_corrolated_xml_others_files(my_listof_ordereddicts_cross_docs,listeof)
            doc_name = request.GET["file_name"]
            xml = my_tree = download_file(request)
            liste_of_txt = getTexts(my_listof_ordereddicts)
            nb = 0
            for child in xml.iter():
                    #car = False
                if child.text=="":
                    pass
                else:
                    nb +=1
            pare = 0
            missing=liste_of_txt
            to_add=liste_of_txt

            for l in liste_of_txt:
                taken = False
                car= False
                for child in xml.iter():
                    if (child.tag == l[0]):
                        car = True
                        if (child.text == l[1]):
                        # or child.text.split() == l[1].split():
                            ct = child.text
                            child.text = mystring+ct
                            pare +=1
                            taken=True

            for child in xml.iter():
                b=''
                if child.text:
                    if (child.text)[0:9] == mystring:
                        pass
                    else:
                        child.text=b
            while (check_empty_nodes(xml)==True):
                remove_empty_nodes(xml)
            for child in xml.iter():
                if child.text:
                    if (child.text)[0:9] == mystring:
                        ancien = (child.text)[9:]
                        child.text = ancien

            xmle=xml
            y= etree.tostring(xmle,encoding='UTF-8')
            z = "<xml>\n"+y+j2+"</xml>"
            z = u''.join((z)).encode('utf-8')
            z = str(z)
            z = z.replace("\t","")
            z = z.replace("\n","")

            json_contentt = etree.fromstring(z)
            json_contents = etree.tostring(json_contentt, pretty_print=True,encoding='UTF-8', method="xml")
            list_od_dwnld_files.append((navigation_name,request.GET["doc_id"],json_contents))

        return HttpResponse(json_contents, HTTP_200_OK)
    except:
        json_contents = {'message':'No resource found.'}
        return HttpResponse(json_contents, status=status.HTTP_404_NOT_FOUND)


def download_corrolated_xml_others_files(L,listeof):
    """ Download the xml coming from the other querried documents

    :param request:
        - list
        - list
    :return:
    """
    global my_list_of_tag_text_initialdoccurrent
    my_list_of_tag_text_initialdoccurrent = listeof
    xml_files = []
    doc_ids = []
    json_contents = ''
    json_to_render=''
    docid_and_trees = []
    for ordereddict in L:
        xml_data = (ordereddict[0]).items()[1][1]
        xml_dta = json.dumps(xml_data)
        xml_d = json.loads(xml_dta)

        json_content = json2xml(xml_d)
        my_xml_string = str(json_content)
        my_tree = get_tree(my_xml_string)

        doc_ids.append((ordereddict[0]).items()[0][1])
        xml_files.append(json_content)
        docid_and_trees.append(((ordereddict[0]).items()[0][1],my_tree))

        json_contents = json_contents + '\n' + json_content

    if len(docid_and_trees)>1:
        for li in docid_and_trees:
            i = docid_and_trees.index(li)
            for lii in docid_and_trees[i+1:]:
                ii = docid_and_trees.index(lii)
                var_p = 0
                for child1, child2 in izip(li,lii):
                    if child1 == child2:
                        var_p +=1
                if var_p == len(li) & len(li) == len(lii):
                        del docid_and_trees[ii]
        table_id=[]
        my_ordered_xml_list = []
        lesdocsvus =[]
        for t1 in docid_and_trees:
            y=[]
            i = docid_and_trees.index(t1)
            already_see = False
            for tab in table_id:
                if tab == t1[0]:
                    already_see = True
            if already_see == False:
                table_id.append(t1[0])
                for t2 in docid_and_trees[i+1:]:
                    if t1[0] == t2[0]:
                        lesdocsvus.append(t1[0])
                        if y!=[]:
                            x = union_tree(t1[1],t2[1],verbose=False)
                            y = union_tree(y,x,verbose=False)
                        else:#Write for the first time
                            y = union_tree(t1[1],t2[1],verbose=False)
            if y:
                my_ordered_xml_list.append((t1[0],y))

        for t in docid_and_trees:
            if t [0] in lesdocsvus:
                pass
            else:
                my_ordered_xml_list.append((t[0],t[1]))

        if my_ordered_xml_list==[]:
            json_to_render = json_contents
        mytab_of_tree=[]
        for xml in my_ordered_xml_list:
            s = LTree_to_xml_string(xml[1])
            tree2 = etree.fromstring(s)
            i=1
            global sz
            if sz == 0:
                for child in tree2.iter():
                    if child.getchildren():
                        pass
                    else:
                        sz +=1
                listeof2 = listeof[:sz]
                fill_xml(tree2,listeof2)
            else:
                fill_xml(tree2,listeof[sz:])
                sz +=1
            mytab_of_tree.append((xml[0],tree2))

        for t in mytab_of_tree:
            checkandremove(t[1],listeof)
        for t in mytab_of_tree:
            json_to_render += etree.tostring(t[1])#, pretty_print=True)
    else:
        json_to_render = json_contents
    global sz
    sz = 0
    return json_to_render

def generate_xml(content):
    """ Create the xml associated to a string

    :param request:
        - string
    :return:
    """
    tree = etree.fromstring(content)
    return tree

def getTexts(L):
    """Return the tags and the texts for an xml object

    :param request:
        - OrderedDict
    :return:
    """
    listofcontents = []
    listoftexts = []
    listoftag_texts = []

    for ordereddict in L:
        xml_data = (ordereddict[0]).items()[1][1]
        xml_dta = json.dumps(xml_data)
        xml_d = json.loads(xml_dta)
        json_content = json2xml(xml_d)
        jsoncontent = u''.join((json_content)).encode('utf-8')
        jsoncontent = str(jsoncontent)
        jsoncontent = jsoncontent.replace("\t","")
        jsoncontent = jsoncontent.replace("\n","")
        listofcontents.append(jsoncontent)

    for l in listofcontents:
        my_tree = generate_xml(l)
        for child in my_tree.getiterator():
            if child.getchildren():
                pass
            else:
                listoftag_texts.append((child.tag,child.text))
    return  listoftag_texts

def aggregate_query(L):
    """
        Re build the xml from parts of xml coming from a same document
    :param request:
        - string
    :return:
    """
    queries = [query.split('.') for query in L]
    # Check that the first elements of each query are all identical and we initialize the root
    if not queries or [_[0] for _ in queries].count(queries[0][0]) == len(queries):
        root = Node(queries[0][0])
        for query in queries:
            current_node = root
            for element in query[1:]:
                child = current_node.get_child(element)
                if child is None:
                    new_node = Node(element)
                    current_node.add_child(new_node)
                    current_node = new_node
                else:
                    current_node = child
        return root
    else:
        print("No common root")


def tree_to_xml_string(tree):
    """
        Conversion of an Node-Tree to an XML String
    :param request:
        - XML node
    :return:
    """
    def iter_2_by_2(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

    def rec_xml_to_string(tree):
        current_node = tree
        left = "<{}>".format(current_node.data)
        right = "</{}>".format(current_node.data)
        if current_node.children:
            return "".join([left+rec_xml_to_string(child)+right for child in current_node.children])
        else:
            return left+""+right

    xml_string = rec_xml_to_string(tree)
    xml_str_split = xml_string.split('><')
    xml_str_split[0] = xml_str_split[0][1:]
    xml_str_split[-1] = xml_str_split[-1][:-1]
    remove_idx = [i for i, (a, b) in enumerate(iter_2_by_2(xml_str_split)) if (a.startswith('/') and a[1:] == b)]
    remove_idx_set = set(remove_idx) | set([x+1 for x in remove_idx])
    filtered_list = ["<{}>".format(x) for i, x in enumerate(xml_str_split) if (i not in remove_idx_set)]
    return '<?xml version="1.0"?>{}'.format(''.join(filtered_list))


def json2xml(json_obj, line_padding=""):
    """
        Conversion of a JSON object, a Dict or an Oredereddict into an XML String
    :param request:
        - json object or Dict or Oredereddict
    :return:
    """
    result_list = list()
    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json2xml(sub_elem, line_padding))
        return "\n".join(result_list)

    if json_obj_type is dict or isinstance(json_obj, OrderedDict):
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append("%s<%s>" % (line_padding, tag_name))
            result_list.append(json2xml(sub_obj, "\t" + line_padding))
            result_list.append("%s</%s>" % (line_padding, tag_name))
        return "\n".join(result_list)

    return "%s%s" % (line_padding, json_obj)

def get_node_name(node_id):
    """
        Get the name of the node
    :param request:
        - node id
    :return:
    """
    navigation_name0 = Navigation.get_name(node_id)
    indexx = (navigation_name0).rfind("#")
    return navigation_name0[indexx+1:]

def remove_empty_nodes(xml):
    """
        Remove the node without any value for an xml tree
    :param request:
        - xml object
    :return:
    """
    for child in xml.getiterator():
        if child.getchildren():
            pass
        else:
            if (str(child.text))[0:9]==mystring:
                pass#print (child.tag,child.text)
            else:
                try:
                    xmlpere = child.findall("..")
                    xmlpere[0].remove(child)
                except:
                    pass

def check_empty_nodes(xml):
    """
        Check if there are some node that have no value for an xml tree
    :param request:
        - xml object
    :return:
    """
    myvar = False
    for child in xml.getiterator():
        if child.getchildren():
            pass
        else:
        #if child.text!='':
            if (str(child.text))[0:9]==mystring:
                pass
            else:
                return True
    return False

def checkandremove(xml,listeof):
    lst = listeof
    for child in xml.iter():
        if child.getchildren():
            pass#print('')
        else:
            for s in listeof:
                if str(child.tag) == str(s[0]):
                    try :
                        if (str(child.text))[0:9] == mystring:
                            lst.remove(s)
                    except:
                        lst.remove(s)
    for child in xml.iter():
        if child.getchildren():
            pass#print('')
        else:
            for s in lst:
                if str(child.tag) == str(s[0]):
                    try :
                        if (child.text)[0:9] == mystring:
                            pass
                        else:
                            child.text = mystring+str(s[1])
                    except:
                        child.text = mystring+str(s[1])
    for child in xml.iter():
        if child.getchildren():
            pass
        else:
            if (child.text)[0:9] == mystring:
                ancien = (child.text)[9:]
                child.text = ancien

def fill_xml(xml,listeof):
    """
        Add the value of the nodes for an xml tree
    :param request:
        - xml object
        - list of the value for each xml node
    :return:
    """
    i=0
    global sz
    empty_nodes = 0
    first_time = True
    for child in xml.iter():
        if child.getchildren():
            pass#print('')
        else:
            if first_time == True:
                first_time = False
            else:
                empty_nodes+=1
    myliste = []
    if empty_nodes==0:
        myliste = listeof
    else:
        myliste = listeof[0:empty_nodes]

    for child in xml.iter():
        if child.getchildren():
            pass#print('')
        else:
            if empty_nodes==0:
                if str(child.tag) == str(listeof[0][0]):
                    child.text = mystring + str(listeof[0][1])
                    myliste.remove(myliste[0])
            else:
                for s in listeof[0:empty_nodes]:
                    tab = False
                    if str(child.tag) == str(s[0]):
                        child.text = mystring + str(s[1])
                        myliste.remove(s)
                        #break
                    i +=1
    for l in myliste:
        for child in xml.iter():
            if child.getchildren():
                pass#print('')
            else:
                if child.text =='':
                    child.text = l[1]
    return xml

def get_tree(xml_string):
    """
        Get the xml tree associated to an xml string
    :param request:
        - string
    :return:
    """
    parser = XMLParser(target=MyParser())
    parser.feed(xml_string)
    tree = parser.close()
    return tree

def pairwise(iterable):
    """
        Create an inclusion list that represents the xml
    :param request:
        - list of the xml brackets eg: ["a","b","c","/c","/b","/a"]
        iterable s -> (s0,s1), (s2,s3), (s4, s5), ...
    :return:
    """
    it = iter(iterable)
    return izip(it, it)

def union_tree(tree1, tree2, verbose = False):
    """
        Get the union of parts of xml trees
    :param request:
        - xml trees
    :return:
    """
    if verbose:
        def verboseprint(*args):
            for arg in args:
                end = " "
                print(arg, end)
            print()
    else:
        verboseprint = lambda *a: None

    tree = deepcopy(tree1)
    stack_tree = deque([tree])
    stack_tree1 = deque([tree1])
    stack_tree2 = deque([tree2])
    while stack_tree1:
        verboseprint("stack tree1 = {}".format([x[0] for x in stack_tree1]))

        current_node_tag_t, current_node_childs_t = stack_tree.pop()
        current_node_tag_t1, current_node_childs_t1 = stack_tree1.pop()
        current_node_tag_t2, current_node_childs_t2 = stack_tree2.pop()
        verboseprint("tag courant t1 = {}".format(current_node_tag_t1))
        verboseprint("tag courant t2 = {}".format(current_node_tag_t2))

        current_node_childs_t1_pairwised = list(pairwise(current_node_childs_t1))
        current_node_childs_t2_pairwised = list(pairwise(current_node_childs_t2))
        current_node_childs_tags_t1 = [x[0] for x in current_node_childs_t1_pairwised]
        current_node_childs_tags_t2 = [x[0] for x in current_node_childs_t2_pairwised]
        verboseprint("current_node_childs_tags_t1 = {}".format(current_node_childs_tags_t1))
        verboseprint("current_node_childs_tags_t2 = {}".format(current_node_childs_tags_t2))

        # It is necessary to stack the common nodes for the continuation of the course and to add the non common node

        # compare the tags between each tree
        childs_t1_dict = {tag:val for tag, val in current_node_childs_t1_pairwised}
        childs_t2_dict = {tag:val for tag, val in current_node_childs_t2_pairwised}
        tag_set_1, tag_set_2 = set(current_node_childs_t1[::2]), set(current_node_childs_t2[::2])
        interection_tag = tag_set_1 & tag_set_2
        difference_tag = tag_set_2 - tag_set_1
        verboseprint("Intersection tag = {}".format(interection_tag))
        verboseprint("Difference tag = {}".format(difference_tag))

        # We make sure of the order of the ensembles
        intersection_tag_ordered = [_ for _ in current_node_childs_tags_t1 if _ in interection_tag]
        difference_tag_ordered   = [_ for _ in current_node_childs_tags_t2 if _ in difference_tag]
        verboseprint("difference_tag_ordered = {}".format(difference_tag_ordered))
        #retrieve subtrees of each sub ensemble
        common_childs = list(chain.from_iterable([(tag, childs_t1_dict[tag]) for tag in intersection_tag_ordered]))
        uncommon_childs = list(chain.from_iterable([(tag, childs_t2_dict[tag]) for tag in difference_tag_ordered]))
        verboseprint("common_childs_list = {}".format(common_childs))
        verboseprint("uncommon_childs_list = {}".format(uncommon_childs))

        # Stack for the rest of the way, there are always common nodes
        if common_childs:
            stack_tree.extend(list(pairwise(current_node_childs_t))[::-1])
            stack_tree1.extend(list(pairwise(current_node_childs_t1))[::-1])
            stack_tree2.extend(list(pairwise(current_node_childs_t2))[::-1])
        # Gather nodes not common to both trees
        #if current_node_tag_t1 == current_node_tag_t2:
        current_node_childs_t.extend(uncommon_childs)

#         verboseprint("tree = {}".format(tree))
        verboseprint()
    return tree

def iter_2_by_2(iterable):
    """
        Create an inclusion list that represents the xml
    :param request:
        - list of the xml brackets eg: ["a","b","c","/c","/b","/a"]
    :return:
    """
    #"s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def LTree_to_xml_string(tree):
    """Conversion of a Tree to an XML String
    :param request:
        - xml tree
    :return:
    """
    def rec_xml_to_string(tree):
        current_node_tag, current_node_childs = tree
        left = "<{}>".format(current_node_tag)
        right = "</{}>".format(current_node_tag)
    #     print(current_node_tag, [x for x in current_node_childs[::2]])
        if current_node_childs:
            return "".join([left+rec_xml_to_string(child)+right for child in pairwise(current_node_childs)])
        else:
            return left+""+right

    xml_string = rec_xml_to_string(tree)
    xml_str_split = xml_string.split('><')
    xml_str_split[0] = xml_str_split[0][1:]
    xml_str_split[-1] = xml_str_split[-1][:-1]
    remove_idx = [i for i, (a, b) in enumerate(iter_2_by_2(xml_str_split)) if (a.startswith('/') and a[1:] == b)]
    remove_idx_set = set(remove_idx) | set([x+1 for x in remove_idx])
    filtered_list = ["<{}>".format(x) for i, x in enumerate(xml_str_split) if (i not in remove_idx_set)]
    return ''.join(filtered_list)
