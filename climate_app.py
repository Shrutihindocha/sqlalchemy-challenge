# importing dependencies
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import numpy as np

#Setting up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#creating session
session = Session(engine)

#converting end_date to datetime format
from datetime import datetime
end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
for _ in end_date:
    end_date = _
end_date = datetime.strptime(end_date, '%Y-%m-%d')
start_date = end_date - dt.timedelta(days=365)

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-02-02<br/>"
        f"/api/v1.0/2016-02-02/2016-05-02<br/>"
    )

# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    print("Server received request for 'precipitation' page...")
    ppt_data = dict(session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date))
    return jsonify(ppt_data)

# Define what to do when a user hits the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    print("Server received request for 'stations' page...")
    stations = session.query(Station.station).all()
    stations = list(np.ravel(stations))
    return jsonify(stations)

# Define what to do when a user hits the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")
    session = Session(engine)
    stations_all = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).order_by(func.count(Measurement.station).desc())
    station_highest_obs = stations_all[0][0]

    tobs = session.query(Measurement.tobs).\
            filter(Measurement.station == station_highest_obs).all()
    tobs = list(np.ravel(tobs))
    return jsonify(tobs)

# Define what to do when a user hits the /api/v1.0/<start> and /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>")
def temperatures1(start):
    session = Session(engine)
    stations_all = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc())
    station_highest_obs = stations_all[0][0]

    temperatures1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
    temperatures1 = list(np.ravel(temperatures1))
    return jsonify(temperatures1)

@app.route("/api/v1.0/<start>/<end>")
def temperatures(start, end):
    session = Session(engine)
    stations_all = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc())
    station_highest_obs = stations_all[0][0]

    temperatures = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        
    temperatures = list(np.ravel(temperatures))
    return jsonify(temperatures)

if __name__ == "__main__":
    app.run(debug=True)