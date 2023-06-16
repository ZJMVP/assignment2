from math import radians, sin, cos, asin, sqrt
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request
import pyodbc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zjmvp'

driver = '{ODBC Driver 18 for SQL Server}'
database = 'zjtest'
server = 'zj-server.database.windows.net'
username = "jie_zhao"
password = "Kd1016686103"

with pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password) as conn:
    with conn.cursor() as cursor:
        temp = []
        cursor.execute("SELECT TOP 3 time, place FROM earthquake")
        while True:
            r = cursor.fetchone()
            if not r:
                break
            print(str(r[0]) + " " + str(r[1]))
            temp.append(r)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/Task1", methods=['GET', 'POST'])
def task1():
    return render_template('Task1.html')


class MyForm1(FlaskForm):
    mag = StringField(label='Enter Magnitude: ', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


def distance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
    # calculate the result
    return (c * r)


@app.route('/Task2', methods=['GET', 'POST'])
def Task2():
    if request.method == 'POST':
        Range1 = str(request.form['Range1'])
        Range2 = str(request.form['Range2'])
        net = request.form['Net']
        query = "SELECT * FROM dbo.earthquake where (mag BETWEEN '" + Range1 + "' and '" + Range2 + "') and net = '" + net + "' order by mag"
        cursor.execute(query)
        raw_results = cursor.fetchall()
        length = len(raw_results)
        results = raw_results[-3:]
        results.append(raw_results[0])
        results.append(raw_results[1])
        results.append(raw_results[2])
        return render_template("Task2.html", length=len(results), rows=results)
    else:
        return render_template("Task2.html")


@app.route('/show_a_earthquake', methods=['GET', 'POST'])
def Task1():
    if request.method == 'POST':
        time = request.form['time']
        query = "SELECT * FROM dbo.earthquake WHERE time = " + time
        cursor.execute(query)
        results = cursor.fetchall()
        return render_template("Task1.html", length=len(results), rows=results)


@app.route('/Task3', methods=['GET', 'POST'])
def Task3():
    if request.method == 'POST':
        time = request.form['Time']
        net = request.form['Net']
        latitude = request.form['Latitude']
        longitude = request.form['Longitude']
        mag = request.form['Mag']
        place = request.form['Place']
        insert_row = "INSERT INTO dbo.earthquake VALUES('" + time + "','" + latitude + "','" + longitude + "','" + mag + "','" + net + "','" + place + "')"
        cursor.execute(insert_row)

        return render_template("index.html")
    else:
        return render_template("Task3.html")


if __name__ == '__main__':
    app.run(port=8000)
