# STAT 107 SpeedGrader
This is a webapp to pull up a student's Jupyter notebook for a certain lab before a deadline (if no deadline given, the latest commit is used)

Setup: 
1. Go to [https://my.siebelschool.illinois.edu/](https://my.siebelschool.illinois.edu/) and select your lab sections, then export to CSV
2. Name the CSV file `roster.csv` and place in static folder
3. Put your GitHub token in `token.txt` (make sure the token is authorized for STAT 107)

How to Use:
- `flask run` to start
- Go to the port listed in the terminal or `http://localhost:1989/`
- Select a section, lab, and deadline (optional) from the dropdowns
- You can switch between students with prev/next or the dropdown
- If a student's notebook has not been previously loaded for a lab and deadline, it will take a few seconds to load
- You can load all students' files from a section at once with "Load All Section Files" and unload all files with "Clear All Files"
- Edit static/labs.csv to add other labs/projects
