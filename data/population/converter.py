# -*-*- encoding: utf8 -*-*-
import pprint
import csv
import json

REGION_TRANSLATOR = {
        u'Total' : u'Total',
        u'Total Nacional' : u'Total',
        u'Castilla -La Mancha' : u'Castilla La Mancha',
        u'Castilla - La Mancha' : u'Castilla La Mancha',
        u'Rioja (La)' : u'La Rioja',
        u'Rioja; La' : u'La Rioja',
        u'Balears (Illes)' : u'Islas Baleares',
        u'Balears; Illes' : u'Islas Baleares',
        u"Cataluña" : u"Cataluña", 
        u"Andalucía" : u"Andalucía", 
        u"Madrid (Com. de)" : u"Madrid", 
        u"Madrid (Com. De)" : u"Madrid", 
        u"Madrid; Comunidad de" : u"Madrid", 
        u"Murcia (Región de)" : u"Murcia", 
        u"Murcia; Región de" : u"Murcia", 
        u"Asturias (Principado de)" : u"Asturias", 
        u"Asturias; Principado de" : u"Asturias", 
        u"País Vasco" : u"País Vasco", 
        u"Canarias" : u"Islas Canarias", 
        u"Galicia" : u"Galicia", 
        u"Cantabria" : u"Cantabria", 
        u"Comunidad Valenciana" : u"Valencia", 
        u"Comunitat Valenciana" : u"Valencia", 
        u"Castilla y León" : u"Castilla y León",
        u"Aragón" : u"Aragon",
        u"Extremadura" : u"Extremadura",
        u"Navarra (C. Foral de)" : u"Navarra",
        u"Navarra; Comunidad Foral de" : u"Navarra",
        u'Ceuta y Melilla' : u'Ceuta y Melilla',
        u'Ceuta' : u'Ceuta y Melilla',
        u'Melilla' : u'Ceuta y Melilla',
}

def _retrieve_old_data(rows, initial, end, regions):
    data = {
        # year : {
        #    'region-id' : {
        #       'total' : {
        #       'total' : X,
        #       'men'   : Y,
        #       'women' : Z,
        #    }
        # }
    }

    for line in xrange(initial - 1, end):
        row = rows[line]
        year = int(row[0].strip()[-4:])
        data[year] = {}

        values = row[1:-1]
        for col, value in enumerate(values):
            int_value = int(float(value))
            community = regions[col / 3 * 3]
            if col % 3 == 0:
                data[year][community] = {
                    'total' : int_value
                }
            elif col % 3 == 1:
                data[year][community]['men'] = int_value
            else:
                data[year][community]['women'] = int_value
    return data


def convert_old_ones(fname, names_line, initial_total, end_total, initial_18, end_18):
    reader = csv.reader(open(fname))
    rows = [ line for line in reader ]

    regions = []
    for col in rows[names_line - 1][1:-1]:
        new_col = col.strip().decode('cp1252').replace(u'\xa0', u'')
        if new_col in REGION_TRANSLATOR:
            regions.append(REGION_TRANSLATOR[new_col])
        elif new_col.strip() == '':
            regions.append('')
        else:
            print "Missing %r" % new_col
            REGION_TRANSLATOR.get(new_col)
    
    data = {
        'total' : _retrieve_old_data(rows, initial_total, end_total, regions),
        '18' : _retrieve_old_data(rows, initial_18, end_18, regions)
    }
    return data
            
def merge(data, new_data):
    # data = {
    #    'total' : {
    #         year : {
    #             'region-id' : { 'total' : ... }
    #         }
    #    },
    #    '18' : { ... }
    # }
    for year in new_data['total']:
        data['total'][year] = new_data['total'][year]
        data['18'][year] = new_data['18'][year]

data = convert_old_ones("population_spain_1977_1981.csv", names_line = 8, initial_total = 12, end_total = 16, initial_18 = 18, end_18 = 22)

new_data = convert_old_ones("population_spain_1981_1991.csv", names_line = 8, initial_total = 12, end_total = 22, initial_18 = 24, end_18 = 34)
merge(data, new_data)

new_data = convert_old_ones("population_spain_1991_2001.csv", names_line = 8, initial_total = 12, end_total = 22, initial_18 = 24, end_18 = 34)
merge(data, new_data)

new_data = convert_old_ones("population_spain_2001_2012.csv", names_line = 8, initial_total = 11, end_total = 21, initial_18 = 23, end_18 = 33)
merge(data, new_data)

json_data = json.dumps(data, indent = 4)
FNAME = '../../website/static/data/population.json'
open(FNAME, 'w').write(json_data)
print "%s saved." % FNAME
