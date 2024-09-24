from flask import Flask, render_template, request, send_from_directory, jsonify
from helper_functions import *
import requests
import os
import subprocess

TOKEN = open("token.txt").read().strip()
OWNER = "stat107-illinois"
ROSTER_FILE = "static/roster.csv"
LABS_FILE = "static/labs.csv"

student_index = None
info = None

# create static/tmp if it doesn't exist
if not os.path.exists(os.path.join("static", "tmp")):
    os.makedirs(os.path.join("static", "tmp"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html",
                           sections = get_sections(ROSTER_FILE),
                           labs = get_labs(LABS_FILE)
                            )

@app.route('/loadSection', methods = ["POST"])
def load_section():
    global student_index
    global info
    section = request.form["section"]
    info = get_student_info(section, ROSTER_FILE)
    student_index = 0
    netid = info[student_index]["netid"]
    name = info[student_index]["name"]
    return jsonify({"netid": netid, "name": name, "students": info})

@app.route('/nextStudent', methods = ["POST"])
def next_student():
    global student_index
    student_index = (student_index + 1) % len(info)
    netid = info[student_index]["netid"]
    name = info[student_index]["name"]
    return jsonify({"netid": netid, "name": name, "progress": f"{student_index + 1}/{len(info)}"})

@app.route('/prevStudent', methods = ["POST"])
def prev_student():
    global student_index
    student_index = (student_index - 1) % len(info)
    netid = info[student_index]["netid"]
    name = info[student_index]["name"]
    return jsonify({"netid": netid, "name": name, "progress": f"{student_index + 1}/{len(info)}"})

@app.route('/loadStudent', methods = ["POST"])
def load_student():
    global student_index
    deadline = request.form["deadline"]
    file = request.form["file"]
    if "netid" in request.form:
        student_index = [student["netid"] for student in info].index(request.form["netid"])
    netid = info[student_index]["netid"]
    name = info[student_index]["name"]

    output, successful = load_notebook(netid, deadline, file, name, TOKEN)

    if not successful:
        return output
    else:
        file_name_html = output

    return send_from_directory(os.path.join("static", "tmp"), file_name_html)

@app.route('/clearFiles', methods = ["POST"])
def clear_files():
    for file in os.listdir(os.path.join("static", "tmp")):
        os.remove(os.path.join("static", "tmp", file))
    return "Files cleared"

@app.route('/loadAllFiles', methods = ["POST"])
def load_all_files():
    deadline = request.form["deadline"]
    file = request.form["file"]
    for student in info:
        netid = student["netid"]
        name = student["name"]

        load_notebook(netid, deadline, file, name, TOKEN)

    return "All files loaded"

@app.route('/getProgress', methods = ["POST"])
def get_progress():
    return f"{student_index + 1}/{len(info)}"

if __name__ == '__main__':
    app.run(port = 1989)
