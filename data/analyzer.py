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
from pandas import DataFrame

config = {
    'user': 'aitor',
    'password': 'pelicano',
    'host': 'thor.deusto.es',
    'database': 'teseo_clean',
}

persons_university = []
persons_id = []


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
    
def get_first_level_descriptors():
    cnx = mysql.connector.connect(**config)
    
    print "Recovering first level descriptors"
    cursor = cnx.cursor()    
    query = "select id, text, code from descriptor where parent_code IS NULL"
    cursor.execute(query)
    descriptors = {}
    for d in cursor:
        descriptors[d[2]] = {"id" : d[0], "text" : d[1]}
    
    cursor.close()
    cnx.close()
    
    return descriptors
    
def build_panel_network_by_descriptor(desc_id, unesco_code):  
    cnx = mysql.connector.connect(**config)
    
    print "Recovering thesis ids"
    cursor = cnx.cursor()    
    query = "SELECT thesis_id FROM association_thesis_description WHERE descriptor_id = " + str(desc_id)
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
                if not G.has_edge(m1, m2):
                    G.add_edge(m1,m2, weight = 1)
                else:
                    G.edge[m1][m2]['weight'] += 1

    
    cursor.close()
    cnx.close()
        
    nx.write_gexf(G, "./networks/panels-" + str(unesco_code) + ".gexf")
    return G
    
        
def generate_random_graph(n, m):
    print "Building random graph"
    G = barabasi_albert_graph(n, m, 10)
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
    print "  - histogram:", hist_clic
    
    results = {}
    results['clique_tot'] = tot_cliques
    results['clique_avg'] = tot_size * 1.0 / tot_cliques
    results['clique_max'] = max_size
    results['clique_min'] = min_size
    results['clique_greater_5'] = high_5
    results['clique_greater_5_norm'] = high_5 * 1.0 / tot_cliques
    #results['clique_histogram'] = hist_clic
    return results
    
def analize_degrees(G):
    print "Calculating degrees..."
    degrees = nx.degree(G)
    hist = nx.degree_histogram(G)
    print "DEGREES:"
    print "  - Max degree:", max(degrees.values())
    print "  - Min degree:", min(degrees.values())
    print "  - Avg. degree:", sum(degrees.values()) * 1.0 / len(degrees)
    print "  - histogram:", hist
    
    results = {}
    results['degree_avg'] = sum(degrees.values()) * 1.0 / len(degrees)
    results['degree_max'] = max(degrees.values())
    results['degree_min'] = min(degrees.values())
    #results['degree_histogram'] = hist
    return results
    
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
    print "  - histogram:", hist_weight
    
    results = {}
    results['weight_avg'] = acum_weight * 1.0 / len(G.edges())
    results['weight_max'] = max_weight
    results['weight_min'] = min_weight
    #results['weight_histogram'] = hist_weight
    return results
    
    
   
def analyze_rdn_graph():
    G = generate_random_graph(188979, 7) #nodes and nodes/edges
    nx.write_gexf(G, "./networks/barabasi_panel.gexf")
    print "Nodes:", G.number_of_nodes()
    print "Edges:", G.number_of_edges()
    analize_cliques(G)
    analize_degrees(G)


def analyze_first_level_panels():
    descriptors = get_first_level_descriptors()
    results = {}
    
    for d in descriptors:
        descriptor = descriptors[d]
        print "\n*********DESCRIPTOR: " + descriptor['text'] + "(" + str(d) + ")"
        G = build_panel_network_by_descriptor(descriptor['id'],d)
        print "\nDESCRIPTOR: " + descriptor['text'] + "(" + str(d) + ")"
        print "Nodes:", G.number_of_nodes()
        print "Edges:", G.number_of_edges()
        res_clique = analize_cliques(G)
        res_degree = analize_degrees(G)
        res_weight = analize_edges(G)
        d_final = dict(res_clique)
        d_final.update(res_degree)
        d_final.update(res_weight)
        d_final['id'] = d
        d_final['avg_clustering'] = nx.average_clustering(G)
        results[descriptor['text']] = d_final
        
    print "Writing json..."
    json.dump(results, open('./networks/first_level_analysis.json','w'), indent = 2)
    
def from_json_to_dataframe():
    results = json.load(open('./networks/first_level_analysis.json','r'))
    df = DataFrame(results)
    df.to_csv("panels.csv")
    dft = df.transpose()
    dft.to_csv("panels_trans.csv")
    return df
    #df = DataFrame(['id', 'name', 'clique_tot', 'clique_avg', 'clique_max', 'clique_min', 'clique_greater_5', 'degree_max', 'degree_min', 'degree_avg', 'weight_max', 'weight_min', 'weight_avg']);

