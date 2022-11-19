# CPSC-449-Web Backend Engineering:Project-2

Guided by Professor: Kenytt Avery @ProfAvery

# Project Members:

1. Debdyuti Das
2. Janiece Garcia
3. Peining Lo
4. Sravani Kallmepudi

# Project description: 

This project is about splitting monolith service that exposed two different sets of resources in project 1, into two separate microservices and authenticating the endpoints of each service.

Configuration files:
1. Procfile is a mechanism for declaring what commands are run by your application to start the app 
2. Update the nginx.config into default file present in /etc/nginx/sites-enabled

The following are the steps to run the project:
1. Installing and configuring Nginx:
    > sudo apt update
    > sudo apt install --yes nginx-extras
2. Clone the github repository https://github.com/plo8/cpsc449-project2.git
3. Then cd into the cpsc449-project2 folder and run the following commands:
    > mkdir var
3. Run both the init scripts to populate the database and automatically connect the api to the database. 
    > ./bin/init_auth.sh
    
    > ./bin/init_game.sh
4. Start the services    
    > foreman start -m auth=1,game=3   
    
Now the API can be run using Postman(the method which we followed) or using curl or httpie.

ENDPOINT 1:
For registering an user: @app.route("/register", methods=["POST"])
```bash
http POST http://tuffix-vm/register/ username=Rain password=rain@123
```
ENDPOINT 2:
For authenticating the user:@app.route("/auth", methods=["GET"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/auth
```

ENDPOINT 3: 
For creating a new game for an authenticated user:@app.route("/game/", methods=["POST"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/game
```
ENDPOINT 4:
For getting the game state of the authenticated user:@app.route("/game/:gameId", methods=["GET"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/game/:gameId
```
 
ENDPOINT 5:
List all the games for the authenticated user:@app.route("/my-games", methods=["GET"])
```bash
Ex: On postman with Basic-Auth: http://tuffix-vm/my-games  
