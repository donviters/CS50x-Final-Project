# CS50 Final Project - Tennis
#### Video Demo:  <https://youtu.be/RAHinhZ9cPc>
#### Description:

#### My final project is a web app designed to store information about tennis players, tournaments, and matches. I got this idea because at the Guayaquil Tenis Club, where I play, there are multiple tournaments throughout the year, and it would be nice to have a site where people could see rankings, history between two players, and general player information. I filled the database with a little bit of professional tennis players information to showcase how the app works.

## app.py
#### This is the python application. There are multiple routes that will take the user to the corresponding html files. I used the finance problem app.py as a reference and modified it to fit my project.

## helpers.py
#### Recycled apology and login_required functions from finance problem.

## @app.route("/login")
#### The first page of the program is login (function recycled from finance problem) and will take the user to login.html template.
#### Not every user will be able to register, only administrators can create new accounts, so as to protect the database from people entering wrong information.
#### However, users that don't have an account will be able to access the first three main menu options because they don't involve messing with the database information, only querying.
#### To login in you can use username 'cs50' and password 'cs50'. This username is independent from the database to make user the staff can access and test the project.

## @app.route("/")
#### index.html is the main page. It's a background image of a tennis court and you can select six different options from the navbar main menu: Search Player, Head to Head, Ranking, Add Player, Add Tournament, and Add Match.

## @app.route("/search_player")
#### The first menu option will take the user to the search_player.html template. He can enter the name of a player in a text input element, for example Roger Federer and submit by pressing the button.
#### If the user enters the name of a player not in the database, an apology will be returned. Also, the user will be alerted if the name field is blank after pressing the button.
#### The app will take the user to player_info.html template detailing the player information in a table: name, age, country and rank. Tennis ranks are determined by the points earned in matches during the last 1 year period, so if a player hasn't played for a long time, his rank will appear as inactive.

## @app.route("/head_to_head")
#### The second menu option will take the user to the head_to_head.html template. The user will be able to choose two players from the database and submit by pressing the button. You can try selecting Roger Federer and Andre Agassi for a good example.
#### If the user doesn't choose any of the players or he chooses the same player twice, an alert will be displayed.
#### After submitting, the app will take the user to the h2h_detail.html template, where two tables will be displayed, showing the details of matches between the players selected.

## @app.route("/ranking")
#### The third menu option will take the user to the ranking.html template. It will display a table of players ordered by the number of points each has in descending order. Note that tennis rankings only consider points won during the last 1 year period.
#### Matches from 2023 Grand Slam tournmanets starting at the semi finals have been entered in the database, so that you can see a good example.

## @app.route("/add_player")
#### The fourth menu option will take the user to the add_player.html template. It will display a form composed of two text inputs for first name and last name, a date input for the birthdate, and a select input for the country. The user will be alerted if any of these fields hadn't been completed when pressing the button.
#### If the user enters a player that already exists in the database, an apology will be displayed.
#### After entering correct information for a new player and submitting by pressing the button, the app will return to the homepage and a message will be flashed confirming that a new players has been added.

## @app.route("/add_tournament")
#### The fifth menu option will take the user to the add_tournament.html template. It will display a text input for the name of the tournament, a select input for the year the tournament was played, and a select input for the court surface the event was played in. The user will be alerted if any of the fields are blank after pressing the button.
#### If the user enters a tournament event that already exists, an apology will be displayed.
#### After entering a new tournament information correctly and pressing the button, the app will return to the homepage and a message will be flashed confirming that a new tournament has been added.

## @app.route("/add_match")
#### The sixth and last menu option will take the user to the add_match.html template. It will display a select input for an event where a match took place, a select input for the player who won the match, a select input for the player who lost the match, a select input for the round of the tournament the match corresponded to, the final score of the match, and the date of the match. The user will be alerted if any of the fields are blank or if he chose the same player for winner and loser of the match, after presing the button.
#### If the user enters a tournament event that already exists, an apology will be returned.
#### After entering a new match information correctly and pressing the button, the app will return to the homepage and a message will be displayed confirming that a new match has been added.

## @app.route("/register")
#### Register function recycled from the finance problem. Takes the user to the register.html template, which displays three text inputs for username, password, and password confirmation. The user will be alerted if any of the fiels are blanks after pressing the button.
#### In this app, users are admins, and only they can create new admins. This is to prevent malicious users from messing with the database.

## scripts.js
#### Javascript code to animate the menu buttons from all html templates.

## schema.sql
#### Code used to create all the tables in the database.

## tennis.db
#### Database file.