import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Session link from python to DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    data = session.query(Measurement.date, Measurement.prcp).\
           order_by(Measurement.date).all()

    precip_dates = []

    for date, prcp in data:
        new_dict = {}
        new_dict[date] = prcp
        precip_dates.append(new_dict)

    session.close()

    return jsonify(precip_dates)


@app.route("/api/v1.0/stations")
def stations():

    results = session.query(Station.station).all()
    stations = list(np.ravel(results))

    session.close()
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():

    
    lastdate = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    last_date = dt.datetime.strptime(lastdate[0], '%Y-%m-%d')

    
    query_date = dt.date(last_date.year, last_date.month,
                         last_date.day) - dt.timedelta(days=365)

   
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= query_date).all()

    all_tobs = []
    for row in results:
        tobs_dict = {}
        tobs_dict["date"] = row.date
        tobs_dict["tobs"] = row.tobs
        all_tobs.append(tobs_dict)

    session.close()
    return jsonify(all_tobs)


@app.route("/api/v1.0/temp/start")
def stats():

    start_date = session.query(func.min(Measurement.date)).all()[0][0]

    sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    temp_lstuple = session.query(*sel).filter(Measurement.date >= start_date).all()

    session.close()

    temp_pram1_list = list(np.ravel(temp_lstuple))
    temp_list =[]
    for t in temp_lstuple:
        temp_dict = {}
        temp_dict["Min Temp"] = temp_pram1_list[0]
        temp_dict["Avg Temp"] = temp_pram1_list[1]
        temp_dict["Max Temp"] = temp_pram1_list[2]
        temp_list.append(temp_dict)
    return jsonify(temp_list)


@app.route("/api/v1.0/temp/start/end")
def tempstartend(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    temps_q = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temps = list(np.ravel(temps_q))

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
