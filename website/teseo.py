#!/usr/bin/python
# -*- coding: utf-8 -*-

# all the imports
from flask import Flask, request, session, g, redirect, url_for, render_template, flash


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/bu')
def bu():
    return render_template("male_female.html")


if __name__ == '__main__':
    app.run(debug=True)
