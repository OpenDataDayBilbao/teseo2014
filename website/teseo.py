#!/usr/bin/python
# -*- coding: utf-8 -*-

# all the imports
from flask import Flask, request, session, g, redirect, url_for, render_template, flash


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


if __name__ == '__main__':
    app.run(debug=True)
