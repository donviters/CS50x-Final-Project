import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tennis.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Create a permanent user independent from the database to make sure CS50 staff can test the app
        if request.form.get("username") == "cs50" and request.form.get("password") == "cs50":
            session["user_id"] = 3
            return redirect("/")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    """Home page"""
    return render_template("index.html")


@app.route("/search_player", methods=["GET", "POST"])
def search_player():
    """Search for a player and show a table with his info"""
    if request.method == "GET":
        return render_template("search_player.html")

    elif request.method == "POST":
        first_name = request.form.get("first_name").strip().upper()
        last_name = request.form.get("last_name").strip().upper()

        player = db.execute("SELECT * FROM players JOIN countries ON players.country_id = countries.id WHERE first_name = ? AND last_name = ?", first_name, last_name)
        # Apologize if the player is not in the database

        if len(player) == 0:
            return apology("Player not in database")

        player = player[0]
        # https://www.codingem.com/how-to-calculate-age-in-python/
        # Calculate the players age
        birthdate = player["birthdate"]
        birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
        birthdate = birthdate.date()
        today = datetime.now()
        today = today.date()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        # Get the player's ranking
        date = datetime.now().date()
        date_1_year_ago = date - relativedelta(years=1)
        # Tennis rankings only consider the points earned during the last 1 year
        rank = db.execute("SELECT rank FROM (SELECT ROW_NUMBER() OVER() as rank, first_name, last_name, a_date, total_points FROM (SELECT first_name, last_name, a_date, sum(points) AS total_points FROM points JOIN players ON points.player_id = players.id WHERE a_date BETWEEN ? AND ? GROUP BY player_id ORDER BY total_points DESC)) WHERE first_name = ? AND last_name = ?", date_1_year_ago, date, first_name, last_name)
        # if player isn't in ranking, then set rank as inactive
        if len(rank) == 0:
            rank = "INACTIVE"
        else:
            rank = rank[0]["rank"]

        return render_template("player_info.html", player=player, age=age, rank=rank)


@app.route("/head_to_head", methods=["GET", "POST"])
def head_to_head():
    """Show match history between 2 players"""
    players = db.execute("SELECT * FROM players ORDER BY last_name")

    if request.method == "GET":
        return render_template("head_to_head.html", players=players)

    elif request.method == "POST":
        player1_id = request.form.get("player1")
        player2_id = request.form.get("player2")

        # Apologize if the 2 players entered are the same
        if player1_id == player2_id:
            return apology("choose 2 different players")

        # Create the matches dictionary, which will contain details of each match between the 2 players
        matches = db.execute("SELECT * FROM matches " +
        "JOIN events ON matches.event_id = events.id " +
        "JOIN tournaments ON tournaments.id = events.tournament_id " +
        "JOIN surfaces ON events.surface_id = surfaces.id " +
        "JOIN rounds ON matches.round_id = rounds.id " +
        "WHERE (winner_id = ? OR winner_id = ?) AND (loser_id = ? OR loser_id = ?) " +
        "ORDER BY a_date DESC",
        player1_id, player2_id, player1_id, player2_id)

        # In the dictionary above we have all column values required but not the player's names. Create a player dictionary with key value pairs id-name
        row = db.execute("SELECT * FROM players WHERE id = ?", player1_id)
        player1_name = row[0]["first_name"] + " " + row[0]["last_name"]

        row = db.execute("SELECT * FROM players WHERE id = ?", player2_id)
        player2_name = row[0]["first_name"] + " " + row[0]["last_name"]

        # Query the database to find out how many matches each player won
        row = db.execute("SELECT count(*) FROM matches WHERE winner_id = ? AND loser_id = ?", player1_id, player2_id)
        player1_wins = row[0]["count(*)"]

        row = db.execute("SELECT count(*) FROM matches WHERE winner_id = ? AND loser_id = ?", player2_id, player1_id)
        player2_wins = row[0]["count(*)"]

        players = {int(player1_id) : [player1_name, player1_wins] , int(player2_id) : [player2_name, player2_wins]}

        return render_template("h2h_detail.html", matches=matches, players=players)


