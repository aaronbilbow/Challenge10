# Import necessary libraries
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
from datetime import datetime, timedelta

# Step 1: Create a SQLAlchemy engine to connect to the database
engine = sqlalchemy.create_engine("sqlite:///hawaii.sqlite")

# Step 2: Reflect the tables into classes using automap_base
Base = automap_base()
Base.prepare(engine, reflect=True)

# Step 3: Link Python to the database by creating a SQLAlchemy session
session = Session(engine)

# Create a Flask app
app = Flask(__name__)

# Step 4: Define routes for your API

# Homepage route to list all available routes
@app.route("/")
def homepage():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the most active station in the last 12 months<br/>"
        f"/api/v1.0/&lt;start&gt; - Temperature statistics from a given start date (format: YYYY-MM-DD)<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; - Temperature statistics between a start and end date (format: YYYY-MM-DD/YYYY-MM-DD)"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query and return a JSON list of stations
    station_data = session.query(Station.station, Station.name).all()
    stations_list = [{"station": station, "name": name} for station, name in station_data]

    return jsonify(stations_list)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Identify the most active station with the highest number of observations
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(sqlalchemy.func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year ago from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query temperature observations for the most active station for the last 12 months
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a JSON list of temperature observations
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Temperature statistics route (with start date)
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Query and return temperature statistics for dates greater than or equal to the start date
    temperature_stats = session.query(
        sqlalchemy.func.min(Measurement.tobs).label("TMIN"),
        sqlalchemy.func.avg(Measurement.tobs).label("TAVG"),
        sqlalchemy.func.max(Measurement.tobs).label("TMAX")
    ).filter(Measurement.date >= start).all()

    # Convert the query results to a JSON list of temperature statistics
    temperature_stats_list = [
        {"TMIN": TMIN, "TAVG": TAVG, "TMAX": TMAX} for TMIN, TAVG, TMAX in temperature_stats
    ]

    return jsonify(temperature_stats_list)

# Temperature statistics route (with start and end date)
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    # Query and return temperature statistics for dates between start and end (inclusive)
    temperature_stats = session.query(
        sqlalchemy.func.min(Measurement.tobs).label("TMIN"),
        sqlalchemy.func.avg(Measurement.tobs).label("TAVG"),
        sqlalchemy.func.max(Measurement.tobs).label("TMAX")
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a JSON list of temperature statistics
    temperature_stats_list = [
        {"TMIN": TMIN, "TAVG": TAVG, "TMAX": TMAX} for TMIN, TAVG, TMAX in temperature_stats
    ]

    return jsonify(temperature_stats_list)

if __name__ == "__main__":
    app.run(debug=True)
