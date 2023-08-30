from flask import *
import ibm_db

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30119;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jwd91864;PWD=MJNlfu6uIlz77nRu",'','')
print(conn)

app=Flask(__name__)


@app.route('/')
def home():
    return render_template('register.html')
@app.route('/register1',methods=['POST'])
def register1():
    x=[x for x in request.form.values()]
    print(x)
    NAME=x[0]
    EMAIL=x[1]
    PASSWORD=x[2]
    sql="SELECT * FROM REGISTER WHERE EMAIL=?"
    prep_stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(prep_stmt,1,EMAIL)
    ibm_db.execute(prep_stmt)
    account=ibm_db.fetch_assoc(prep_stmt)
    print(account)
    if account:
        return render_template('login.html',pred="You are already a member,Please login using your credentials")
    else:
        sql1="INSERT INTO REGISTER VALUES(?,?,?)"
        prep_stmt1=ibm_db.prepare(conn,sql1)
        ibm_db.bind_param(prep_stmt1,1,NAME)
        ibm_db.bind_param(prep_stmt1,2,EMAIL)
        ibm_db.bind_param(prep_stmt1,3,PASSWORD)
        ibm_db.execute(prep_stmt1)
        return render_template('login.html',pred="Registration Successfull,Please login")

@app.route('/login',methods=['POST'])
def login(): 
    x=[x for x in request.form.values()]
    print(x)
    NAME=x[0]
    PASSWORD=x[1]
    sql="SELECT * FROM REGISTER WHERE NAME=?"
    prep_stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(prep_stmt,1,NAME)
    ibm_db.execute(prep_stmt)
    account=ibm_db.fetch_assoc(prep_stmt)
    print(account)
    if(account):
        USERNAME=account["NAME"]
        USERPASSWORD=account["PASSWORD"]
        USEREMAIL=account["EMAIL"]
        if NAME==USERNAME and PASSWORD==USERPASSWORD:
            sql2="INSERT INTO LOGIN VALUES(?,?)"
            prep_stmt3=ibm_db.prepare(conn,sql2)
            ibm_db.bind_param(prep_stmt3,1,USERNAME)
            ibm_db.bind_param(prep_stmt3,2,USEREMAIL)
            ibm_db.execute(prep_stmt3)
            return render_template('login.html',pred="Login Successful")
        else:
            return render_template('login.html',pred="Check your Username and Password")
    else:
        return render_template('login.html',pred="No account found,Please register")
    
@app.route('/signout',methods=['POST'])
def signout():
    
    # sql3="DELETE FROM LOGIN WHERE NAME=?"
    # prep_stmt4=ibm_db.prepare(conn,sql3)
    # ibm_db.bind_param(prep_stmt4,1,"vignesh")
    # ibm_db.execute(prep_stmt4)
    return render_template('login.html',pred="Signed Out")

@app.route('/login1')
def login1():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')


if __name__=="__main__":
    app.run(debug=True,port=8080)