@app.route("/ranking", methods=["GET", "POST"])
def ranking():
    """Get a ranking of players."""
    date = datetime.now().date()
    date_1_year_ago = date - relativedelta(years=1)
    # Tennis rankings only consider the points earned during the last 1 year
    ranking = db.execute("SELECT ROW_NUMBER() OVER() as rank, first_name, last_name, a_date, total_points FROM (SELECT first_name, last_name, a_date, sum(points) AS total_points FROM points JOIN players ON points.player_id = players.id WHERE a_date BETWEEN ? AND ? GROUP BY player_id ORDER BY total_points DESC)", date_1_year_ago, date)
    return render_template("ranking.html", ranking=ranking)

@app.route("/add_player", methods=["GET", "POST"])
@login_required
def add_player():
    """Add a player to the database"""
    if request.method == "GET":
        # Got a list of all countries from https://pytutorial.com/python-country-list/?expand_article=1
        countries = ['Afghanistan', 'Aland Islands', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia, Plurinational State of', 'Bonaire, Sint Eustatius and Saba', 'Bosnia and Herzegovina', 'Botswana', 'Bouvet Island', 'Brazil', 'British Indian Ocean Territory', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos (Keeling) Islands', 'Colombia', 'Comoros', 'Congo', 'Congo, The Democratic Republic of the', 'Cook Islands', 'Costa Rica', "Côte d'Ivoire", 'Croatia', 'Cuba', 'Curaçao', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands (Malvinas)', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern Territories', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard Island and McDonald Islands', 'Holy See (Vatican City State)', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran, Islamic Republic of', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', "Korea, Democratic People's Republic of", 'Korea, Republic of', 'Kuwait', 'Kyrgyzstan', "Lao People's Democratic Republic", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao', 'Macedonia, Republic of', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico', 'Micronesia, Federated States of', 'Moldova, Republic of', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestinian Territory, Occupied', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Réunion', 'Romania', 'Russian Federation', 'Rwanda', 'Saint Barthélemy', 'Saint Helena, Ascension and Tristan da Cunha', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin (French part)', 'Saint Pierre and Miquelon', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Sint Maarten (Dutch part)', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Georgia and the South Sandwich Islands', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'South Sudan', 'Svalbard and Jan Mayen', 'Swaziland', 'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Taiwan, Province of China', 'Tajikistan', 'Tanzania, United Republic of', 'Thailand', 'Timor-Leste', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'United States Minor Outlying Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela, Bolivarian Republic of', 'Viet Nam', 'Virgin Islands, British', 'Virgin Islands, U.S.', 'Wallis and Futuna', 'Yemen', 'Zambia', 'Zimbabwe']
        # Convert all countries to uppercase
        countries = [country.upper() for country in countries]

        return render_template("add_player.html", countries=countries)

    elif request.method == "POST":
        first_name = request.form.get("first_name").strip().upper()
        last_name = request.form.get("last_name").strip().upper()
        birthdate = request.form.get("birthdate")
        country = request.form.get("country")

        # Apologize if the user left blank fields. Javascript in the HTML will hopefully handle this, but just in case
        if first_name == "" or last_name == "" or birthdate == "" or country == "":
            return apology("complete all fields")

        # Try inserting country into the countries database. Country name is unique, so duplicates won't be accepted
        try:
            db.execute("INSERT INTO countries (country_name) VALUES (?)", country)
        except:
            pass

        # Get the country id from the countries database
        row = db.execute("SELECT * FROM countries WHERE country_name = ?", country)
        country_id = row[0]["id"]

        # Try inserting player into database. first name and last name pair has to be unique. Error will occur if attempting to add duplicate
        try:
            db.execute("INSERT INTO players (first_name, last_name, birthdate, country_id) VALUES (?, ?, ?, ?)", first_name, last_name, birthdate, country_id)
        except:
            return apology("player already exists")

        flash("Player Successfully Added")
        return render_template("index.html")

