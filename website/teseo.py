#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from slugify import slugify

import os
import sys
import simplejson as json

lib_path = os.path.abspath('../')
sys.path.append(lib_path)

from data.cache import codes_descriptor, university_locations

app = Flask(__name__)
app.config.from_object(__name__)


NUMBER_OF_TOP_TOPICS = 15


###########################################################################
#####   Template filters
###########################################################################

@app.template_filter('slugify')
def _jinja2_filter_slugify(string):
    return slugify(string)


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

    return render_template("topic_analysis/top_topics.html", min_year=min_year, max_year=max_year, university_slug=university_slug, top_topics=ordered_topics[:NUMBER_OF_TOP_TOPICS], universities=sorted(universities))


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


@app.route('/testing')
def testing():
    return render_template("network/index.html")


###########################################################################
#####   Main
###########################################################################


if __name__ == '__main__':
    app.run(debug=True)
