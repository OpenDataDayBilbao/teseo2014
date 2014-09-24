# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 08:55:14 2014

@author: aitor
"""

import mysql.connector
import networkx as nx
from networkx.generators.random_graphs import barabasi_albert_graph
import json
import os.path
import numpy as np
import pandas as pd
from pandas import Series

config = {
    'user': 'aitor',
    'password': 'pelicano',
    'host': 'thor.deusto.es',
    'database': 'teseo_clean',
}



# Execute it once
def get_persons_university():
    p_u = {}
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    query = "SELECT thesis.author_id, thesis.university_id, university.name, university.location, person.name FROM thesis, university, person WHERE thesis.university_id = university.id AND thesis.author_id = person.id"
    cursor.execute(query)
    for thesis in cursor:
        p_u[thesis[0]] = { 
                            "university" : {"id" : thesis[1], "name" : thesis[2], "location" : thesis[3]},
                            "author" : {"name" : thesis[4]}
                         }
    cursor.close()
    cnx.close()
    json.dump(p_u, open("./cache/persons_university.json", "w"), indent=2)
    
    
def load_persons_university():
    print "Loading the persons_university cache..."
    if not os.path.isfile("./cache/persons_university.json"):
        print "  - Building the persons_university cache..."
        get_persons_university()
        
    p_u = json.load(open("./cache/persons_university.json", "r"))
    print "done"
    return p_u
    
def get_persons_id():
    p_i = {}
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    query = "SELECT person.id, person.name FROM person"
    cursor.execute(query)
    for person in cursor:
        p_i[person[0]] = person[1]
    
    cursor.close()
    cnx.close()    
    json.dump(p_i, open("./cache/persons_id.json", "w"), indent = 2)
    

def load_persons_id():
    print "Loading the persons_id cache..."
    if not os.path.isfile("./cache/persons_id.json"):
        print "  - Building the persons_id cache..."
        get_persons_university()
        
    p_u = json.load(open("./cache/persons_id.json", "r"))
    print "done"
    return p_u    

    
persons_university = load_persons_university()
persons_id = load_persons_id()
    

def build_thesis_genealogy():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()    
    query = "SELECT thesis.author_id, advisor.person_id FROM thesis, advisor WHERE thesis.id = advisor.thesis_id"
    cursor.execute(query)
    G = nx.DiGraph()
    for thesis in cursor:
        G.add_edge(thesis[1], thesis[0])
        
    i = 0        
    for n in G.nodes():
        try:
            node = str(n)
            G.node[n]["name"] = persons_id[node]
            try:
                G.node[n]["university"] = persons_university[node]["university"]["name"]
                G.node[n]["location"] = persons_university[node]["university"]["location"]
                i += 1
            except:
                G.node[n]["university"] = "none"
                G.node[n]["location"] = "none"
        except:
            print n
    
    print "Total persons with a location:", i
    cursor.close()
    cnx.close()
        
    nx.write_gexf(G, "./networks/genealogy.gexf")
    return G
    
def build_panel_network(with_weigh = True):
    cnx = mysql.connector.connect(**config)
    
    print "Recovering thesis ids"
    cursor = cnx.cursor()    
    query = "SELECT id FROM thesis"
    cursor.execute(query)
    thesis_ids = []
    for thesis in cursor:
        thesis_ids.append(thesis[0])
    cursor.close()
    
    print "Creating panel network"
    cursor = cnx.cursor() 
    G = nx.Graph()
    for c, thesis_id in enumerate(thesis_ids):
        if c % 1000 == 0:
            print c, "of", len(thesis_ids)
        cursor.execute("SELECT person_id FROM panel_member WHERE thesis_id = " + str(thesis_id))
        members = []
        for member in cursor:
            members.append(member[0])
        
        for i, m1 in enumerate(members):
            for m2 in members[i+1:]:
                if with_weigh:
                    if not G.has_edge(m1, m2):
                        G.add_edge(m1,m2, weight = 1)
                    else:
                        G.edge[m1][m2]['weight'] += 1
                else: 
                    G.add_edge(m1,m2)
    
    cursor.close()
    cnx.close()
        
    nx.write_gexf(G, "./networks/panels.gexf")
    return G
    
def analize_cliques(G):
    print "Calculating cliques..."
    cliques = nx.find_cliques(G)
    print "Analysing the results..."
    tot_cliques = 0
    tot_size = 0
    max_size = 0
    min_size = 10000
    high_5 = 0
    hist_clic = {}
    for c in cliques:
        tot_cliques += 1
        tot_size += len(c)
        if len(c) > 5: #5 is the panel size in Spain
            high_5 += 1
            
        if len(c) > max_size :
            max_size = len(c)
        if len(c) < min_size:
            min_size = len(c)
            
        if hist_clic.has_key(len(c)):
            hist_clic[len(c)] += 1
        else:
            hist_clic[len(c)] = 1
            
    print "CLIQUES:"
    print "  - Total cliques:", tot_cliques
    print "  - Avg cliques size:", tot_size * 1.0 / tot_cliques
    print "  - Max clique:", max_size
    print "  - Min clique:", min_size
    print "  - Cliques with a size higher than 5:", high_5
    print hist_clic
    
def analize_degrees(G):
    print "Calculating degrees..."
    degrees = nx.degree(G)
    hist = nx.degree_histogram(G)
    print "DEGREES:"
    print "  - Max degree:", max(degrees.values())
    print "  - Min degree:", min(degrees.values())
    print "  - Avg. degree:", sum(degrees.values()) * 1.0 / len(degrees)
    print "  - histogram:", hist
    
def analize_edges(G):
    print "Analizing edges..."
    min_weight = 10000
    max_weight = 0
    acum_weight = 0
    hist_weight = {}
    for e in G.edges(data=True):
        acum_weight += e[2]['weight']
        if max_weight < e[2]['weight']:
            max_weight = e[2]['weight']
        if min_weight > e[2]['weight']:
            min_weight = e[2]['weight']
        
        if hist_weight.has_key(e[2]['weight']):
            hist_weight[e[2]['weight']] += 1
        else:
            hist_weight[e[2]['weight']] = 1
        
        
    print "EDGES:"
    print "  - Max weight:", max_weight
    print "  - Min weight:", min_weight
    print "  - Avg weight:", acum_weight * 1.0 / len(G.edges())
    print hist_weight
    
    
    
def generate_random_graph(n, m):
    print "Building random graph"
    G = barabasi_albert_graph(n, m, 10)
    return G

    
        
          
if __name__=='__main__':
    #G = build_panel_network()    
    G = generate_random_graph(188979, 7) #nodes and nodes/edges
    nx.write_gexf(G, "./networks/barabasi_panel.gexf")
    print "Nodes:", G.number_of_nodes()
    print "Edges:", G.number_of_edges()
    analize_cliques(G)
    analize_degrees(G)
#    analize_edges(G)
    

    
    
    
    print "fin"