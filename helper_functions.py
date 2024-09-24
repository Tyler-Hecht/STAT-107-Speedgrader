import pandas as pd
from datetime import datetime
import pytz
import os
import requests
import subprocess

def get_student_info(section, file):
    df = pd.read_csv(file)
    df_section = df[df["Section"] == section]
    return [
        {"netid": netid, "name": name}
        for netid, name in
        zip(
            df_section["Net ID"].tolist(),
            df_section["Name"].tolist()
        )
    ]

def get_sections(file):
    df = pd.read_csv(file)
    df_clean = df.dropna()
    return [{"name": section} for section in df_clean["Section"].unique().tolist()]

def get_labs(file):
    df = pd.read_csv(file)
    names = df.name
    paths = df.path
    return [{"name": name, "path": path} for name, path in zip(names, paths)]

def commit_date_to_CT(commit_date):
    # translates the commit date from UTC to CT
    commit_date = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
    commit_date = commit_date.replace(tzinfo=pytz.utc)
    commit_date = commit_date.astimezone(pytz.timezone('America/Chicago'))
    return commit_date

def is_relevant_commit(commit, deadline, netid, name):
    # a commit is relevant if it was made by the student before the deadline
    author_email = commit['commit']['author']['email']
    author_name = commit['commit']['author']['name']
    
    if not ( # lots of students messed up this step in the setup, so we consider multiple possibilities
            author_email.upper().startswith(netid.upper()) 
            or author_email.upper().startswith("NETID")
            or author_name.upper().startswith(netid.upper())
            or author_name.upper() == name.upper()
            ):
        return False
    date = commit_date_to_CT(commit["commit"]["author"]["date"])
    if deadline:
        deadline = datetime.strptime(deadline, "%Y-%m-%d").astimezone(pytz.timezone('America/Chicago'))
        # make deadline 11:59pm
        deadline = deadline.replace(hour=23, minute=59, second=59)
        return date <= deadline
    # if no deadline is provided, accept all commits by the student
    return True

def load_notebook(netid, deadline, file, name, token):
    commits = requests.get(
        f'https://api.github.com/repos/stat107-illinois/fa24_stat107_{netid}/commits',
        headers={
            'accept': 'application/vnd.github.v3.raw',
            'authorization': f'token {token}'
                }
        ).json()
    
    first_last_name = name.split(", ")[1].split(" ")[0] + " " + name.split(", ")[0]

    relevant_commits = [commit for commit in commits if is_relevant_commit(commit, deadline, netid, first_last_name)]
    if len(relevant_commits) == 0:
        return f"No relevant commits found", False
    latest_commit = relevant_commits[0]
    latest_commit["commit"]["message"]

    notebook = requests.get(
    f'https://api.github.com/repos/stat107-illinois/fa24_stat107_{netid}/contents/{file}?ref={latest_commit["sha"]}',
    headers={
        'accept': 'application/vnd.github.v3.raw',
        'authorization': f'token {token}'
            }
    )

    if notebook.status_code != 200:
        return f"No file {file} found", False
    
    lab_name_ipynb = file.split("/")[-1]
    lab_name_html = lab_name_ipynb.replace(".ipynb", ".html")
    file_name_ipynb = os.path.join("static", "tmp", f"{netid}_{deadline}_{lab_name_ipynb}")
    file_name_html = f"{netid}_{deadline}_{lab_name_html}"

    if not os.path.exists(os.path.join("static", "tmp", file_name_html)):
        with open(file_name_ipynb, 'wb') as f:
            f.write(notebook.content)

        process = subprocess.Popen(["jupyter", "nbconvert", "--to", "html", file_name_ipynb])
        process.wait()

    return file_name_html, True
