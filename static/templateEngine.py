from jinja2 import Environment, FileSystemLoader
import shutil

def write ():
    environment = Environment(loader=FileSystemLoader("./static/templates/"))
    results_filename = "tabel_report.html"
    results_template = environment.get_template("index.html")
    students = [
        {"name": "Sandrine",  "score": 100},
        {"name": "Gergeley", "score": 87},
        {"name": "Frieda", "score": 92},
        {"name": "Fritz", "score": 40},
        {"name": "Sirius", "score": 75},
    ]
    context = {
        "students": students,
        "test_name": 'halo',
        "max_score": 100,
    }
    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        shutil.copy("tabel_report_yg_dipakai.html","./static/")