
from flask import Flask,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pandas as pd
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/gocart'
db = SQLAlchemy(app)
app.secret_key = 'super-secret-key'
@app.route("/" )
def home():
    admin=db.engine.execute('select fname from customer where c_id=1')
    admin=[_[0] for _ in admin][0]
    return render_template("home.html",admin=admin)
@app.route("/login.html")
def home_():
    return render_template("login.html",id=None)

@app.route("/signup.html")
def sign():
    return render_template("signup.html")

class Customer(db.Model):
    #fname,mname,lname,dob,sex,phone,email,address1,addres2,postal_code,password
    c_id=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(10),nullable=False)
    mname=db.Column(db.String(10), nullable=True)
    lname=db.Column(db.String(10), nullable=True)
    dob=db.Column(db.Date, nullable=True)
    sex=db.Column(db.String(10), nullable=False)
    phone=db.Column(db.String(10), nullable=False)
    is_seller=db.Column(db.String(3), nullable= False)
    email=db.Column(db.String(10),nullable=False)
    address1=db.Column(db.String(100), nullable=False)
    address2=db.Column(db.String(100), nullable=True)
    postal_code=db.Column(db.String(10), nullable=False)
    password=db.Column(db.String(20),nullable=False)

class Product(db.Model):
    #brand,category,depart,price,name,seasson_to_wear, type,description,image,item_avl
    p_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(10),nullable=False)
    brand=db.Column(db.String(10), nullable=False)
    category=db.Column(db.String(10), nullable=False)
    depart=db.Column(db.Date, nullable=False)
    price=db.Column(db.Integer, nullable=False)
    seasson_to_wear=db.Column(db.String(10), nullable=False)
    type=db.Column(db.String(10), nullable= False)
    description=db.Column(db.String(100),nullable=False)
    image=db.Column(db.String(30), nullable=False)
    item_avl=db.Column(db.Integer, nullable=True)

class Orders(db.Model):
    c_id=db.Column(db.Integer,nullable=False,primary_key=True)
    p_id = db.Column(db.Integer, nullable=False,primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
#name = db.engine.execute( 'select fname,lname from customer')
#[print(_) for _ in name] # It returns tupple of all the selected attributes

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        f=request.form.get("fnm")
        m = request.form.get("mnm")
        l = request.form.get("lnm")
        s=request.form.get("gender")
        d = request.form.get("dob")
        p = request.form.get("phone")
        t = request.form.get("type")
        e = request.form.get("email")
        a1 = request.form.get("addrl1")
        a2 = request.form.get("addrl2")
        pc = request.form.get("pc")
        pw = request.form.get("pass")
        #print(s,f,p,e,a1,pc,pw)
        if t == "seller":
            t = "Yes"
        else:
            t = "No"
        if(f and p and e and a1 and pc and pw):
            emails=[_[0] for _ in db.engine.execute('select email from customer')]
            if e not in emails:

                entry=Customer(fname=f,mname=m,lname=l,sex=s,dob=d,phone=p,is_seller=t,email=e,address1=a1,address2=a2,postal_code=pc,password=pw)
                db.session.add(entry)
                db.session.commit()

                return render_template("login.html")
            return render_template("login.html", msg="user already registred")
    return render_template("signup.html")

@app.route("/login" ,methods=["GET","POST"])
def login():
    if request.method=="POST":
        e=request.form.get("email")
        p=request.form.get("pass")
        emails=[_[0] for _ in db.engine.execute('select email from customer')]
        if e in emails:
            if p==[_[0] for _ in db.engine.execute('select password from customer where email="{}"'.format(e))][0]:
                session['user']=[_[0] for _ in db.engine.execute('select c_id from customer where email="{}"'.format(e))][0]
                return redirect(url_for("welcome"))
            return render_template("login.html",notif="password is incorrect")
    return render_template("login.html",notif="user not found")

@app.route("/welcome" ,methods=["GET","POST"])
def welcome():
    c_id=session["user"]
    username= [_[0] for _ in db.engine.execute('select fname from customer where c_id={}'.format(c_id))][0]
    is_seller = [_[0] for _ in db.engine.execute('select is_seller from customer where c_id={}'.format(c_id))][0]
    user = dict(zip(["c_id", 'name', 'is_seller'], (c_id, username, is_seller)))
    products = [_[0] for _ in db.engine.execute('select name from product')]
    p_id = [_[0] for _ in db.engine.execute('select p_id from product')]
    prices = [_[0] for _ in db.engine.execute('select price from product')]
    images = [_[0] for _ in db.engine.execute('select image from product')]

    product = zip(p_id, products, prices, images)
    return render_template("welcome.html", user=user, product=product)

@app.route("/orders" ,methods=["POST"])
def orders():
        c_id=session['user']
        o=db.engine.execute('select name from orders natural join product where c_id="{}"'.format(c_id))
        q=db.engine.execute('select quantity from orders where c_id="{}"'.format(c_id))
        o=[_[0] for _ in o]
        q = [_[0] for _ in q]
        o=zip(range(1,len(o)+1),o,q)
        return render_template('orders.html',orders=o)

#brand,category,depart,price,name,seasson_to_wear, type,description,image,item_avl
@app.route("/addproduct" ,methods=['GET','POST'])
def add():
    if request.method=="POST":
        b=request.form.get("brand")
        c=request.form.get("cat")
        d=request.form.get("depart")
        p=request.form.get("price")
        n=request.form.get("name")
        s=request.form.get("seasson")
        t=request.form.get("type")
        des=request.form.get("description")
        i=request.form.get("item_avl")

        im=[_[0] for _ in db.engine.execute('select p_id from product order by p_id DESC limit 1')][0]
        im=str(im+1)+".png"
        if(b and c and d and p and n and s and t and des and i):
            entry=Product(brand=b,category=c,depart=d,price=p,name=n,seasson_to_wear=s, type=t,description=des,image=im,item_avl=i)
            db.session.add(entry)
            db.session.commit()
            return "added successfully"
        return render_template("add.html")
    return None

@app.route("/buy",methods=["GET","POST"])
def buy():
    if request.method=="POST":
        c_id=session['user'];
        p_id=request.form.get("item")
        q=db.engine.execute('select quantity from orders where c_id={} and p_id={}'.format(c_id,p_id))
        flag=0
        try:
            q=[_[0] for _ in q][0]
            flag=1
        except:
            q=0
        if flag==0:
            entry=Orders(c_id=c_id,p_id=p_id,quantity=q+1)
            db.session.add(entry)
            db.session.commit()
        else:
            db.engine.execute('update orders set quantity={} where p_id={} and c_id={}'.format(q+1,p_id,c_id))
        item_avl=[_[0] for _ in db.engine.execute('select item_avl from product where p_id={}'.format(p_id))][0]
        db.engine.execute('update product set item_avl={} where p_id={}'.format(item_avl-1,p_id))
        return redirect(url_for("welcome"))
    return "error"

@app.route("/logout",methods=["GET",'POST'])
def logout():
    if request.method=="POST":
        session.pop('user')
        return render_template("login.html")
    return None
app.run(debug=True)