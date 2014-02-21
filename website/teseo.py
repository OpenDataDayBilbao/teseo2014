#!/usr/bin/python
# -*- coding: utf-8 -*-

# all the imports
from flask import Flask, request, session, g, redirect, url_for, render_template, flash
import json


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/genero')
def gender():
    return render_template("male_female.html")


@app.route('/total')
def total_theses_by_year():
    return render_template("total_theses_by_year.html")


@app.route('/topics/<year>')
def topics_by_five_years(year):
    json_data = open('static/data/processed_data/first_level_areas_temporal.json')
    data = json.load(json_data)
    json_data.close

    tag_dict = {}

    min_year = int(year)
    max_year = min_year + 5

    for _year in range(min_year, max_year):
        tags = data[str(year)]
        for key, value in tags.items():
            if key in tag_dict.keys():
                tag_dict[key] = tag_dict[key] + value
            else:
                tag_dict[key] = value

    return render_template("topics_per_five_years.html", tag_dict=tag_dict, min_year=min_year, max_year=max_year)


@app.route('/all_topics/<year>')
def all_topics_by_five_years(year):
    json_data = open('static/data/processed_data/areas_temporal.json')
    data = json.load(json_data)
    json_data.close

    tag_dict = {}

    min_year = int(year)
    max_year = min_year + 5

    for _year in range(min_year, max_year):
        tags = data[str(year)]
        for key, value in tags.items():
            if key in tag_dict.keys():
                tag_dict[key] = tag_dict[key] + value
            else:
                tag_dict[key] = value

    return render_template("topics_per_five_years.html", tag_dict=tag_dict, min_year=min_year, max_year=max_year)


if __name__ == '__main__':
    app.run(debug=True)
