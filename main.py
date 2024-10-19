from flask import Flask,render_template,request,redirect,flash
import pymysql as ps
import datetime

try:
    con=ps.connect(host="localhost",user="root",password="h13143m17",database="Hospital",cursorclass=ps.cursors.DictCursor)
    cursor=con.cursor()
except:
    print("Error")

yesterday = datetime.date.today()-datetime.timedelta(days=1)
#2024-10-18 = yesterday
yest = str(yesterday)[8:]+'-'+str(yesterday)[5:7]+'-'+str(yesterday)[:4] #18-10-2024

try:
    cursor.execute(f"delete from Appointments where apDate = '{yest}'")
    con.commit()
    print("Deleted")
except:
    print("Error")

LOGINEMAIL=''
ptid = 0
warning ="rgb(255, 80, 80)"
alert="rgb(255, 162, 48)"
success="rgb(111, 255, 85)"
today = datetime.date.today()
 
now = str(today)[8:]+'-'+str(today)[5:7]+'-'+str(today)[:4]

app=Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

# -------------------------------------------------------------PATIENT PAGE ROUTING SETUPS-------------------------------------------------------------------

@app.route('/phome')
def phome():
    global ptid
    datas = {}
    sessions = []
    try:
        cursor.execute(f"select * from Patient where ptEmail='{LOGINEMAIL}'")
        datas = cursor.fetchone()
        ptid = datas['ptId']
        cursor.execute(f"select * from Appointments where ptId = {ptid} and apDate = '{now}'")
        sessions = cursor.fetchall()
    except:
        flash("Error 404",warning)
    return render_template("Phome.html",info = datas,infos = sessions,currentdate = now)

@app.route('/palldoctors')
@app.route('/palldoctors/<int:id>',methods=['POST','GET'])
def palldoctors(id=None):
    if request.method == 'POST':
        print(id)
        FAVSTATUS = request.form['FAVSTATUS']
        if FAVSTATUS == None:
            pass
        else:
            try:
                cursor.execute(f"select drId from Pfav where ptId={ptid}")
                favdatas = cursor.fetchall()
                listoffavdatas = []
                for i in favdatas:
                    listoffavdatas.append(i['drId'])
                if FAVSTATUS == 'yes' and id not in listoffavdatas:
                    try:
                        cursor.execute(f"insert into Pfav (drId,ptId) values ({id},{ptid})")
                        con.commit()
                    except:
                        flash("error to add fav",alert)
                else:
                    if id in listoffavdatas:
                        try:
                            cursor.execute(f"delete from Pfav where ptId={ptid} and drId={id}")
                            con.commit()
                        except:
                            flash("error to add fav",alert)
            except Exception as e:
                print(e)
                flash("Somthing error",alert)
    datas = []
    try:
        cursor.execute("select * from Doctor")
        datas = cursor.fetchall()
    except:
        flash("Something went wrong in Server",warning)
        return redirect('/phome')
    return render_template("Palldoctors.html", infos = datas)

@app.route('/pmydoctor')
def pmydoctor():
    datas = []
    try:
        cursor.execute(f"select * from Doctor where drId in (select drId from Pfav where ptId = {ptid})")
        datas = cursor.fetchall()
    except:
        flash ("Somthing Error in Server",alert)

    return render_template("Pmydoctor.html",infos = datas)

@app.route('/pmysessions')
def pmysessions():
    datas = []
    try:
        cursor.execute(f"select * from Appointments where ptId = {ptid}")
        datas = cursor.fetchall()
        for i in datas:
            cursor.execute(f"select drName from Doctor where drId={i['drId']}")
            i['drName'] = cursor.fetchone()['drName']
    except:
        flash("Server Error",alert)
    return render_template("Pmysessions.html",infos = datas)

@app.route('/pprofile')
def pprofile():
    datas = {}
    try:
        cursor.execute(f"select * from Patient where ptEmail='{LOGINEMAIL}'")
        datas = cursor.fetchone()
    except:
        flash("Error 404",warning)
    return render_template("Pprofile.html",info = datas)

@app.route('/viewDprofile/<int:id>',methods=['POST','GET'])
def viewDprofile(id):
    dats = []
    try:
        cursor.execute(f"select * from Doctor where drId={id}")
        dats=cursor.fetchone()
    except:
        flash("Error",alert)
    return render_template("viewDprofile.html",info = dats)

