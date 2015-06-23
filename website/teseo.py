#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from slugify import slugify

import os
import sys
import json

lib_path = os.path.abspath('../')
sys.path.append(lib_path)

from data.cache import codes_descriptor, university_locations


#   http://flask.pocoo.org/snippets/35/
class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001; # where Flask app runs
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = Flask(__name__)
app.config.from_object(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.debug = False


NUMBER_OF_TOP_ITEMS = 15


###########################################################################
#####   Template filters
###########################################################################

@app.template_filter('slugify')
def _jinja2_filter_slugify(string):
    return slugify(unicode(string))


@app.template_filter('divisibleby')
def _jinja2_filter_divisibleby(dividend, divisor):
    return ((dividend % divisor) == 0)


###########################################################################
#####   Views
###########################################################################


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


#####   Gender analysis     ###############################################


@app.route('/advisor_gender_distribution')
def advisor_gender_distribution():
    return render_template("gender_analysis/advisor_distribution.html")


@app.route('/panel_gender_distribution')
def panel_gender_distribution():
    return render_template("gender_analysis/panel_distribution.html")


@app.route('/theses_gender_distribution')
def theses_gender_distribution():
    return render_template("gender_analysis/theses_distribution.html")


@app.route('/topic_gender_distribution/')
@app.route('/topic_gender_distribution/<topic>')
def topic_gender_distribution(topic="antropologia"):
    topic = topic.upper().replace("-", " ")
    return render_template("gender_analysis/topic_distribution.html", topic=topic)


#####   Network analysis    ###############################################


@app.route('/network/level_1')
def network_level_1():
    return render_template("network/level_1_relationships.html")


@app.route('/network/level_2')
def network_level_2():
    return render_template("network/level_2_relationships.html")


@app.route('/network/level_3')
def network_level_3():
    return render_template("network/level_3_relationships.html")


#####   Topic analysis      ###############################################


@app.route('/topic_evolution/')
@app.route('/topic_evolution/<topic>')
def topic_evolution(topic="antropologia"):
    topics = []

    for key, value in codes_descriptor.items():
        if str(key)[2:6] == '0000':
            topics.append(value)

    topic_slug = topic

    if topic:
        topic = topic.upper().replace("-", " ")

    low_level_topic = False

    if (topic and topic not in topics):
        low_level_topic = True

    return render_template("topic_analysis/single_evolution.html", topic=topic, topic_slug=topic_slug, low_level_topic=low_level_topic, topics=sorted(topics))


@app.route('/top_topics/<min_year>/<max_year>/<university_slug>')
def top_topics(min_year, max_year, university_slug):
    universities = []

    for university in university_locations.keys():
        universities.append(university)

    json_file = open('static/data/university_area_year_by_uni.json')
    data = json.load(json_file)

    university_data = {}

    for university_key in data.keys():
        key_slug = slugify(unicode(university_key))
        if (university_slug == key_slug):
            university_data = data[university_key]

    topic_count_dict = {}

    for year in range(int(min_year), int(max_year) + 1):
        year_str = str(year)
        if year_str in university_data.keys():
            for topic in university_data[year_str].keys():
                if topic in topic_count_dict.keys():
                    topic_count_dict[topic] = topic_count_dict[topic] + university_data[year_str][topic]
                else:
                    topic_count_dict[topic] = university_data[year_str][topic]

    ordered_topics = []

    for topic in sorted(topic_count_dict, key=topic_count_dict.get, reverse=True):
        ordered_topics.append([topic, topic_count_dict[topic]])

    return render_template("topic_analysis/top_topics.html", min_year=min_year, max_year=max_year, university_slug=university_slug, top_topics=ordered_topics[:NUMBER_OF_TOP_ITEMS], universities=sorted(universities))


@app.route('/top_universities/<min_year>/<max_year>/<topic_slug>')
def top_universities(min_year, max_year, topic_slug):
    json_file = open('static/data/university_area_year_by_code.json')
    data = json.load(json_file)

    topics = []
    topic_data = {}

    for topic in data.keys():
        key_slug = slugify(unicode(topic))
        topics.append(topic)
        if (topic_slug == key_slug):
            topic_data = data[topic]

    university_count_dict = {}

    for year in range(int(min_year), int(max_year) + 1):
        year_str = str(year)
        if year_str in topic_data.keys():
            for university in topic_data[year_str].keys():
                if university in university_count_dict.keys():
                    university_count_dict[university] = university_count_dict[university] + topic_data[year_str][university]
                else:
                    university_count_dict[university] = topic_data[year_str][university]

    ordered_universities = []

    for university in sorted(university_count_dict, key=university_count_dict.get, reverse=True):
        ordered_universities.append([university, university_count_dict[university]])

    top_universities = json.dumps(ordered_universities[:NUMBER_OF_TOP_ITEMS])

    return render_template("topic_analysis/top_universities.html", min_year=min_year, max_year=max_year, topic_slug=topic_slug, top_universities=top_universities, topics=sorted(topics))


@app.route('/all_topics_by_range/<min_year>/<max_year>')
def all_topics_by_range(min_year, max_year):
    return render_template("topic_analysis/topics_by_range.html", high_level=False, min_year=min_year, max_year=max_year)


@app.route('/topics_by_range/<min_year>/<max_year>')
def topics_by_range(min_year, max_year):
    return render_template("topic_analysis/topics_by_range.html", high_level=True, min_year=min_year, max_year=max_year)


#####   Totals analysis     ###############################################


@app.route('/month_distribution/')
def month_distribution():
    return render_template("totals_analysis/month_distribution.html")


@app.route('/theses_by_university/')
def theses_by_university():
    universities = []

    for university in university_locations.keys():
        universities.append(university)

    return render_template("totals_analysis/theses_by_university.html", universities=sorted(universities))


@app.route('/theses_geographical_distribution')
def theses_geographical_distribution():
    return render_template("totals_analysis/theses_geographical_distribution.html")


###########################################################################
#####   Main
###########################################################################


if __name__ == '__main__':
    app.run(debug=False)
