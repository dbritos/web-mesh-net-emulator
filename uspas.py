#!/usr/bin/python2.7
"""
runs on the server, reads form input, prints HTML
"""
import cgi, sys
import mysql.connector
import string
import time
from validate_email import validate_email
from datetime import date
import cgitb
cgitb.enable()
print("Content-type: text/html")

db = mysql.connector.connect(user='root',password='dgi', database='mesh')
cursor = db.cursor()
form = cgi.FieldStorage()

head = """
<!DOCTYPE html>
<html>
<head>
	<title>Leaflet.draw vector editing handlers</title>
	<meta content="text/html;charset=utf-8" http-equiv="Content-Type">

"""

fin = """
</body>
</html>
"""
login = """
</head>
<body>
<form method="POST" action="uspas.py" onsubmit="return checkForm(this);">
<fieldset>
<legend>Login</legend>
<p>Username: <input title="Enter your mail has username" type="email" required placeholder="Enter a valid email address" name="username"></p>
<p>Password: <input title="Password must contain at least 6 characters, including UPPER/lowercase and numbers" type="password" name="pwd1" onchange="
  this.setCustomValidity(this.validity.patternMismatch ? this.title : '');
  if(this.checkValidity()) form.pwd2.pattern = this.value;
"></p>
<p><input type="submit" name="login" value="Login"></p>
<p><input type="submit" name="registrar" value="Register"></p>
</fieldset>
</form>
"""

def printmenu(num):
    print("</head>")
    print("<body>")
    print("<form action='link.py' method='post'>")
    print("<input type='hidden' name=sid value=" + str(num)  +">")
    print("<button type='submit'>Edit Network</button>")
    print("<button type='submit' formmethod='post' formaction='link.py'>Run Network</button>")
    print("</form>")
    print("<form action='uspas.py' method='post'>")
    print("<button type='submit'>Return to login</button>")
    print("</form>")


registrar = """
</head>
<body>
<form method="POST" action="uspas.py" onsubmit="return checkForm(this);">
<fieldset>
<legend>Register</legend>
<p>Username: <input title="Enter your mail has username" type="email" required placeholder="Enter a valid email address" name="username"></p>
<p>Password: <input title="Password must contain at least 6 characters, including UPPER/lowercase and numbers" type="password" required pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}" name="pwd1" onchange="
  this.setCustomValidity(this.validity.patternMismatch ? this.title : '');
  if(this.checkValidity()) form.pwd2.pattern = this.value;
"></p>
<p>Confirm Password: <input title="Please enter the same Password as above" type="password" required pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}" name="pwd2" onchange="
  this.setCustomValidity(this.validity.patternMismatch ? this.title : '');
"></p>
<p><input type="submit" name="register" value="Register"></p>
</fieldset>
</form>

"""
print(head)

if 'registrar' in form:
    print(registrar)
elif 'register' in form:
    email = form['username'].value
    if validate_email(email,verify=True):
        data =(form['username'].value,form['pwd1'].value,3,date.today())
        insert_stmt = (
            "INSERT INTO usuarios (mail,password,level,fecha) "
            "VALUES (%s, %s, %s, %s)")
        cursor.execute(insert_stmt,data)
        db.commit()
        print(login)
    else:
        print("<p><font color='red'>Mail not exist try again register</font></p>")
        print(registrar)
elif 'login' in form:
    data =form['username'].value
    cursor.execute ("SELECT password,numero FROM usuarios WHERE mail = '%s'"  %(data))
    pasnum = cursor.fetchone()
    if pasnum != None:
        passw,num = pasnum
        if passw == form['pwd1'].value:
            printmenu(num)
        else:
            print("<p><font color='red'>Bad password, try again if not have username register</font></p>")
            print(login)    
    else:
        print("<p><font color='red'>Bad username, try again if not have username register</font></p>")
        print(login)
elif 'sid' in form:
    printmenu(form['sid'].value)
else:
    print(login)
print(fin)