@app.route('/pbooking/<int:id>',methods=['POST','GET'])
@app.route('/pbooking',methods=['POST','GET'])
def pbooking(id = None):
    datas = []
    try:
        cursor.execute(f"select apDate,apTime from Appointments where drId = {id} and ptId is null")
        datas = cursor.fetchall()
    except:
        flash("Some Error",alert)
    if request.method =='POST':
        datas = []
        DAY  = request.form['DAY']
        try:
            cursor.execute(f"select apDate,apTime from Appointments where drId = {id} and apDay = '{DAY}' and ptId is null")
            datas = cursor.fetchall()
        except:
            flash("Some Error",alert)
    
    return render_template('Pbooking.html',infos = datas,drid = id)

@app.route('/pbooking_app/<int:id>/<string:date>/<string:time>',methods=['POST','GET'])
def pbooking_app(id=None,date=None,time=None):
    if request.method == 'POST':
        Session_Title = request.form['Session_Title']
        try:
            cursor.execute(f"update Appointments set ptId = {ptid},apTitle='{Session_Title}' where drId = {id} and apDate='{date}' and apTime='{time}'")
            con.commit()
            flash("Appointment booked successfully",success)
        except:
            flash("Booking Failed",alert)
    return redirect('/pmysessions')

@app.route('/delete_app/<int:id>/<string:date>/<string:time>/<int:flag>')
def delete_app(id=None,date=None,time=None,flag=None):
    try:
        cursor.execute(f"update Appointments set ptId = null,apTitle = null where drId = {id} and apDate='{date}' and apTime='{time}'")
        con.commit()
        flash("Appointment Deleted successfully",success)
    except:
        flash("Deletion Failed",alert)
    if flag==0:
        return redirect('/pmysessions')
    else:
        return redirect('/dmysessions')

@app.route('/search_app_by_date',methods=['POST','GET'])
def search_app_by_date():
    if request.method == 'POST':
        DATE = request.form['DATE']
        DATE = DATE[8:]+'-'+DATE[5:7]+'-'+DATE[:4]
        datas = []
        try:
            cursor.execute(f"select * from Appointments where ptId = {ptid} and apDate = '{DATE}'")
            datas = cursor.fetchall()
            for i in datas:
                cursor.execute(f"select drName from Doctor where drId={i['drId']}")
                i['drName'] = cursor.fetchone()['drName']
        except:
            flash("Server Error",alert)
    return render_template("Pmysessions.html",infos = datas)

@app.route('/search_all_doctors',methods=['POST','GET'])
def search_all_doctors():
    datas = []
    if request.method == 'POST':
        FILTER = request.form['FILTER']
        VALUE = request.form['VALUE']
        print(FILTER)
        if FILTER == "name":
            try:
                cursor.execute(f"select * from Doctor where drName = '{VALUE}'")
                datas = cursor.fetchall()
            except:
                flash("Data not found",warning)
        elif FILTER == "city":
            try:
                cursor.execute(f"select * from Doctor where drHospitalCity = '{VALUE}'")
                datas = cursor.fetchall()
            except:
                flash("Data not found",warning)
        else:
            try:
                cursor.execute(f"select * from Doctor where drSpecialist = '{VALUE}'")
                datas = cursor.fetchall()
            except:
                flash("Data not found",warning)
    return render_template("Palldoctors.html", infos = datas)

@app.route('/search_all_doctors_fav',methods=['POST','GET'])
def search_all_doctors_fav():
    datas = []
    if request.method == 'POST':
        FILTER = request.form['FILTER']
        VALUE = request.form['VALUE']
        print(FILTER)
        if FILTER == "name":
            try:
                cursor.execute(f"select * from Doctor where drName = '{VALUE}' and drId in (select drId from Pfav where ptId = {ptid})")
                datas = cursor.fetchall()
            except:
                flash("Data not found",warning)
        elif FILTER == "city":
            try:
                cursor.execute(f"select * from Doctor where drHospitalCity = '{VALUE}' and drId in (select drId from Pfav where ptId = {ptid})")
                datas = cursor.fetchall()
            except:
                flash("Data not found",warning)
        else:
            try:
                cursor.execute(f"select * from Doctor where drSpecialist = '{VALUE}' and drId in (select drId from Pfav where ptId = {ptid})")
                datas = cursor.fetchall()
            except:
                flash("Data not found",warning)
    return render_template("Pmydoctor.html", infos = datas)
