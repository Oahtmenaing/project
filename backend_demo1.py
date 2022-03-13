import string
import random
import re

from  flask import Flask,send_from_directory,render_template, session, request, flash, redirect, url_for
import flask_wtf
from flask_wtf import FlaskForm
import config
from wtforms import StringField, PasswordField,FloatField, SubmitField, IntegerField, DateField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from werkzeug.routing import BaseConverter
from flask_sqlalchemy import SQLAlchemy
import hashlib


# configration
app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/static')
app.config.from_object(config)
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = "12345678"

# 绝对路径


# Define the common used class
class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True,unique = True,) # 商品id
    name = db.Column(db.String(200), nullable=False,) # 商品名称
    unit_price = db.Column(db.Float(10), nullable=False) # 商品单价
    number = db.Column(db.Integer,nullable=False) # 商品库存
    description = db.Column(db.String(2000))# 商品描述
    image = db.Column(db.String(2000)) # 图片信息

class AddForm(FlaskForm):
    id = IntegerField(label=u"产品编号唯一", validators=[DataRequired(u'供应商编号必填')])
    name = StringField(label=u"产品名称", validators=[DataRequired(u'供货商必填')])
    unit_price = FloatField(label=u"单价", validators=[DataRequired(u"价格必填")])
    number = IntegerField(label=u"库存", validators=[DataRequired(u"数量必填")])
    description = StringField(label=u"产品描述",validators=[DataRequired()])
    image = StringField(label=u"产品图片名",validators=[DataRequired()])
    submit = SubmitField(label=u'保存数据',)

class DeleteForm(FlaskForm):
    id = IntegerField(label=u"产品编号唯一", validators=[DataRequired(u'供应商编号必填')])
    submit = SubmitField(label=u'保存数据',)

# class ImageConverter(BaseConverter):
#     def __init__(self,url,regex):
#         super

@app.route('/Image/<filename>')
def upload_images(filename):

    return {{ url_for('static',filename='images/'+filename) }}
    # return send_from_directory(cur_dir)

# 初始界面
@app.route('/')
def index():
    return render_template('index.html')

# 初始界面
@app.route('/back/')
def back():
    return render_template('index.html')


@app.route('/information/')  # 商品信息视图
def information():
    products = Products().query.all()

    return render_template('information.html', products = products)

# @app.route('/index/', methods=['GET', 'POST'])
# def index():
#     return render_template('index.html', username='rpc')
# 路由信息



# 展示信息
@app.route('/show/', methods=['GET', 'POST'])
def show():
    product_list = Products.query.filter_by().all()
    print(product_list)
    # file_path = os.path.join('../Image/', file_name)
    return render_template('show.html', products=product_list)

@app.route('/add/', methods=["GET", "POST"])
def add():
    form = AddForm()
    if request.method == "POST":
        '''表单验证'''
        # 提取表单数据
        id = form.id.data
        name = form.name.data
        unit_price = form.unit_price.data

        number = form.number.data
        description = form.description.data
        image = form.image.data

        # 保存数据库
        product = Products(id=id,name=name,unit_price=unit_price,number=number,description=description,image=image)
        print(product)
        db.session.add(product)
        db.session.commit()
        form.required = True
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/delete/', methods=["GET", "POST"])
def delete():
    form = DeleteForm()
    if request.method == "POST":
        '''表单验证'''
        # 提取表单数据
        id = form.id.data

        product = Products.query.filter_by(id=id).first()
        print(product)

        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('delete.html', form=form)


@app.route('/modify/', methods=["GET", "POST"])
def modify():
    form = AddForm()
    if form.validate_on_submit():
        print('change')
        '''表单验证'''
        # 提取表单数据
        id = form.id.data
        name = form.name.data
        unit_price = form.unit_price.data

        number = form.number.data
        description = form.description.data
        image = form.image.data
        print('change')
        # 保存数据库
        # product = Products(id=id,name=name,unit_price=unit_price,number=number,description=description,image=image)


        change_product = db.session.query(Products).filter(Products.id.like(id)).first()

        print(change_product)
        change_product.name = name
        change_product.unit_price = unit_price
        change_product.number = number
        change_product.description = description
        change_product.image = image
        db.session.commit()
        form.required= True
        return redirect(url_for('index'))
    return render_template('modify.html', form=form)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), nullable=False)
    mobile = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    salt = db.Column(db.String(4), nullable=False)


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    salt = db.Column(db.String(4), nullable=False)


