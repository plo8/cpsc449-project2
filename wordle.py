import dataclasses
import collections
from operator import itemgetter
import databases
from quart import Quart, g, request, jsonify, abort
from quart_schema import validate_request, RequestSchemaValidationError, QuartSchema
import sqlite3
import toml
import random

app = Quart(__name__)
QuartSchema(app)
app.config.from_file(f"./etc/{__name__}.toml", toml.load)

@dataclasses.dataclass
class userData:
    id: int
    username: str
    password: str

async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database(app.config["DATABASES"]["URL"])
        # db = g._sqlite_db = databases.Database('sqlite+aiosqlite:/wordle.db')
        await db.connect()
    return db

@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()

@app.route("/users/all", methods=["GET"])
async def all_users():
    db = await _get_db()
    all_users = await db.fetch_all("SELECT * FROM userData;")

    return list(map(dict, all_users))  


#------------Registering a new user-----------------#

@app.route("/register/", methods=["POST"])
@validate_request(userData)
async def register_user(data):
    db = await _get_db()  
    
    userData = dataclasses.asdict(data)   
    
    try:
        id = await db.execute(
            """
            INSERT INTO userData(id, username, password)
            VALUES(:id, :username, :password)
            """,
            userData,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    
    userData["id"] = id      
    return jsonify({"statusCode": 200, "message": "Successfully registered!"})

@app.errorhandler(RequestSchemaValidationError)
def bad_request(e):
    return {"error": str(e.validation_error)}, 400

@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409

@app.errorhandler(401)
def unauthorized(e):
    return {"error": str(e)}, 401


SearchParam = collections.namedtuple("SearchParam", ["name", "operator"])
SEARCH_PARAMS = [
    
    SearchParam(
        "username",
        "=",
    ),
    SearchParam(
        "password",
        "=",
    ),
    
]

#-------------Authenticating the credentials for Login----------------
@app.route('/auth', methods=['GET'])
async def authenticate():
    query_parameters = request.args
    #db = await _get_db()    
      
    
    sql = "SELECT username,password FROM userData"
    conditions = []
    values = {}

    for param in SEARCH_PARAMS:
        if query_parameters.get(param.name):
            if param.operator == "=":
                conditions.append(f"{param.name} = :{param.name}")
                values[param.name] = query_parameters[param.name]               

    if conditions:
        sql += " WHERE "
        sql += " AND ".join(conditions)

    app.logger.debug(sql)

    db = await _get_db()
    results = await db.fetch_all(sql, values)  
   
    
    my_list= list(map(dict, results))    
    pwd = list(map(itemgetter('password'), my_list))
    name = list(map(itemgetter('username'), my_list))    
   
    result_dict= {}

    for key in name:
         for value in pwd:
             result_dict[key] = value
             pwd.remove(value)
             break      
    

    for key in result_dict:
        if(request.authorization.password==result_dict[key] and request.authorization.username==key  ) :        
            return jsonify({"statusCode": 200, "authenticated": "true"})   
    # WWW-Authenticate error for 401
    return jsonify({"statusCode": 401, "error": "Unauthorized", "message": "Login failed !" })     
    
    
# ---------------GAME API---------------

def getGuessState(guess, secret):
    word = guess
    secretWord = secret

    matched = []
    valid = []

    for i in range(len(secretWord)):
        correct = word[i] == secretWord[i]
        valid.append({"inSecret": correct, "wrongSpot": False, "used": True if correct else False})
        matched.append(correct)

    for i in range(len(secretWord)):
        currentLetter = secretWord[i]
        for j in range(len(secretWord)):
            if i != j:
                if not(matched[i]) and not(valid[j].get("used")):
                    if word[j] == currentLetter:
                        valid[j].update({"inSecret": True, "wrongSpot": True, "used": True})
                        matched[i] = True

    data = []
    index = 0

    for i in word:
        d = {}
        del valid[index]["used"]
        d[i] = valid[index]
        data.append(d)
        index += 1

    return data

async def gameStateToDict(game):
    db = await _get_db()
    secretWord = await db.fetch_one("SELECT word FROM correct WHERE id=:id", values={"id": game[2]})
    secretWord = secretWord[0]

    state = {"guessesLeft": game[3], "finished": True if game[4] == 1 else False, "gussedWords": []}

    timeGuessed = 6 - game[3]
    guessedWords = []

    for i in range(timeGuessed):
        word = game[i + 5]
        wordState = {word: getGuessState(word, secretWord)}
        guessedWords.append(wordState)

    state["gussedWords"] = guessedWords

    return state

async def updateGameState(game, word, db, finished = 0):
    numGuesses = game[3]
    nthGuess = 6 - numGuesses + 1

    sql = "UPDATE game SET guesses=:numGuess, finished=:finished, "
    suffix = "guess" + str(nthGuess) + "=:guess" + " WHERE id=:id"

    gameFinished = finished
    if numGuesses - 1 == 0:
        gameFinished = 1
    await db.execute(sql + suffix, values={"numGuess": numGuesses - 1, "id": game[0], "finished": gameFinished, "guess": word })

# ---------------CREATE NEW GAME---------------

@app.route("/game", methods=["POST"])
async def newGame():
    db = await _get_db()

    body = await request.get_json()
    userId = body.get("userId")

    if not(userId):
        abort(400, "Please provide the user id")

    user = await db.fetch_one("SELECT * FROM userData WHERE id=:userId", values={"userId": userId})

    if not(user):
        abort(404, "Could not find user with this id")

    words = await db.fetch_all("SELECT * FROM correct")
    num = random.randrange(0, len(words), 1)

    data = {"wordId": words[num][0], "userId": user[0]}

    id = await db.execute(
        """
        INSERT INTO game(wordId, userId)
        VALUES(:wordId, :userId)
        """,
        data)

    res = {"gameId": id, "guesses": 6}
    return res, 201

@app.errorhandler(400)
def noUserId(e):
    return {"error": str(e).split(':', 1)[1][1:]}, 400

@app.errorhandler(404)
def userNotFound(e):
    return {"error": str(e).split(':', 1)[1][1:]}, 404

# ---------------GUESS A WORD---------------

@app.route("/game/<int:gameId>", methods=["PATCH"])
async def guess(gameId):
    db = await _get_db()

    body = await request.get_json()

    userId = body.get("userId")
    word = body.get("word").lower()

    if not(userId) or not(word):
        abort(400, "Please provide the user id and the guess word")

    game = await db.fetch_one("SELECT * FROM game WHERE id=:id", values={"id": gameId})

    # Check iff game exists
    if not(game):
        abort(404, "Could not find a game with this id")

    if int(userId) != game[1]:
        abort(400, "This game does not belong to this user")

    user = await db.fetch_one("SELECT * FROM userData WHERE id=:userId", values={"userId": userId})

    # Check if user exists
    if not(user):
        abort(404, "Could not find this user")

    # Check if game is finished
    if game[4] == 1:
        abort(400, "This game has already ended")

    # Check if word is valid
    if len(word) != 5:
        abort(400, "This is not a valid guess")

    wordIsValid = False

    # check if word is in correct table
    correct = await db.fetch_one("SELECT word FROM correct WHERE word=:word", values={"word": word})

    if not(correct):
        valid = await db.fetch_one("SELECT word FROM valid WHERE word=:word", values={"word": word})
        wordIsValid = valid is not None

    # invalid guess
    if not(wordIsValid) and not(correct):
        abort(400, "Guess word is invalid")

    # Not correct but valid
    secretWord = await db.fetch_one("SELECT word FROM correct WHERE id=:id", values={"id": game[2]})
    secretWord = secretWord[0]

    # guessed correctly
    if word == secretWord:
        await updateGameState(game, word, db, 1)

        return {"word": {"input": word, "valid": True, "correct": True}, 
        "numGuesses": game[3] - 1}

    await updateGameState(game, word, db, 0)

    data = getGuessState(word, secretWord)

    return {"word": {"input": word, "valid": True, "correct": False}, 
        "gussesLeft": game[3] - 1, 
        "data": data}

@app.errorhandler(400)
def noUserId(e):
    return {"error": str(e).split(':', 1)[1][1:]}, 400

@app.errorhandler(404)
def userNotFound(e):
    return {"error": str(e).split(':', 1)[1][1:]}, 404


# ---------------LIST GAMES FOR A USER---------------

@app.route("/users/<int:userId>/games", methods=["GET"])
async def myGames(userId):
    db = await _get_db()
    
    user = await db.fetch_one("SELECT * FROM userData WHERE id=:id", values={"id": userId})

    if not(user):
        abort(404, "Could not find this user")

    games = await db.fetch_all("SELECT * FROM game WHERE userId=:id", values={"id": userId})

    gamesList = list(map(dict, games))
    res = []

    for game in gamesList:
        res.append({"gameId": game.get("id"), "guessesLeft": game.get("guesses"), "finished": True if game.get("finished") == 1 else False})

    return res

@app.errorhandler(404)
def userNotFound(e):
    return {"error": str(e).split(':', 1)[1][1:]}, 404

# ---------------GET GAME STATE---------------

@app.route("/game/<int:gameId>", methods=["GET"])
async def getGame(gameId):
    db = await _get_db()

    game = await db.fetch_one("SELECT * FROM game WHERE id=:id", values={"id": gameId})

    if not(game):
        return {"message": "No game found with this id"}, 404
    
    return await gameStateToDict(game)

# game
# 0 = id
# 1 = userId
# 2 = wordId
# 3 = guesses
# 4 = finished
# 5 = guess1
# 6 = guess2
# 7 = guess3
# 8 = guess4
# 9 = guess5
# 10 = guess6