# -------------------------------------------------------------DOCTOR PAGE ROUTING SETUPS-------------------------------------------------------------------

@app.route('/dhome')
def dhome():
    global ptid
    datas = {}
    sessions =[]
    try:
        cursor.execute(f"select drId,drName,drGender from Doctor where drEmail='{LOGINEMAIL}'")
        datas = cursor.fetchone()
        ptid = datas['drId']
        cursor.execute(f"select * from Appointments where drId = {ptid} and apDate = '{now}'")
        sessions = cursor.fetchall()
    except:
        flash("Error 404",warning)
    return render_template("Dhome.html",info = datas,currentdate = now,infos = sessions)

@app.route('/dmyappointments',methods=['POST','GET'])
def dmyappointments():
    datas = {}
    datas_booked = {}
    try:
        cursor.execute(f"select apDay,count(*) as total from Appointments where drId = {ptid} group by apDay")
        for i in cursor.fetchall():
            datas[i['apDay']] = i['total']
        cursor.execute(f"select apDay,count(*) as total from Appointments where drId = {ptid} and ptId is not null group by apDay")
        for i in cursor.fetchall():
            booked = i['total']-datas[i['apDay']]
            datas_booked[i['apDay']] = booked if ( booked >=0) else booked * -1
    except:
        flash("Error in server",alert)
    return render_template("Dmyappointments.html",info = datas,currentdate = now, infos =datas_booked)

@app.route('/dmysessions')
def dmysessions():
    datas = []
    try:
        cursor.execute(f"select * from Appointments where drId = {ptid} and ptId is not null")
        datas = cursor.fetchall()
        for i in datas:
            cursor.execute(f"select ptName from Patient where ptId={i['ptId']}")
            i['ptName'] = cursor.fetchone()['ptName']
    except:
        flash("Server Error",alert)
    return render_template("Dmysessions.html",infos = datas)

@app.route('/dprofile')
def dprofile():
    datas = {}
    try:
        cursor.execute(f"select * from Doctor where drEmail='{LOGINEMAIL}'")
        datas = cursor.fetchone()
    except:
        flash("Error 404",warning)
    return render_template("Dprofile.html",info = datas)

@app.route('/dmyappointments_addtimesteup',methods=['POST','GET'])
def dmyappointments_addtimesteup():
    if request.method == 'POST':
        SCHEDULE = request.form['SCHEDULE']
        APPOINTMENTTIME = request.form['APPOINTMENTTIME']
        if int(APPOINTMENTTIME[:2])>12:
            APPOINTMENTTIME = str(int(APPOINTMENTTIME[:2])-12)+APPOINTMENTTIME[2:]+" pm"
        else:
            APPOINTMENTTIME = APPOINTMENTTIME + " am"
        day = request.form['day']
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        index = days_of_week.index(day)

        upcoming_dates = []
        current_date = today

        if SCHEDULE == 'everyday':
            while len(upcoming_dates) < 4:
                if current_date.strftime("%A") == day:
                    upcoming_dates.append(current_date.strftime('%d-%m-%Y'))
                current_date += datetime.timedelta(days=1)
        elif SCHEDULE == 'alternative':
            while len(upcoming_dates) < 2:
                if current_date.strftime("%A") == day:
                    upcoming_dates.append(current_date.strftime('%d-%m-%Y'))
                current_date += datetime.timedelta(days=1)
        else:
            if today.strftime("%A") == day:
                upcoming_dates.append(today.strftime('%d-%m-%Y'))
        try:
            for i in range(len(upcoming_dates)):
                cursor.execute(f"insert into Appointments (drId,apDate,apTime,apDay) values({ptid},'{upcoming_dates[i]}','{APPOINTMENTTIME}','{day}')")
                con.commit()
                flash("updated.",success)
        except Exception as e:
            print(e)
            flash("Somthing went wrong in Server",alert)
    return render_template("Dmyappointments_addtimesteup.html")

