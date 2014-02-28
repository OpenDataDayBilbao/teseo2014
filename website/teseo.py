#!/usr/bin/python
# -*- coding: utf-8 -*-

# all the imports
from flask import Flask, request, session, g, redirect, url_for, render_template, flash
import json

from slugify import slugify

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from data.cache import codes_descriptor


app = Flask(__name__)
app.config.from_object(__name__)


@app.template_filter('slugify')
def _jinja2_filter_slugify(string):
    return slugify(string)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/theses_geographical_distribution')
def theses_geographical_distribution():
    return render_template("totals_analysis/theses_geographical_distribution.html")


@app.route('/genero_del_tribunal')
def gender_in_panel():
    return render_template("gender_in_panel.html")


@app.route('/theses_gender_distribution')
def theses_gender_distribution():
    return render_template("gender_analysis/theses_distribution.html")


@app.route('/panel_gender_distribution')
def panel_gender_distribution():
    return render_template("gender_analysis/panel_distribution.html")


@app.route('/topics/<min_year>/<max_year>')
def topics_by_five_years(min_year, max_year):
    json_data = open('static/data/first_level_areas_temporal.json')
    data = json.load(json_data)
    json_data.close

    tag_dict = {}

    min_year = int(min_year)
    max_year = int(max_year)

    for _year in range(min_year, max_year):
        tags = data[str(_year)]
        for key, value in tags.items():
            if key in tag_dict.keys():
                tag_dict[key] = tag_dict[key] + value
            else:
                tag_dict[key] = value

    return render_template("topics_per_five_years.html", tag_dict=tag_dict, min_year=min_year, max_year=max_year)


@app.route('/all_topics/<min_year>/<max_year>')
def all_topics_by_five_years(min_year, max_year):
    json_data = open('static/data/areas_temporal.json')
    data = json.load(json_data)
    json_data.close

    tag_dict = {}

    min_year = int(min_year)
    max_year = int(max_year)

    for _year in range(min_year, max_year):
        tags = data[str(_year)]
        for key, value in tags.items():
            if key in tag_dict.keys():
                tag_dict[key] = tag_dict[key] + value
            else:
                tag_dict[key] = value

    return render_template("topics_per_five_years.html", tag_dict=tag_dict, min_year=min_year, max_year=max_year)


@app.route('/evolution_topic/<topic>')
def evolution_topic(topic):
    return render_template("evolution_topic.html", topic=topic)


@app.route('/evolution_topic/<topic_1>/<topic_2>')
def evolution_topic_comparison(topic_1, topic_2):
    return render_template("evolution_topic_comparison.html", topic_1=topic_1, topic_2=topic_2)


@app.route('/topic_list/')
def topic_list():
    topics = []

    for key, value in codes_descriptor.items():
        if str(key)[2:6] == '0000':
            topics.append(value)

    return render_template("topic_analysis/topic_list.html", topics=sorted(topics))


@app.route('/topic_geographical_distribution')
def topic_geographical_distribution():
    topics = []

    for key, value in codes_descriptor.items():
        if str(key)[2:6] == '0000':
            topics.append(value)

    return render_template("topic_analysis/topic_geographical_distribution.html", topics=sorted(topics))


@app.route('/topic_evolution/')
@app.route('/topic_evolution/<topic>')
def topic_evolution(topic=None):
    topics = []

    for key, value in codes_descriptor.items():
        if str(key)[2:6] == '0000':
            topics.append(value)

    if topic:
        topic = topic.upper().replace("-", " ")

    return render_template("topic_analysis/single_evolution.html", topic=topic, topics=sorted(topics))


@app.route('/gender_by_topic/<min_year>/<max_year>')
def gender_by_topic(min_year, max_year):
    return render_template("gender_analysis_by_topics.html", min_year=min_year, max_year=max_year)


if __name__ == '__main__':
    app.run(debug=True)
