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