def panel_repetition_per_advisor():
    cnx = mysql.connector.connect(**config)    
    print "Recovering thesis ids for each advisor..."
    cursor = cnx.cursor()    
    
    query = "SELECT person_id, thesis_id FROM advisor"
    cursor.execute(query)
    thesis_advisor = {}
    for thesis in cursor:
        adv_id = thesis[0]
        thesis_id = thesis[1]
        if thesis_advisor.has_key(adv_id):
            thesis_advisor[adv_id].append(thesis_id)
        else:
            thesis_advisor[adv_id] = [thesis_id]
    cursor.close()
    
    print "Counting repetitions..."
    cursor = cnx.cursor() 
    results = {}
    for c, adv in enumerate(thesis_advisor):
        if c % 500 == 0:
            print c, "of", len(thesis_advisor)
        thesis_ids = thesis_advisor[adv]
        adv_id = adv
        for thesis_id in thesis_ids:                  
            cursor.execute("SELECT person_id FROM panel_member WHERE thesis_id = " + str(thesis_id))
            for member in cursor:
                if results.has_key(adv_id):
                    if results[adv_id].has_key(member[0]):
                        results[adv_id][member[0]] += 1
                    else:
                        results[adv_id][member[0]] = 0
                else: 
                    results[adv_id] = {member[0] : 0}
    
    cursor.close()
    cnx.close()
    
    json.dump(results, open('./networks/repetitions_per_advisor.json', 'w'), indent=2)
    
    print "Procesing total repetitons"
    repetitions_per_advisor = {}
    for adv in results:
        total_rep = 0
        for rep in results[adv]:
            total_rep += results[adv][rep]
            
        repetitions_per_advisor[adv] = total_rep
    
        
    return repetitions_per_advisor
    
def thesis_per_year():
     
    results = {}
    cnx = mysql.connector.connect(**config)   
    cursor = cnx.cursor()  
    for year in range(1977,2015):                           
        query = "SELECT count(defense_date) FROM thesis WHERE year(defense_date)=year('" + str(year) + "-01-01')"
        cursor.execute(query)
        for r in cursor:
            results[year] = r[0]

    cursor.close()       
    cnx.close()    
    return results
    
def thesis_per_location():
    results = {}
    cnx = mysql.connector.connect(**config)   
    cursor = cnx.cursor()  
    cursor.execute("select distinct(location) from university")
    locations = []
    for l in cursor:
        locations.append(l[0])
    results = {}
    for location in locations:                           
        query = "SELECT count(thesis.id) FROM thesis, university WHERE university.location = '" + location + "'"
        cursor.execute(query)
        for r in cursor:
            results[location] = r[0]

    cursor.close()       
    cnx.close()    
    return results
    
def analyze_advisor_student_genders():
    cnx = mysql.connector.connect(**config)   
    cursor = cnx.cursor()  
    print "Recovering advisor-student pairs..."
    cursor.execute("SELECT thesis.author_id, advisor.person_id FROM thesis, advisor WHERE thesis.id = advisor.thesis_id")
    adv_stu = []
    for advisor in cursor:
        adv_stu.append([advisor[1], advisor[0]])
    
    print "Recovering genders..."
    genders = {}    
    cursor.execute("SELECT person.id, person.gender FROM person")
    for person in cursor:
        genders[person[0]] = person[1]
        
    
    cursor.close()       
    cnx.close() 
    
    print "Counting..."
    results = {}
    results["MM"] = 0
    results["FF"] = 0
    results["FM"] = 0
    results["MF"] = 0
    
    for pair in adv_stu:      
        try:
            adv_gender = genders[pair[0]]
            stu_gender = genders[pair[1]]
        except:
            adv_gender = 'none'
            stu_gender = 'none'
            
        if adv_gender == 'male':
            if stu_gender == 'male':
                results['MM'] += 1
            elif stu_gender == 'female':
                results['MF'] += 1          
        elif adv_gender == 'female':
            if stu_gender == 'male':
                results['FM'] += 1
            elif stu_gender == 'female':
                results['FF'] += 1
    
    
    
    return results
    

if __name__=='__main__':       
    results = analyze_advisor_student_genders()
    print results
  
    
    print "fin"