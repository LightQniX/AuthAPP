from flask import Flask, render_template, request, flash, render_template_string, redirect, Response, make_response
import psycopg2
import json
import random
import string
import os


port = int(os.environ.get('PORT', 5000))

dbhost = 'ec2-54-216-17-9.eu-west-1.compute.amazonaws.com'
dbname = 'djrs2mt5np83b'
dbuser = 'womlylvmxosadm'
dbport = '5432'
dbpass = '300cba31baa710789df66e6dbda88f1183d92462e00f8c92ff44687a27ac601c'
con = psycopg2.connect(dbname=dbname, port=dbport, user=dbuser, password=dbpass, host=dbhost)
con.set_session(autocommit=True)
cur = con.cursor()


tokens = []
app = Flask(__name__)


def check(t):
    for i in range(0, len(tokens)):
        if t in tokens[i]:
            return True
    return False


@app.route("/getUser/<token>", methods=["POST", "GET"])
def getUser(token):
    username = None
    for i in range(0, len(tokens)):
        if token in tokens[i]:
            username = tokens[i][1]
            break


    if username:
        cur.execute(f"select * from users where login='{username}'")
        r = cur.fetchall()[0]
        data = {
            'id': r[0],
            'username': r[1],
            'nickname': r[3]
        }
        return data, 200

    else:
        return {'error': 'user not found'}, 404


@app.route("/isauthed/<token>", methods=["POST", "GET"])
def isauthed(token):
    if check(token):
        return {'auth': 'authed'}, 200
    else:
        return {'auth': 'not authed'}, 403


@app.route("/login", methods=["POST", "GET"])
def lonig():
    global tokens

    try:
        if check(request.cookies.get('token')):
            return {'auth': 'already authed'}, 403
    except:
        pass

    login = request.args.get('login')
    password = request.args.get('password')


    cur.execute(f"select * from users where login='{login}'")
    res = cur.fetchall()


    if res:
        res = res[0]
        if password == res[2]:
            tk = ''.join(random.choices(string.ascii_lowercase, k=64))
            tokens.append([tk, res[1]])

            resp = make_response(json.dumps({
                                            'auth': 'success',
                                            'cookie':
                                                     {
                                                      'token': tk,
                                                      'username': res[1]
                                                      }
                                             }))

            resp.set_cookie('token', tk)
            resp.set_cookie('username', res[1])
            print(f'login >> {tk}')
            return resp, 200

        else:
            return {'auth': 'wrong password'}, 403

    else:
        return {'auth': 'user no found'}, 404







@app.route("/logout", methods=["POST", "GET"])
def logout():

    for i in range(0, len(tokens)):
        if request.cookies.get('token') in tokens[i]:
            tokens.pop(i)
            print(tokens)
            return {'auth': 'logged out'}, 200

    return {'auth': 'not logged in'}, 403






@app.route("/register", methods=["POST", "GET"])
def register():

    login = request.args.get('login')
    password = request.args.get('password')
    nickname = request.args.get('nickname')

    cur.execute(f"select * from users where login='{login}'")
    res = cur.fetchall()

    if not res:
        cur.execute(f"INSERT INTO users (login, password, nickname) VALUES('{login}', '{password}', '{nickname}');" )
        return {'auth': 'registered successfully'}, 200
    else:
        return {'auth': 'user exists'}, 403

app.run(threaded=True,host='0.0.0.0', port=port)

#app.run(debug=True, host='localhost', port=5003)















