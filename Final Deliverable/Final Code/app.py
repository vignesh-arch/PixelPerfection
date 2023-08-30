from flask import *
import os
import base64
import requests
import ibm_boto3
import replicate
from ibm_botocore.client import Config,ClientError
import ibm_db
import re
import requests

app = Flask(__name__)


MODE='demo' 
RAPIDAPI_KEY="3801acee72msh26906931aee075dp1640aejsn78b541076ce0" #rapid api key

OPTIONS = {
    'demo': {
        'url': 'https://demo.api4ai.cloud/img-bg-removal/v1/results',
        'headers': {'A4A-CLIENT-APP-ID': 'sample'}
    },
    'rapidapi': {
        'url': 'https://background-removal4.p.rapidapi.com/v1/results',
        'headers': {'X-RapidAPI-Key': RAPIDAPI_KEY}
    }
}

COS_END_POINT="https://s3.us-south.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID="Zilfo9px58o1ZpUqzICdwhwF6mV4ZbxKM86QAMUdVuUD"
COS_RES_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/0c99b2c2ed6a41919b9d8b8ff36c9f3d:c56177ab-c237-4a12-9e31-913e74e58dc6::"

os.environ["REPLICATE_API_TOKEN"] = "r8_34nlmqzjOaNREnC4InS3jiwnlnvc13b2ci5Rd" #replicate api key

#ibm cloud object storage connection
cos=ibm_boto3.client("s3",ibm_api_key_id=COS_API_KEY_ID,ibm_service_instance_id=COS_RES_CRN,config=Config(signature_version="oauth"),endpoint_url=COS_END_POINT)
conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=8e359033-a1c9-4643-82ef-8ac06f5107eb.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30120;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xhh29229;PWD=UGnlTT78369pGWHy",'','')
print("Connection Successful",conn)

app.secret_key="vignesh"
global user



        

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/upscale_ui')
def upscale_ui():
    return render_template('upscale.html')

@app.route('/cartoon')
def cartoon():
    return render_template('cartoon.html')

@app.route('/beauty')
def beauty():
    return render_template('beauty.html')

@app.route('/vehrm')
def vehrm():
    return render_template('vehicleremove.html')

def getImageLink():     #To store image from form to local storage and get cos link from it 
    f=request.files['image']
    basepath=os.path.dirname(__file__)
    filepath=os.path.join(basepath,'uploads',f.filename)
    f.save(filepath)
    cos.upload_file(Filename=filepath,Bucket='vignesh-arch',Key=f.filename)
    link="https://vignesh-arch.s3.us-south.cloud-object-storage.appdomain.cloud/"+f.filename
    return link,f.filename

def uploadAndClean(*img):     #method to store the output img to cos and to clean the previously stored(unused images) from local storage and cos
    key_name=key_name=img[0].replace(".","")+img[1]+"_out.jpg"
    cos.upload_file(Filename=img[0],Bucket='vignesh-arch',Key=key_name)
    url="https://vignesh-arch.s3.us-south.cloud-object-storage.appdomain.cloud/"+key_name
    storeHistory(url,img[1])
    basepath=os.path.dirname(__file__)
    os.remove(img[0])
    os.remove("/"+basepath+"/uploads/"+img[0])
    try:
        cos.delete_object(Bucket="vignesh-arch", Key=img[0])
        print("Item: {filename} deleted!\n".format(img[0]))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete object: {0}".format(e))
    return url

def storeHistory(*img):  #To store the image url's in the ibm db2
    sql="INSERT INTO IMAGE_URL(USERD,"+img[1]+") VALUES(?,?)"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['USERD'])
    ibm_db.bind_param(stmt,2,img[0])
    ibm_db.execute(stmt)

def getHistory():   #To get the stored image url's from the ibm db2
    sql="SELECT * FROM IMAGE_URL WHERE USERD=?"
    stmt=ibm_db.prepare(conn,sql)
    try:
        ibm_db.bind_param(stmt,1,session['USERD'])
        ibm_db.execute(stmt)
        rmbg=[]
        carbg=[]
        upscale=[]
        boxcut=[]
        while True:
            data=ibm_db.fetch_assoc(stmt)
            if not data:
                break
            else:
                if data['REMOVEBG']!= None:
                    rmbg.append(data['REMOVEBG'])
                if data['CARBG']!= None:
                    carbg.append(data['CARBG'])
                if data['BOWLCUT']!= None:
                    boxcut.append(data['BOWLCUT'])
                if data['UPSCALE']!= None:
                    upscale.append(data['UPSCALE'])
        print(rmbg,carbg,upscale,boxcut)
        return rmbg,carbg,upscale,boxcut
    except KeyError:
        return render_template('login.html')


