#!/usr/bin/python
# -*- coding: utf-8 -*-

# all the imports
from flask import Flask, request, session, g, redirect, url_for, render_template, flash
import json
from static.data.cache import codes_descriptor


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/genero')
def gender():
    return render_template("male_female.html")


@app.route('/genero_del_tribunal')
def gender_in_panel():
    return render_template("gender_in_panel.html")


@app.route('/total_theses')
def total_theses():
    return render_template("totals_analysis/total_theses.html")


@app.route('/theses_gender_distribution')
def theses_gender_distribution():
    return render_template("gender_analysis/theses_gender_distribution.html")


@app.route('/topics/<min_year>/<max_year>')
def topics_by_five_years(min_year, max_year):
    json_data = open('static/data/processed_data/first_level_areas_temporal.json')
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
    json_data = open('static/data/processed_data/areas_temporal.json')
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


@app.route('/evolution_topic/')
def evolution_topic_list():
    topics = []

    for key, value in codes_descriptor.items():
        if str(key)[2:6] == '0000':
            topics.append(value)

    return render_template("evolution_topic_list.html", topics=topics)


@app.route('/gender_by_topic/<min_year>/<max_year>')
def gender_by_topic(min_year, max_year):
    return render_template("gender_analysis_by_topics.html", min_year=min_year, max_year=max_year)


if __name__ == '__main__':
    app.run(debug=True)
