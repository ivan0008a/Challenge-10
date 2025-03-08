from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


app = Flask(__name__)


database_path = "sqlite:////Users/aleksandrivanov/Desktop/challenge 10/Resources/hawaii.sqlite"
engine = create_engine(database_path)


Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station



@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"<h1>Hawaii Climate API</h1>"
        f"<h2>Available Routes:</h2>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a> - Last 12 months of precipitation</li>"
        f"<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a> - List of weather stations</li>"
        f"<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a> - Last 12 months of temperature observations</li>"
        f"<li>/api/v1.0/&lt;start&gt; - Temperature stats from start date</li>"
        f"<li>/api/v1.0/&lt;start&gt;/&lt;end&gt; - Temperature stats from start to end date</li>"
        f"</ul>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON of last 12 months of precipitation data."""
    session = Session(engine)


    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    prev_year = recent_date - dt.timedelta(days=365)


    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= prev_year.strftime("%Y-%m-%d")).all()
    session.close()


    prcp_dict = {date: prcp for date, prcp in prcp_results}
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """"""
    session = Session(engine)
    stations_list = session.query(Station.station).all()
    session.close()

    return jsonify([station[0] for station in stations_list])


@app.route("/api/v1.0/tobs")
def tobs():
    """"""
    session = Session(engine)


    active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(
        func.count(Measurement.station).desc()).first()[0]


    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    prev_year = recent_date - dt.timedelta(days=365)


    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == active_station,
                                                                            Measurement.date >= prev_year.strftime(
                                                                                "%Y-%m-%d")).all()
    session.close()

    return jsonify([{date: tobs} for date, tobs in tobs_results])


@app.route("/api/v1.0/<start>")
def temp_start(start):
    """

    """

    session = Session(engine)


    results = (session.query(func.min(Measurement.tobs),
                             func.avg(Measurement.tobs),
                             func.max(Measurement.tobs))
                      .filter(Measurement.date >= start)
                      .all())
    session.close()


    tmin, tavg, tmax = results[0]


    return jsonify({
        "Start Date": start,
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    })

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """

    """

    session = Session(engine)


    results = (session.query(func.min(Measurement.tobs),
                             func.avg(Measurement.tobs),
                             func.max(Measurement.tobs))
                      .filter(Measurement.date >= start)
                      .filter(Measurement.date <= end)
                      .all())
    session.close()

    tmin, tavg, tmax = results[0]


    return jsonify({
        "Start Date": start,
        "End Date": end,
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    })


if __name__ == "__main__":
    app.run(debug=True)



