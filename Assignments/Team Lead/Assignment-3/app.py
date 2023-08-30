from flask import *
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=v815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30367;SECURITY=SSL;UID=vjf17320;PWD=gHq50AUEWED31DdN",'','')
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
            return render_template('login.html',pred=f'Login Successful {USEREMAIL}')
        else:
            return render_template('login.html',pred="Check your Username and Password")
    else:
        return render_template('login.html',pred="No account found,Please register")
    
@app.route('/signout',methods=['GET','POST'])
def signout():
    if request.method=='GET':
        USEREMAIL=request.args.get('email')
    else:
        USEREMAIL=request.form.value('email')
    sql="DELETE FROM LOGIN WHERE EMAIL=?"
    prep_stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(prep_stmt,1,USEREMAIL)
    ibm_db.execute(prep_stmt)
    return render_template('login.html',pred="Signed Out")

@app.route('/login1')
def login1():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')


if __name__=="__main__":
    app.run(debug=True,port=8080,host='0.0.0.0')