@app.route("/add_tournament", methods=["GET", "POST"])
@login_required
def add_tournament():
    """Add a tournament to the database"""
    if request.method == "GET":
        surfaces = ['HARD', 'CLAY', 'GRASS']
        # Pass in list of surfaces for the select form
        return render_template("add_tournament.html", surfaces=surfaces)

    elif request.method == "POST":
        # Retrieve the values from the form into variables
        tournament_name = request.form.get("tournament_name").strip().upper()
        year = request.form.get("year")
        surface = request.form.get("surface")

        # Javascript should take care of blank fields but just in case
        if tournament_name == "" or year == "" or surface == "":
            return apology("complete all fields")

        # Try adding a tournament to the tournaments table. The names must be unique so duplicates won't be added
        try:
            db.execute("INSERT INTO tournaments (tournament_name) VALUES (?)", tournament_name)
        except:
            pass

        # Try adding a surface to the surface table. The names must be unique so duplicates won't be added
        try:
            db.execute("INSERT INTO surfaces (surface_name) VALUES (?)", surface)
        except:
            pass

        # Get the surface id
        row = db.execute("SELECT * FROM surfaces WHERE surface_name = ?", surface)
        surface_id = row[0]["id"]

        # Now add the tournament at the events table. Apologize if it already exists
        row = db.execute("SELECT * FROM tournaments WHERE tournament_name = ?", tournament_name)
        tournament_id = row[0]["id"]
        try:
            db.execute("INSERT INTO events (tournament_id, a_year, surface_id) VALUES (?, ?, ?)", tournament_id, year, surface_id)
        except:
            return apology("Tournament already exists")

        flash("Tournament Successfully Added")
        return render_template("index.html")


@app.route("/add_match", methods=["GET", "POST"])
@login_required
def add_match():
    """Add match to database"""
    # Dictionary of rounds as keys with values the points for winning match at that particular round
    rounds = {"RR" : 0, "R128" : 10, "R64" : 45, "R32" : 90, "R16" : 180, "QF" : 360, "SF" : 720, "F" : 1200}

    if request.method == "GET":
        events = db.execute("SELECT * FROM tournaments JOIN events ON tournaments.id = events.tournament_id ORDER BY tournament_name, a_year")
        players = db.execute("SELECT * FROM players ORDER BY last_name")
        return render_template("add_match.html", events=events, players=players, rounds=rounds)

    elif request.method == "POST":
        event_id = request.form.get("event_id")
        winner_id = request.form.get("winner_id")
        loser_id = request.form.get("loser_id")
        round = request.form.get("round")
        score = request.form.get("score").strip()
        date = request.form.get("date")

        # Try adding the round to the database. round name is unique so any duplicates will not add
        try:
            db.execute("INSERT INTO rounds (round_name) VALUES (?)", round)
        except:
            pass

        # Get the round id
        row = db.execute("SELECT * FROM rounds WHERE round_name = ?", round)
        round_id = row[0]["id"]

        # Search on the database if there's already a match between the two players at that tournament at that particular round and if so apologize
        row = db.execute("SELECT * FROM matches WHERE event_id = ? " +
                         "AND (winner_id = ? OR winner_id = ?) AND (loser_id = ? OR loser_id = ?)" +
                         "AND round_id = ?",
                         event_id, winner_id, loser_id, winner_id, loser_id, round_id)
        if len(row) > 0:
            return apology("there's already a match between selected players in tournament round")

        # Insert match in matches table
        db.execute("INSERT INTO matches (event_id, winner_id, loser_id, round_id, score, a_date) VALUES (?, ?, ?, ?, ?, ?)", event_id, winner_id, loser_id, round_id, score, date)

        # Get the inserted match id
        row = db.execute("SELECT * FROM matches WHERE event_id = ? AND winner_id = ? AND loser_id = ? AND round_id = ? AND score = ? AND a_date = ?", event_id, winner_id, loser_id, round_id, score, date)
        match_id = row[0]["id"]

        # Now add points in points table. The player who lost the match will be awarded points according the the round where he lost
        points = rounds[round]
        db.execute("INSERT INTO points (player_id, match_id, a_date, points) VALUES (?, ?, ?, ?)", loser_id, match_id, date, points)

        # If player won the tournament add 800 points
        if round == "F":
            points = 2000
            db.execute("INSERT INTO points (player_id, match_id, a_date, points) VALUES (?, ?, ?, ?)", winner_id, match_id, date, points)

        flash("Match Successfully Added")
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    """Register user"""
    # User reached route via get. Show user the register form
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via post. Check for errors in the submited form data
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Apologize if user left blank any of the form fields
        if username == "" or password == "" or confirmation == "":
            return apology("all fields are required")
        # Apologize if password and confirmation password didn't match
        if password != confirmation:
            return apology("passwords didn't match")
        # Query the users database for the username entered. Apologize if it's already taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username taken")

        # Insert new user into the users database
        password_hash = generate_password_hash(password)
        id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash
        )

        # Log user in
        session["user_id"] = id
        return redirect("/")