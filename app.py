import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, historicData

from FinanceDBUtils import database

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'flask'

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

mydb = database(app)


# Make sure API key is set
# if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # get user's cash
    userid = session["user_id"]

    # fetch user's positions
    positions = mydb.findPortfoliosbyUserId(userid)

    for position in positions:
        stock = lookup(position['symbol'])
        if stock:
            position['name'] = stock['name']
            position['price'] = stock['price']

        position['price'] = usd(position['price'])

    return render_template('index.html', items=positions)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add shares of stock"""
    if request.method == "POST":

        # variables
        userid = session["user_id"]
        symbol = request.form.get('symbol')

        try:
            stock = validationStockOrderRequestData(symbol)
        except ValueError as err:
            print(err.args)
            return apology(err.args[0],err.args[1])

        # more variables
        symbol = stock['symbol']
        price = stock['price']

        positions = mydb.findPortfoliosbyUserIdAndSymbol(userid, symbol)
        # if don't have this stock, insert a new row, otherwise update row
        if len(positions) != 1:
            mydb.InsertToPortfolios(userid, symbol, price)
        else:
            apology("symbol is existed", 400)

        return redirect("/")
    return render_template("add.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        user = mydb.findUser(request.form.get("username"))
        # Ensure username exists and password is correct
        if not user or not check_password_hash(user[2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user[0]

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    username = request.form.get("username")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # check username & password submission looks ok
        try:
            validateUserRegistration(username, password, confirmPassword)
            mydb.registerUser(username, generate_password_hash(password, method='pbkdf2:sha256', salt_length=8))
            return redirect("/")
        except ValueError as err:
            print(err.args)
            return apology(err.args[0],err.args[1])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Sell shares of stock"""
    userid = session["user_id"]
    if request.method == "POST":
        # variables
        symbol = request.form.get('symbol')

        try:
            stock = validationStockOrderRequestData(symbol)
        except ValueError as err:
            print(err.args)
            return apology(err.args[0],err.args[1])

        # more variables
        symbol = stock['symbol']

        position = mydb.findPortfoliosbyUserIdAndSymbol(userid, symbol)

        # if user can't afford
        if not position:
            return apology("you don't have this symbol", 400)

        mydb.DeletePortfolio(userid, symbol)

        return "Success", 200

    symbols = mydb.findPortfolioSymbolsbyUserId(userid)
    print(symbols)
    return render_template("remove.html",items=symbols)



def validateUserRegistration(username, password, confirmPassword):
    # 1. username is not empty
    if not username:
        raise ValueError('must have username',400)
    # 2. password
    if not password:
        raise ValueError('must have password',400)
    # 3. confirm
    if not (confirmPassword) or (confirmPassword != password):
        raise ValueError('password must match confirpassword',400)

    # 4. check password format
    #The password must have at least one uppercase and one lowercase character.
    #The password must have a minimum of one numeric character.
    #The password must have at least one special symbol.
    #The password must be 6 to 10 characters long.
    regular_expression = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,10}$"
    # compiling regex to create regex object
    pattern = re.compile(regular_expression)
    # searching regex
    valid = re.search(pattern, password)
    # validating conditions
    if not valid:
        raise ValueError('password must follow the requirements',400)
    # 5. check username
    user = mydb.findUser(username)
    if user:
        raise ValueError('username is duplicated',400)

    return 0


def validationStockOrderRequestData(symbol):
    if not symbol :
        raise ValueError("symbol is required", 400)

    stock = lookup(symbol)

    if not stock:
        raise ValueError("can't fetch the symbol from IEX", 400)

    return stock

@app.route("/chart", methods=["GET"])
@login_required
def chart():

    symbol = request.args.get('symbol')
    timeframe = request.args.get('timeframe')
    print(symbol)
    print(timeframe)

    data = mydb.getPlotData(symbol, timeframe)

    return render_template("chart.html",title='AAPL Chart', max=data['maxPrice'], labels=data['labels'], values=data['closePrices'])