#user login
@app.route('/login_user',methods=['POST','GET'])
def login_user():
    msg='None'
    if request.method=="POST":
        Email=request.form['EMAIL']
        Password=request.form['PASSWORD']
        sql="SELECT * FROM USER1 WHERE EMAIL=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,Email)
        ibm_db.bind_param(stmt,2,Password)
        ibm_db.execute(stmt)
        acc=ibm_db.fetch_assoc(stmt)
        if acc:
            session['Loggedin']=True
            session['USERD']=acc['USERD']
            session['NAME']=acc['NAME']
            msg="logged"
            return render_template('home.html',log=msg)
        else:
            msg="Please check your Username and Password"
            return render_template('register.html',msg=msg)
    return render_template('login.html',msg=msg)

"""User can register"""
@app.route('/register_user',methods=['POST','GET'])
def register_user():
    msg='None'
    if request.method=='POST':
        Name=request.form['NAME']
        Email=request.form['EMAIL']
        Password=request.form['PASSWORD']
        sql="SELECT * FROM USER1 WHERE EMAIL=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,Email)
        ibm_db.bind_param(stmt,2,Password)
        ibm_db.execute(stmt)
        acc=ibm_db.fetch_assoc(stmt)
        if acc:
            msg="You are already registered.Please Login using using your credientials"
            return render_template('login.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',Email):
            msg="Please type valid Email"
        else:
            sql="SELECT COUNT(*) FROM USER1"
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.execute(stmt)
            count=ibm_db.fetch_assoc(stmt)
            print(count)
            sql1="INSERT INTO USER1 VALUES(?,?,?,?)"
            stmt1=ibm_db.prepare(conn,sql1)
            ibm_db.bind_param(stmt1,1,Name)
            ibm_db.bind_param(stmt1,2,Email)
            ibm_db.bind_param(stmt1,3,Password)
            ibm_db.bind_param(stmt1,4,count['1']+1)
            ibm_db.execute(stmt1)
            msg="Successfully Registered"
            return render_template('login.html',msg=msg)
    return render_template('register.html',msg=msg)

#user logout
@app.route('/logout_user')
def logout_user():
    session.pop('loggedin',None)
    session.pop('USERD',None)
    return render_template('home.html')

@app.route('/myimg')
def myimg():
    try:
        rmbg,carbg,upscale,boxcut=getHistory()
    except ValueError:
        return render_template('login.html')
    return render_template('my_images.html',rmbg=rmbg,carbg=carbg,upscale=upscale,boxcut=boxcut)

@app.route('/upscale',methods=['POST','GET'])
def upscale():
    if request.method=='POST':
        url,filename=getImageLink()
        output = replicate.run(
            "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3",
            input={"img":url}
        )
        data=requests.get(output).content
        file=open(filename,"wb")
        file.write(data)
        file.close()
        link=uploadAndClean(filename,"UPSCALE")
        print(link)
    return render_template("upscale.html",link=link)

@app.route('/rmbg',methods=['POST','GET'])
def rmbg():
    link="None"
    if request.method=='POST':
        url,filename=getImageLink()
        response = requests.post(
            OPTIONS[MODE]['url'],
            headers=OPTIONS[MODE]['headers'],
            data={'url': url})
        img_b64 = response.json()['results'][0]['entities'][0]['image'].encode('utf8')
        path_to_image = os.path.join(filename)
        with open(path_to_image, 'wb') as img:
            img.write(base64.decodebytes(img_b64))
        link=uploadAndClean(path_to_image,"REMOVEBG")
    return render_template('removebg.html',link=link)

@app.route('/rmvehicle',methods=['POST','GET'])
def rmvehicle():
    link="None"
    if request.method=='POST':
        url,filename=getImageLink()
        response = requests.post(
            OPTIONS[MODE]['url'],
            headers=OPTIONS[MODE]['headers'],
            data={'url': url})
        img_b64 = response.json()['results'][0]['entities'][0]['image'].encode('utf8')
        path_to_image = os.path.join(filename)
        with open(path_to_image, 'wb') as img:
            img.write(base64.decodebytes(img_b64))
        link=uploadAndClean(path_to_image,"CARBG")
    return render_template('vehicleremove.html',link=link)

@app.route('/cart',methods=['POST','GET'])
def cart():
    if request.method=='POST':
        url,filename=getImageLink()
        output = replicate.run(
            "orpatashnik/styleclip:7af9a66f36f97fee2fece7dcc927551a951f0022cbdd23747b9212f23fc17021",
            input={"input":url}
        )
        data=requests.get(output).content
        file=open(filename,"wb")
        file.write(data)
        file.close()
        link=uploadAndClean(filename,"BOWLCUT")
        print(link)
    return render_template("upscale.html",link=output)






if __name__=="__main__":
    app.run(debug=True,port=5000,host='0.0.0.0')