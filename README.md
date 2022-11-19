# CPSC-449-Web Backend Engineering:Project-2

Guided by Professor: Kenytt Avery @ProfAvery

# Project Members:

1. Debdyuti Das
2. Janiece Garcia
3. Peining Lo
4. Sravani Kallmepudi

# Project description: 

This project is intented to effectively build a RESTful Web back-end API for a game which is similar to the very well known game "Wordle", with difference of few conditions or features from the original game. Some of these features which are included are letting more than one game to be played per day per player and as well as offering different games to different players.

In this project basically we are splitting monolith service that exposed two different sets of resources in project 1, into two separate microservices and authenticating the endpoints of each service as users-api and games-api, which makes use of Python's Quart web framework, and utilize 6 endpoints to allow an user to interact with the game. Th web services also makes use of NginX for HTTP Authentication, as well as load balancing.

## Configuration files:
1. Procfile is a mechanism for declaring what commands are run by your application to start the app 
2. Update the nginx.config into default file present in /etc/nginx/sites-enabled

## The following are the steps to run the project:
1. Installing and configuring Nginx:
```bash
sudo apt update
sudo apt install --yes nginx-extras
```
2. Clone the github repository:
```bash
git clone https://github.com/plo8/cpsc449-project2.git
```
3. Then cd into the cpsc449-project2 folder and run the following commands:
```bash
cd cpsc449-project2/
mkdir var
```
4. Run both the init scripts to populate the database and automatically connect the api to the database. 
```bash
./bin/init_auth.sh    
./bin/init_game.sh
````
4. Start the services    
```bash
foreman start -m auth=1,game=3  
```
    
Now the API can be run using Postman(the method which we followed) or using curl or httpie.

## ENDPOINT 1:
For registering an user: @app.route("/register", methods=["POST"])
```bash
http POST http://tuffix-vm/register/ username=Rain password=rain@123
```
## ENDPOINT 2:
For authenticating the user:@app.route("/auth", methods=["GET"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/auth
```
## ENDPOINT 3: 
For creating a new game for an authenticated user:@app.route("/game/", methods=["POST"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/game
```
## ENDPOINT 4:
For getting the game state of the authenticated user:@app.route("/game/:gameId", methods=["GET"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/game/:gameId
``` 
## ENDPOINT 5:
List all the games for the authenticated user:@app.route("/my-games", methods=["GET"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/my-games  
```
## ENDPOINT 6:
Guessing a word: @app.route("/game/:gameId", methods=["PATCH"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/game/:gameId
```
