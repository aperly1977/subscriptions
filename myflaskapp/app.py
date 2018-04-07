from flask import Flask, render_template,flash,redirect,url_for,session,request,jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField ,validators ,RadioField
import geoip2.database


app = Flask(__name__)

#confog MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_DB'] = 'hs'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

class subscriptionForm(Form):
    email = StringField('Email',[validators.DataRequired(),validators.Email()])
    firstName = StringField('First Nname',[validators.Length(min=5,max=50)])
    lastName = StringField('Last Name',[validators.Length(min=5,max=50) ])
    action = RadioField('Label', choices=[('start','start'),('end','end')])

@app.route('/subscription',methods=['GET','POST'])

def subscription():
    form = subscriptionForm(request.form)
    if request.method == 'POST' and form.validate():

        email = form.email.data
        firstName = form.firstName.data
        lastName = form.lastName.data
        action = form.action.data
        # get IP
        ip =request.environ['REMOTE_ADDR']


        reader = geoip2.database.Reader('GeoLite2-Country.mmdb')

        try:
            response = reader.country(ip)
            country = response.country.iso_code
        except Exception as e:
            country='N/A'


        reader = geoip2.database.Reader('GeoLite2-City.mmdb')

        try:
            response = reader.city(ip)
            city = response.city.iso_code
        except Exception as e:
            city ="N/A"


        #execute query
        cur.execute("""insert into subscriptions(email,first_name,last_name,action,ip,country)
        values (%s,%s,%s,%s,%s,%s)""",(email,firstName,lastName,action,ip,country))

        mysql.connection.commit()

        #close connection
        cur.close()

        flash("subscribe successfully ",'success')

        return redirect(url_for('index'))

    return render_template('subscription.html',form=form)

@app.route('/report')

def report():

    cur = mysql.connection.cursor()
    #get Report
    result = cur.execute("""
    select s.email ,s.reuqest_time as start_dubscription_date, s.action  , e.action , e.reuqest_time as end_dubscription_date
    from subscriptions s
    left join subscriptions e on s.email = e.email and e.action='end'
    where  s.action='start'
    and CURRENT_TIMESTAMP() between s.reuqest_time and IFNULL(date(e.reuqest_time) , CURRENT_TIMESTAMP())
    """)

    report= cur.fetchall()
    print result
    if result > 0:
        return render_template('report.html',report=report, result=result)
    else:
        msg = "No Active Subscription"
        return render_template('report.html',msg=msg)

    cur.close()

if __name__ == '__main__':
    app.secret_key = 'development'
    app.run(debug=True)
