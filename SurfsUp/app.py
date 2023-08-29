# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
stations = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"

    )
#Precipitation route
@app.route("/api/v1.0/precipitation")
#Create the precipitation function
def precipitation():
    #Set to query the last 12 months of precipitation data
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    preceip_scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= year_ago).\
    order_by(measurement.date).all()
    session.close()
#Create a dictionary from the row data and append to a list of precip   
    precip = {date: prcp for date, prcp in preceip_scores}
#Return the JSON representation of your dictionary   
    return jsonify(precip)
#Stations route
@app.route('/api/v1.0/stations')
#Create the stations function
def stations_func():
    #Query all stations
    total_stations = session.query(stations.station, stations.name, stations.latitude, stations.longitude).all()
    #Convert list of tuples into normal list
    stations_list = list(np.ravel(total_stations))
    session.close()
    #Return a JSON list of stations from the dataset
    return jsonify(stations_list)
#Temperature route
@app.route('/api/v1.0/tobs')
#Create the tobs function
def tabs():
    #Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query the primary station for all tobs from the last year
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    #Find the most active station
    most_active = active_stations[0][0]
    
    sel = [measurement.tobs]
    #Query the last 12 months of temperature observation data for this station
    most_active_temps = session.query(*sel).\
    filter(measurement.station == most_active).all()

    session.close()
    #Convert list of tuples into normal list
    all_tops = list(np.ravel(most_active_temps))
    #Return a JSON list of temperature observations (tobs) for the previous year
    return jsonify(all_tops)
#Start and end route
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
#Create the start_end function
def start_end(start = None, end = None):
    #Select statement
    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    if not end: 
        #Convert string to date
        start = dt.datetime.strptime(start, '%Y%m%d')
        #Query the temperatures
        most_active_temps = session.query(*sel).\
            filter(measurement.date >= start).all()
        session.close()
        #Convert list of tuples into normal list
        temps = list(np.ravel(most_active_temps))
        #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
        return jsonify(temps)
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    start = dt.datetime.strptime(start, '%Y%m%d')
    
    end = dt.datetime.strptime(end, '%Y%m%d')
    #Query the temperatures
    most_active_temps = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date >= end).all()
    session.close()
    #Convert list of tuples into normal list
    temps = list(np.ravel(most_active_temps))
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    return jsonify(temps)







# Define main behavior
if __name__ == '__main__':
    app.run(debug=True)