@app.route('/dmyappointments_timesteup/<string:day>',methods=['POST','GET'])
def dmyappointments_timesteup(day):
    datas = []
    try:
        cursor.execute(f"select * from Appointments where drId={ptid} and apDay='{day}'")
        datas = cursor.fetchall()
    except Exception as e:
        flash("Somthing went wrong in server",alert)
    return render_template("Dmyappointments_timesteup.html",infos = datas)

@app.route('/delete_appointments/<string:date>/<string:time>/<string:day>',methods=['POST','GET'])
def delete_appointments(date,time,day):
    try:
        cursor.execute(f"delete from Appointments where apDate = '{date}' and apTime = '{time}'")
        con.commit()
    except:
        flash("Unable to delete",warning)
    return redirect(f'/dmyappointments_timesteup/{day}')

@app.route('/viewPprofile/<int:id>',methods=['POST','GET'])
def viewPprofile(id):
    dats = []
    try:
        cursor.execute(f"select * from Patient where ptId={id}")
        dats=cursor.fetchone()
    except:
        flash("Error",alert)
    return render_template("viewPprofile.html",info = dats)


@app.route('/search_app_by_date_dr',methods=['POST','GET'])
def search_app_by_date_dr():
    if request.method == 'POST':
        DATE = request.form['DATE']
        DATE = DATE[8:]+'-'+DATE[5:7]+'-'+DATE[:4]
        datas = []
        try:
            cursor.execute(f"select * from Appointments where drId = {ptid} and apDate = '{DATE}' and ptId is not null")
            datas = cursor.fetchall()
            for i in datas:
                cursor.execute(f"select ptName from Patient where ptId={i['ptId']}")
                i['ptName'] = cursor.fetchone()['ptName']
        except:
            flash("Server Error",alert)
    return render_template("Dmysessions.html",infos = datas)
# ----------------------------------------------------------------LOGIN SIGNIN SETUP------------------------------------------------------------------------

@app.route('/login',methods=['POST','GET'])
def login():
    global LOGINEMAIL
    PASSWORD = request.form['USERPASSWORD']
    USEREMAIL = request.form['USERMAIL']
    try:
        cursor.execute(f"select drPassword from Doctor where drEmail='{USEREMAIL}'")
        datas = cursor.fetchone()
        if(datas != None):
            if(datas['drPassword'] == PASSWORD):
                LOGINEMAIL = USEREMAIL
                flash("Login successfully",success)
                return redirect('/dhome')
            else:
                flash("Incorrect Password",warning)
        else:
            flash("You don't have an account please signup.",alert)
        
        cursor.execute(f"select ptPassword from Patient where ptEmail='{USEREMAIL}'")
        datas = cursor.fetchone()
        if(datas != None):
            if(datas['ptPassword'] == PASSWORD):
                LOGINEMAIL = USEREMAIL
                flash("Login successfully",success)
                return redirect('/phome')
            else:
                flash("Incorrect Password",warning)
        else:
            flash("You don't have an account please signup.",alert)
        return redirect('/index')         
    except Exception as e:
        print(e)
        flash("Somting went wrong in server.",alert)
    return redirect('/index')

@app.route('/signup',methods=['POST','GET'])
def signup():
    global DATAS,LOGINEMAIL
    USERNAME = request.form['USERNAME']
    USEREMAIL = request.form['USERMAIL']
    USERROLL = request.form['USERROLL']
    USERPASSWORD = request.form['USERPASSWORD']
    CONFIRMPASSWORD = request.form['USERPASSWORDCONFIRM']
    if USERROLL == 'doctor':
        try:
            cursor.execute(f"select * from Doctor where drEmail='{USEREMAIL}'")
            datas = cursor.fetchone()
            if(datas == None):
                if(CONFIRMPASSWORD == USERPASSWORD):
                    LOGINEMAIL = USEREMAIL
                    cursor.execute(f"insert into Doctor (drName,drEmail,drPassword) values('{USERNAME}','{USEREMAIL}','{USERPASSWORD}')")
                    con.commit()
                    flash("Signup Successfully Please update your profile",success)
                    return redirect('/dhome')
                else:
                    flash("Incorrect Password",warning)
            else:
                flash("You already have an account please login.",alert)
        except:
            flash('Somting went wrong in Server',alert)
    else:
        try:
            cursor.execute(f"select * from Patient where ptEmail='{USEREMAIL}'")
            datas = cursor.fetchone()
            if(datas == None):
                if(CONFIRMPASSWORD == USERPASSWORD):
                    LOGINEMAIL = USEREMAIL
                    cursor.execute(f"insert into Patient (ptName,ptEmail,ptPassword) values('{USERNAME}','{USEREMAIL}','{USERPASSWORD}')")
                    con.commit()
                    flash("Signup Successfully Please update your profile",success)
                    return redirect('/phome')
                else:
                    flash("Incorrect Password",warning)
            else:
                flash("You already have an account please login.",alert)
        except:
            flash('Somting went wrong in Server',alert)
    return redirect('/index')

