import numpy as np
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database intso a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List of all the available api routes."""
    return (
        f"This is the homepage that lists all the available API routes below:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
     # Calculate and store the date a year from the last date in the DB
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query precipitation and dates of the last year
    results = session.query(Measurement.prcp,Measurement.date ).filter(Measurement.date >= last_year).all()
    # Close the session
    session.close()
    # Create a dictionary for all precipitation results in the last year 
    all_precip = {date: prcp for date, prcp in results}
    # Return all precipitation results in the last year as a JSON list
    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    all_stations = session.query(Station.station).all()
    # Close the session
    session.close()
    # Convert station list of tuples into normal list
    station_ID_list = list(np.ravel(all_stations))
    # Return the list of stations by station ID as a JSON list
    return jsonify(station_ID_list=station_ID_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate and store the date a year from the last date in the DB
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query all temperatures of the most active station
    temp_observations = session.query(Measurement.tobs,Measurement.date).filter(Measurement.date >= last_year).filter(Measurement.station =="USC00519281").all()
    # Close the session
    session.close()
    # obtain the dates and relevant temperatures observed and store them
    all_temp_observations = {date: tobs for date, tobs in temp_observations}
    # Return the dates and relevant temperatures as a JSON list
    return jsonify(all_temp_observations)



@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    # If no end date provided, it still returns the summary of the results.
    if not end:
        # Define the start time paramaters and format
        start = dt.datetime.strptime(start, "%Y%m%d")
        # Create our session (link) from Python to the DB
        session = Session(engine)
        # Query the session for the Min, Max and Avg temperatures observed for the date provided
        results=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
        #Close a session
        session.close()
        # Convert list of tuples into normal list
        results_list = list(np.ravel(results))
        return jsonify(results_list)
    # Define the start and end time paramaters and format
    start = dt.datetime.strptime(start, "%Y%m%d")
    end = dt.datetime.strptime(end, "%Y%m%d")
# Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the session for the Min, Max and Avg temperatures observed for the date range provided
    summary_results= session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    #Close a session
    session.close()
    # Convert list of tuples into normal list
    summaryofresults = list(np.ravel(summary_results))
    # Return the Min, Max and Avg temperatures as a JSON list
    return jsonify(summaryofresults)
   
   
if __name__ == '__main__':
    app.run(debug=True)