import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt


engine=create_engine("sqlite:///Resources/hawaii.sqlite")  #initialize database access
Base=automap_base()
Base.prepare(engine, reflect=True)
meas = Base.classes.measurement


app = Flask(__name__)  #flask page start

@app.route("/")
def welcome():   #intro page for navigation
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD - max/min/avg temperature since date<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD - max/min/avg temperature from date1-date2"
    )
@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    lst=session.query(meas.date).order_by(meas.date.desc()).limit(1).all()
    # Calculate the date 1 year ago from the last data point in the databasete
    lst_dt = dt.datetime.strptime(lst[0][0], '%Y-%m-%d')
    year_ago = lst_dt - dt.timedelta(days=365)
    year_ago_str = year_ago.strftime('%Y-%m-%d')
    # Perform a query to retrieve the data and precipitation scores
    precip = session.query(meas.date,meas.prcp,meas.station).filter(meas.date > year_ago_str)
    #convert into dictionary
    data = {}
    for date, prcp, station in precip:
        data[date]={}
        data[date]['station']=station
        data[date]['prcp']=prcp
    return(jsonify(data))



@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    stat = session.query(meas.station,func.count(meas.date)).group_by(meas.station).all()
    stats = {}
    for station, totals in stat:
        stats[station]={}
        stats[station]['Measurements']=totals
    return(jsonify(stats))


@app.route("/api/v1.0/tobs")
def temp():
    session=Session(engine)
    lst=session.query(meas.date).order_by(meas.date.desc()).limit(1).all()
    # Calculate the date 1 year ago from the last data point in the databasete
    lst_dt = dt.datetime.strptime(lst[0][0], '%Y-%m-%d')
    year_ago = lst_dt - dt.timedelta(days=365)
    year_ago_str = year_ago.strftime('%Y-%m-%d')
    #query the popular station
    stat_1 = session.query(meas.date,meas.tobs).filter(meas.date>year_ago_str).filter(meas.station=='USC00519281') 
    data = {}
    for date, tp in stat_1:
        data[date]={}
        data[date]['Temp']=tp
    return(jsonify(data))


@app.route("/api/v1.0/<start>")
def starting(start):
    session=Session(engine)
    max_t = session.query(func.max(meas.tobs)).filter(meas.date>=start).all()
    min_t =session.query(func.min(meas.tobs)).filter(meas.date>=start).all()
    avg_t = session.query(func.avg(meas.tobs)).filter(meas.date>=start).all()
    data = {}
    data['max']=max_t[0][0]
    data['min']=min_t[0][0]
    data['avg']=round(avg_t[0][0],2)
    return(jsonify(data))
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session=Session(engine)
    max_t = session.query(func.max(meas.tobs)).filter(meas.date<=end).filter(meas.date>=start).all()
    min_t =session.query(func.min(meas.tobs)).filter(meas.date<=end).filter(meas.date>=start).all()
    avg_t = session.query(func.avg(meas.tobs)).filter(meas.date<=end).filter(meas.date>=start).all()
    data = {}
    data['max']=max_t[0][0]
    data['min']=min_t[0][0]
    data['avg']=round(avg_t[0][0],2)
    return(jsonify(data))

if __name__ == '__main__':
    app.run(debug=True)