# --------------------------------------------------------------PATIEN PROFILE UPDATE--------------------------------------------------------

@app.route('/ProfileUpdatePatient',methods=['POST','GET'])
def ProfileUpdatePatient():
    if request.method == 'POST':
        NAME = request.form['NAME']
        MOBILE = request.form['MOBILE']
        if MOBILE == '':
            MOBILE=0
        else:
            MOBILE = int(MOBILE)
        GENDER = request.form['GENDER']
        EMAIL = request.form['EMAIL']
        ADDRESS = request.form['ADDRESS']
        CITY = request.form['CITY']
        PINCODE = request.form['PINCODE']
        if PINCODE == '':
            PINCODE = 0
        else:
            PINCODE = int(PINCODE)
        try:
            cursor.execute(f"update Patient set ptName='{NAME}',ptMobile={MOBILE},ptGender='{GENDER}',ptEmail='{EMAIL}',ptAddress='{ADDRESS}',ptCity='{CITY}',ptPincode={PINCODE} where ptEmail='{LOGINEMAIL}'")
            con.commit()
            flash("Profile updated Successfully.",success)
            return redirect('/pprofile')
        except Exception as e:
            print(e)
            flash("Something Wrong",alert)
            return redirect('/pprofile')
    return redirect('/pprofile')

# --------------------------------------------------------------DOCTOR PROFILE UPDATE--------------------------------------------------------

@app.route('/ProfileUpdateDoctor',methods=['POST','GET'])
def ProfileUpdateDoctor():
    if request.method == 'POST':
        NAME = request.form['NAME']
        MOBILE = request.form['MOBILE']
        if MOBILE == '':
            MOBILE=0
        else:
            MOBILE = int(MOBILE)
        GENDER = request.form['GENDER']
        EMAIL = request.form['EMAIL']
        ADDRESS = request.form['ADDRESS']
        PINCODE = request.form['PINCODE']
        if PINCODE == '':
            PINCODE = 0
        else:
            PINCODE = int(PINCODE)
        SPECIALIST = request.form['SPECIALIST']
        OWNCLINIC = request.form['OWNCLINIC']
        CLINICADDRESS = request.form['CLINICADDRESS']
        ADDRESS = request.form['ADDRESS']
        HPINCODE = request.form['HPINCODE']
        if HPINCODE == '':
            HPINCODE = 0
        else:
            HPINCODE = int(HPINCODE)
        EXPERIENCE = request.form['EXPERIENCE']
        if EXPERIENCE == '':
            EXPERIENCE = 0
        else:
            EXPERIENCE = int(EXPERIENCE)
        HOSPITALNAME = request.form['HOSPITALNAME']
        HOSPITALADDRESS = request.form['HOSPITALADDRESS']
        CITY = request.form['HOSPITALCITY']
        ABOUTME = request.form['ABOUTME']

        try:
            cursor.execute(f"update Doctor set drName='{NAME}',drMobile={MOBILE},drEmail='{EMAIL}',drSpecialist='{SPECIALIST}',drAbout='{ABOUTME}',drExperience={EXPERIENCE},drHospitalName='{HOSPITALNAME}',drHospitalCity='{CITY}',drHospitalAdd='{HOSPITALADDRESS}',drAdd='{ADDRESS}',drPincode={PINCODE},drClinicAdd='{CLINICADDRESS}',drHavingClinic='{OWNCLINIC}',drHospitalPincode={HPINCODE},drGender='{GENDER}' where drEmail='{LOGINEMAIL}'")
            con.commit()
            flash("Profile Update Successfully",success)
            return redirect('/dprofile')
        except:
            flash("Somthing went wrong in server Try again",warning)
    return redirect('/dprofile')

if __name__=="__main__":
    app.secret_key="admin480"
    app.run(debug=True)