class LoginForm(FlaskForm):
    username = StringField(label="username", validators=[DataRequired("Username is required")])
    password = PasswordField(label="password", validators=[DataRequired("password is required")])
    submit = SubmitField("Login")
    loginType = -1
    userType = 0

    def validate_username(self, field):
        # Email
        if re.match(r'(.*)@', field.data):
            self.loginType = 0
            if not User.query.filter_by(email=field.data).first():
                raise ValidationError('The username does not exist')
        # Mobile
        elif not re.match(r'(.*)[^0-9]', field.data):
            self.loginType = 1
            if not User.query.filter_by(mobile=field.data).first():
                raise ValidationError('The username does not exist')
        # Username
        else:
            self.loginType = 2
            if not User.query.filter_by(username=field.data).first():
                self.userType = 1
                if not Admin.query.filter_by(username=field.data).first():
                    raise ValidationError('The username does not exist')


class RegisterForm(FlaskForm):
    username = StringField("username", validators=[DataRequired("Username is required")])
    password = PasswordField("password", validators=[DataRequired("Password is required")])
    password_check = PasswordField("password_check"
                                   , validators=[DataRequired("Password_check is required")
            , EqualTo("password", "The checking Password is different from the Password")])
    mobile = StringField("mobile", validators=[DataRequired("Mobile number is required")])
    email = StringField("email", validators=[DataRequired("Email address is required")])
    submit = SubmitField(label='register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The Username is occupied')
        elif Admin.query.filter_by(username=field.data).first():
            raise ValidationError('The Username is occupied')
        if re.match(r'(.*)@', field.data) or not re.match(r'(.*)[^0-9]', field.data):
            raise ValidationError('The Username must not be only including digit and without @')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The email is occupied')

    def validate_mobile(self, field):
        if User.query.filter_by(mobile=field.data).first():
            raise ValidationError('The mobile is occupied')


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'


@app.route('/user/<username>', methods=["GET", "POST"])
def profile(username):
    if request.method == "GET":
        return "POST"
    if request.method == "POST":
        return f'{username}\'s profile'


@app.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("Login Type: " + str(form.loginType))
        print("User Type: " + str(form.userType))
        if form.loginType == 0:
            user = User.query.filter_by(email=form.username.data).first()
        elif form.loginType == 1:
            user = User.query.filter_by(mobile=form.username.data).first()
        elif form.userType == 0:
            user = User.query.filter_by(username=form.username.data).first()
        else:
            user = Admin.query.filter_by(username=form.username.data).first()
        if user:
            username = user.username
            print("username: " + username)
            password = user.password
            print("password: " + password)
            m = hashlib.md5()
            salt = user.salt
            m.update((form.password.data + salt).encode("utf-8"))
            input_password = m.hexdigest()
            print("input Password: " + input_password)
            if input_password == password:
                print("login successfully")
                if form.userType == 0:
                    print("UserType: User")
                else:
                    print("UserType: Admin")
                session["username"] = username
                session["user_type"] = form.userType
            else:
                print("Password incorrect")
                form.password.errors.append("The password is incorrect")
                return render_template('login.html', form=form)
        print(form.username.data)
        return redirect(url_for("index"))
    return render_template('login.html', form=form)


@app.route('/register/', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        mobile = form.mobile.data
        email = form.email.data
        password = form.password.data
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        password_check = form.password_check.data
        m = hashlib.md5()
        m.update((password + salt).encode("utf-8"))
        password = m.hexdigest()
        user = User(username=username, mobile=mobile, email=email, password=password, salt=salt)
        db.session.add(user)
        db.session.commit()
        print(username, password, mobile, email, salt)
        session['username'] = username
        return redirect(url_for("index"))
    return render_template('register.html', form=form)


with app.test_request_context('/hello', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/hello'
    assert request.method == 'POST'


if __name__ == '__main__':
    #清除所有表
    db.drop_all()
    #创建表
    db.create_all()
    # 创建对象插入数据
    Product1 = Products(id=1,name='茄子',unit_price=13.5,number=15,image = 'eggplant.png',description ='vegetables')
    # session 记录到对象任务中
    db.session.add(Product1)
    # 提交任务
    db.session.commit()
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8000
    )
