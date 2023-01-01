from flask_mysqldb import MySQL
import json
from datetime import datetime

from helpers import historicData

class database:
    def __init__(self, app):
        self.app = app
        self.myDatabase = MySQL(app)
        print("db init")




    def registerUser(self, username, password):
        print("registerUser: " + username)
        try:
            cursor = self.myDatabase.connection.cursor()
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            val = (username, password)
            cursor.execute(sql, val)
            self.myDatabase.connection.commit()
        except Exception as e:
            print(e)




    def findUser(self, username):
        print("find user")
        try:
            cursor = self.myDatabase.connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
            user = cursor.fetchone()
            print(user)
            return user
        except Exception as e:
            print(e)

    #############################################

    def findPortfoliosbyUserId(self, userid):
        print("find findPortfoliosbyUserId ", userid)
        try:
            cursor = self.myDatabase.connection.cursor()
            cursor.execute('SELECT * FROM portfolios WHERE user_id = %s', (userid,))
            records = cursor.fetchall()

            row_headers = [x[0] for x in cursor.description]  # this will extract row headers

            json_data = []
            for result in records:
                json_data.append(dict(zip(row_headers, result)))
            temp =  json.dumps(json_data)
            return json.loads(temp)

        except Exception as e:
            print(e)

    def findPortfolioSymbolsbyUserId(self, userid):
        print("findPortfolioSymbolsbyUserId ", userid)
        try:
            cursor = self.myDatabase.connection.cursor()
            cursor.execute('SELECT symbol FROM portfolios WHERE user_id = %s', (userid,))
            records = cursor.fetchall()

            # want string array like ths ['PBR', 'COP']
            json_data = []
            for result in records:
                json_data.append(result[0])
            temp =  json.dumps(json_data)
            return json.loads(temp)

        except Exception as e:
            print(e)

    def InsertToPortfolios(self, userid,symbol,price):
        print("InsertToPortfolios", userid, symbol)
        try:
            query = """INSERT INTO portfolios (user_id, symbol, price, date) VALUES(%s, %s, %s, %s)"""

            date = datetime.now().strftime("%b %d %Y %H:%M:%S")
            cursor = self.myDatabase.connection.cursor()
            cursor.execute(query, (userid, symbol, price, date))
            self.myDatabase.connection.commit()

        except Exception as e:
            print(e)


    def DeletePortfolio(self, userid,symbol):
        print("DeletePortfolio", userid, symbol)
        try:
            query = """DELETE FROM portfolios WHERE user_id=%s AND symbol=%s"""

            cursor = self.myDatabase.connection.cursor()
            cursor.execute(query, (userid, symbol))
            self.myDatabase.connection.commit()

        except Exception as e:
            print(e)

    def findPortfoliosbyUserIdAndSymbol(self, userid, symbol):
        print("find findPortfoliosbyUserId ", userid, symbol)
        try:
            cursor = self.myDatabase.connection.cursor()
            cursor.execute('SELECT * FROM portfolios WHERE user_id = %s AND symbol = %s', (userid,symbol))
            records = cursor.fetchall()

            row_headers = [x[0] for x in cursor.description]  # this will extract row headers

            json_data = []
            for result in records:
                json_data.append(dict(zip(row_headers, result)))
            temp = json.dumps(json_data)
            return json.loads(temp)

        except Exception as e:
            print(e)


    def getPlotData(self, symbol, range):
        data =  historicData(symbol, range)

        labels = []
        closeprices = []
        maxPrice = 0

        for d in data:
            labels.append(d['label'])
            closeprices.append(d['close'])

        maxPrice = max(closeprices)
        return {
            "labels": labels,
            "closePrices": closeprices,
            "maxPrice": maxPrice
        }
