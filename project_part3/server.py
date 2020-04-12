"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

# import query_submission

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

rate_types = ['Winning Rate', 'First Three Rate']
entities = ['Jockey', 'Horse', 'Trainer']
time_frames = ['Races', 'Days']

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://hw2735:5438@35.231.103.173/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)


#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/')
def index():
    """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

    # DEBUG: this is debugging code to see what request looks like
    # print(request.args)

    return render_template("index.html", rate_types=rate_types, entities=entities, time_frames=time_frames,
                           query_data=[], default_error=False, custom_error=False)


@app.route('/run_query', methods=['POST'])
def run_query():
    query_validation = validate_n_entries_field(request.form)
    if query_validation != True:
        error = query_validation
        query_results = []
    else:
        user_query = request.form['query']
        if user_query.split(' ')[0].lower() != 'select':
            # Invalid request
            error = 'We currently only accept queries starting with "SELECT"'
            query_results = []
        else:
            print('Custom Query: {}'.format(user_query))
            error = False

            # Send query to DB
            query_results = []
            print("Start running query")
            cursor = g.conn.execute(user_query)
            print("Finished running query")
            for result in cursor:
                query_results.append(result)
            cursor.close()
            print("the Query results are")
            for row in query_results:
                print(row)

        #     query_results = [[1, 2, 3], ['a', 'b', 'c']] # For DEBUG

    return render_template("index.html", rate_types=rate_types, entities=entities, time_frames=time_frames,
                           query_data=query_results, default_error=False, custom_error=error)


@app.route('/run_default_query', methods=['POST'])
def run_default_query():
    # Runs a pre-defined query
    print('in default query: {}'.format(request.form))
    query_validation = validate_n_entries_field(request.form)
    if query_validation == True:
        print('valid request!')
        error = False

        # Get chosen query parameters
        form = request.form
        n_elements = form['n_entries']
        rate_type = form['rate_type']
        entity_type = form['entity_type']
        time_frame = form['time_frame']
        print(n_elements, rate_type, entity_type, time_frame)

        # TODO need to construct query here
        try:
            n_elements = str(int(n_elements))
        except:
            n_elements = "0"

        if rate_types == 'Winning Rate':
            rate_query = "1"
        else:
            rate_query = "3"
        if entity_type == 'Jockey':
            entity_table = "jockey"
            entity_name = "jockey_name"
        elif entity_type == 'Horse':
            entity_table = "horse"
            entity_name = "horse_name"
        else:
            entity_table = "train_horse NATURAL JOIN trainer"
            entity_name = "trainer_name"

        if time_frame == 'Days':

            query = "WITH \
            tmp AS (SELECT * FROM enter_event NATURAL JOIN race_result NATURAL JOIN " + entity_table + \
                    " WHERE event_date >= (CURRENT_DATE - " + n_elements + " ) ),\
            tmp2 AS (SELECT " + entity_name + ", COUNT(*) AS win FROM tmp\
            WHERE place <=" + rate_query + \
                    " GROUP BY " + entity_name + "),\
            tmp3 AS (SELECT " + entity_name + " , COUNT(*) AS total FROM tmp\
                GROUP BY " + entity_name + " ),\
            tmp4 AS (SELECT * from tmp2 NATURAL JOIN tmp3)\
            SELECT " + entity_name + ", win / CAST(total AS DECIMAL) AS rate FROM tmp4 ORDER BY " + entity_name + " ;"
        else:
            query = "WITH \
            tmp AS (SELECT * FROM enter_event NATURAL JOIN race_result NATURAL JOIN " + entity_table + \
                    " WHERE event_id >= ((SELECT event_id FROM enter_event ORDER BY event_date DESC LIMIT 1) - " + n_elements + " ) ),\
            tmp2 AS (SELECT " + entity_name + ", COUNT(*) AS win FROM tmp\
            WHERE place <=" + rate_query + \
                    " GROUP BY " + entity_name + "),\
            tmp3 AS (SELECT " + entity_name + " , COUNT(*) AS total FROM tmp\
                GROUP BY " + entity_name + " ),\
            tmp4 AS (SELECT * from tmp2 NATURAL JOIN tmp3)\
            SELECT " + entity_name + ", win / CAST(total AS DECIMAL) AS rate FROM tmp4 ORDER BY " + entity_name + " ;"

        # Send query to DB
        print("Start running query")
        print(query)
        cursor = g.conn.execute(query)
        print("Finished running query")
        query_results = []
        for result in cursor:
            query_results.append(result)
        cursor.close()
        print("the Query results are")
        for row in query_results:
            print(row)

    #     query_results = [['a', 'b', 'c'], ['a', 'b', 'c']] # For DEBUG
    else:
        # query_validation is an error string
        print('invalid request')
        query_results = []
        error = query_validation

    return render_template("index.html", rate_types=rate_types, entities=entities, time_frames=time_frames,
                           query_data=query_results, default_error=error, custom_error=False)


def validate_n_entries_field(form):
    # expected_keys = {'rate_type', 'entity_type', 'n_entries', 'time_frame'}
    # keys = set(form.keys())
    # if expected_keys - keys != set():
    #   return 'Please select one of the three rate types at the top.'

    try:
        _ = int(form['n_entries'])
    except:
        print('except hit')
        return 'Please enter a number in the "Number of Entries" field.'

    return True


if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
