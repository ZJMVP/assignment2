from math import radians, sin, cos, asin, sqrt
from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zjmvp'

driver = '{ODBC Driver 18 for SQL Server}'
database = 'zj-earth'
server = 'zj-server.database.windows.net'
username = "jie_zhao"
password = "Kd1016686103"

with pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password) as conn:
    with conn.cursor() as cursor:
        temp = []
        cursor.execute("SELECT TOP 3 time, id FROM earthquake")
        while True:
            r = cursor.fetchone()
            if not r:
                break
            print(str(r[0]) + " " + str(r[1]))
            temp.append(r)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/mag', methods=['GET', 'POST'])
def mag():
    if request.method == 'POST':
        mag = request.form["mag"]
        query = "SELECT * FROM dbo.earthquake where mag >=" + mag
        cursor.execute(query)
        results = cursor.fetchall()
        return render_template('showMag.html', rows=results, temp=0, cnt=len(results))
    return render_template('ShowMag.html', temp=1)


@app.route('/searchRange', methods=['GET', 'POST'])
def searRange():
    if request.method == 'POST':
        Range1 = str(request.form['Range1'])
        Range2 = str(request.form['Range2'])
        Fromdate = request.form['Fromdate']
        Todate = request.form['Todate']
        query = "SELECT * FROM dbo.earthquake where (mag BETWEEN '" + Range1 + "' and '" + Range2 + "') and (CAST(time as date) BETWEEN CAST('" + Fromdate + "' as date) and CAST('" + Todate + "' as date)) "
        cursor.execute(query)
        results = cursor.fetchall()
        return render_template("searchRange.html", length=len(results), rows=results)
    else:
        return render_template("searchRange.html")


def distance(lat1, lat2, lon1, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


@app.route('/speLocation', methods=['POST', 'GET'])
def sLocation():
    if request.method == 'POST':
        lat = request.form['lat']
        lon = request.form['lon']
        distan = request.form['distance']
        query = "Select time,depth,latitude,longitude,id,mag,place from earthquake"
        cursor.execute(query)
        lat = float(lat)
        lon = float(lon)
        distan = float(distan)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            x = distance(lat, float(row[2]), lon, float(row[3]))
            if x <= distan:
                results.append(row)
        return render_template("speLocation.html", rows=results, length=len(results))
    else:
        return render_template('speLocation.html')


@app.route("/cluster", methods=['GET', 'POST'])
def Cluster():
    query = "SELECT mag,COUNT(*) FROM earthquake  group by mag"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template("Cluster.html", msg="completed", rows=results)


@app.route('/comparison', methods=['POST', 'GET'])
def comparison():
    begin = "06:00:00.0000000 +00:00"
    end = "18:00:00.0000000 +00:00"
    query1 = "SELECT id FROM dbo.earthquake where mag > 4.0 and (CAST(time as time) BETWEEN CAST('" + begin + "' as time) and CAST('" + end + "' as time)) "
    cursor.execute(query1)
    days = cursor.fetchall()
    earthDayCount = len(days)
    query2 = "SELECT id FROM dbo.earthquake where mag > 4.0"
    cursor.execute(query2)
    wholeDay = cursor.fetchall()
    earthCount = len(wholeDay)
    winner = "Night"
    if earthDayCount > (earthCount - earthDayCount):
        winner = "Day"
    return render_template("Comparison.html", dayCount=earthDayCount, nightCount=earthCount - earthDayCount, winner=winner)


if __name__ == '__main__':
    app.run(debug=True)
