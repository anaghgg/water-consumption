import sys
import pandas as pd
import mysql.connector
from flask import Flask, render_template, request,redirect, url_for
from pip._internal import main as _main
from predict import Future

mydb = mysql.connector.connect(
  host="xxxxx",
  user="xxxx",
  passwd="xxxx",
  use_pure=True,
  database="xxxx"
)

c=mydb.cursor(prepared=True)

app = Flask(__name__)



@app.route('/')
def home():
    mydb.commit()
    return render_template("home.html")

@app.route('/signup')
def signup():
	return render_template("signup.html")

@app.route('/takedata')
def takedata():
    name=str(request.args.get('name'))
    email=str(request.args.get('email'))
    password=str(request.args.get('password'))
    house=str(request.args.get('house'))
    members=str(request.args.get('members'))
    if len(name)==0 or len(email)==0 or len(password)==0 or len(house)==0 or len(members)==0:
            msg="Fill up all the fields ! "
            return render_template("error.html",msg=msg)
    else:
        try:
            query="SELECT * FROM USER WHERE EMAIL=%s"
            val=(email,)
            c.execute(query,val)
            if len(list(c.fetchall()))>0:
                msg="User with this email already exists!"
                return render_template("error.html",msg=msg)
            else:
                try:
                    query="INSERT INTO USER VALUES (%s,%s,%s,%s,%s)"
                    val=(email,password,name,house,members)
                    c.execute(query,val)
                    try:
                        table="HOUSE"+house
                        table=table.replace(" ","")
                        c.execute("CREATE TABLE "+table+" (ID INT PRIMARY KEY AUTO_INCREMENT, MONTH_YEAR VARCHAR(20), AMOUNT VARCHAR(15))")
                        
                        predtable="PRED"+house
                        predtable=predtable.replace(" ","")
                        c.execute("CREATE TABLE "+predtable+" (ID INT PRIMARY KEY AUTO_INCREMENT, MONTH_YEAR VARCHAR(20), AMOUNT VARCHAR(15))")
                        return render_template("home.html")
                    except:
                        msg="Internal Error"
                        return render_template("error.html",msg=msg)
                        
                except:
                    msg="Internal Error"
                    return render_template("error.html",msg=msg)
                   
        
        except:
            msg="Internal Error"
            return render_template("error.html",msg=msg)  

    
@app.route('/loginpage')
def loginpage():
    return render_template("login.html")

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    try:
        if request.method=='POST':
            password=str(request.form['password'])
            email=str(request.form['email'])
            query="SELECT HOUSE FROM USER WHERE EMAIL=%s and PASSWORD=%s"
            val=(email,password)
            try:
                c.execute(query,val)
            except:
                msg="Internal Error"
                return render_template("error.html",msg=msg)

            rows=list(c.fetchone())
            if len(rows)>0:
                house=rows[0]
                print("\nLogged In\n")
                del password
                del email
                return redirect(url_for("profile",house=house))
            else:
                msg="Wrong credentials"
                return render_template("error.html",msg=msg)
    except:
        msg="Wrong credentials"
        return render_template("error.html",msg=msg)       


@app.route('/profile/<house>')
def profile(house):
    return render_template("profile.html",house=house)
    
@app.route('/adminlogin')
def adminlogin():
    return render_template("adminlogin.html")


@app.route('/verifyadmin',methods=['GET','POST'])
def verifyadmin():
    adminID=str(request.form['id'])
    password=str(request.form['password'])
    if adminID=="555" and password=="admin123" :
        return redirect(url_for("admin"))
    else:
        msg="Wrong credentials"
        return render_template("error.html",msg=msg)
    
@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/update')
def update():
    house=str(request.args.get('house'))
    consume=str(request.args.get('consume'))
    month=str(request.args.get('month'))

    table="HOUSE"+house
    table=table.replace(" ","")
    query="INSERT INTO "+table+"(MONTH_YEAR,AMOUNT) VALUES ('" + month+ "','" + consume +"')"
    print("\n\n"+query+"\n\n")

    try:
        c.execute(query)
        mydb.commit()
        return redirect(url_for("admin"))
    except:
        msg="Internal Error"
        return render_template("error.html",msg=msg)
    
            


@app.route('/predictions/<house>')
def predictions(house):
    table="HOUSE"+house
    table=table.replace(" ","")
    try:
        c.execute("SELECT * FROM "+table)
        df=pd.DataFrame(c.fetchall())
        df.columns=['id','month','amt']
        if len(df)<25:
            msg="Not enough data available\nPredictions can't be made!"
            return render_template("error.html",msg=msg)
        else:
            future=Future()
            pred=future.getPredictions(df)
            if pred is None:
                msg="Internal Error"
                return render_template("error.html",msg=msg)
            else:
                month=pred[0]
                predict=pred[1]
                predTable="PRED"+house
                predTable=predTable.replace(" ","")
                
                c.execute("SELECT * FROM "+predTable+" WHERE MONTH_YEAR='"+month+"' ")
                if len(list(c.fetchall()))==0:
                    query="INSERT INTO "+predTable+"(MONTH_YEAR,AMOUNT) VALUES ('" + month+ "','" + predict +"')"
                    c.execute(query)
                    
                df=pd.read_sql("SELECT * FROM "+predTable+" ORDER BY ID DESC",con=mydb)
                df=df.drop(columns=['ID'])
                month_year=df['MONTH_YEAR'].tolist()
                amount=df['AMOUNT'].tolist()
                size=len(amount)
                if size>1:
                    p=month_year[1]
                    query="SELECT AMOUNT FROM "+table+" WHERE MONTH_YEAR='"+p+"'"
                    print(query)
                    c.execute(query)
                    l=list(c.fetchone())
                    a=str(l[0])
                    return render_template("predict.html",month_year=month_year,amount=amount,size=size,actual=a)
                else:
                    return render_template("predict.html",month_year=month_year,amount=amount,size=size,actual="NA")
                    
                    
                    
    except:
        msg="Internal Error"
        return render_template("error.html",msg=msg)
                    
    

@app.route('/consumption/<house>')
def consumption(house):
    table="HOUSE"+house
    table=table.replace(" ","")
    try:
        df=pd.read_sql("SELECT * FROM "+table+" ORDER BY ID DESC",con=mydb)
        df=df.drop(columns=['ID'])
        month_year=df['MONTH_YEAR'].tolist()
        amount=df['AMOUNT'].tolist()
        size=len(amount)
        bill=[]
        
        for i in range(size):
            amt=int(int(amount[i])*0.05)
            amt=str(amt)
            bill.append(amt)
            
        return render_template("consumption.html",house=house,month_year=month_year,amount=amount,bill=bill,size=size)
        
    except:
        msg="Internal Error"
        return render_template("error.html",msg=msg)
        

app.secret_key = 'super secret key'
app.run()


    

