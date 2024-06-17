from flask import Blueprint,url_for,render_template,request,redirect,flash,jsonify
from flask_login import login_required, current_user
import time
from . import db , scheduler
from .models import Schedule
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import math
from gpiozero import LED
from time import sleep

relay = LED(17)





def end(str,name):
    # stops the water pump and ends the background timer that ran this code inorder to be used again.
    print(str)
    relay.off()
    sleep(3)
    scheduler.remove_job(name)

def myfunc(string,duration,hours,minutes):
    # Terrible name but its the one I chose this is the function that runs the water pump when this function fires it declares the output pin and then makes a schedule to run the end function so that the app is still responsive when the water pump is on.
    print(string,duration)
    scheduler.add_job(end,'interval',seconds=duration,args=["hello world","temp_timer_sched"],id="temp_timer_sched",replace_existing=True)
    relay.on()
    sleep(3)



def convert24(time):
    # Parse the time string into a datetime object
    t = datetime.strptime(time, '%I %p')
    # Format the datetime object into a 24-hour time string for the background scheduler as it runs on 24 hr clock
    return t.strftime('%H')
 
def time_format(hrs,min,per):
    # Format the time ti be presented on the websites in 12 hr format
    hrs = str(hrs)
    t = datetime.strptime(str(min), '%M')
    min = t.strftime('%M')
    final = hrs+":"+min+" "+per
    return final
# Local time has date and time


views = Blueprint('views',__name__)
#create route (base route)
def tod():
    t = time.localtime()
    if t.tm_hour>=12:
        return "Evening "
    return "Morning "

@views.route("/runsched",methods=['GET','POST'])
def run():
    t = time.localtime()
    myfunc("heeyyyeyy",10,9,46)
    return jsonify({})
@views.route('/',methods=["GET","POST"])
@login_required
def home():   
    # trigger = CronTrigger(
    #     year="*", month="*", day="*", hour="9", minute="34", second="0"
    # )
    # scheduler.add_job(myfunc,
    # trigger=trigger,
    # name="daily foo",
    # )
    print(scheduler.get_jobs()) 
    return render_template("home.html", user=current_user,greet_per = tod())
@views.route("/schedules")
@login_required
def schedule():
    return render_template("schedule.html", user=current_user,no_sched = len(Schedule.query.all()) ,schedules = Schedule.query.all())

@views.route('/add_sched', methods=["GET","POST"])
@login_required
def add_sched():
    if request.method == "POST":
        print(request.form )
        name_of_schedule = request.form.get("sched_name")
        TODh = request.form.get("TODh")
        TODm = request.form.get("TODm")
        per_of_day = request.form.get("per_of_day")
        duration = request.form.get("dura")
        if len(TODh) > 0 and len(TODm) > 0:
            TODh = int(TODh)
            TODm = int(TODm)
            if len(duration) > 0:
                duration = int(duration)
                sched = Schedule.query.filter_by(name=name_of_schedule).first()
                if sched:
                    flash("Name already exsists" ,category='error')
                elif len(name_of_schedule) == 0:
                    flash("Must enter a name for the schedule" ,category='error')
                elif TODh > 12  or TODh < 1:
                    flash("Invalid input for hourly time." ,category='error') 
                elif TODm > 59  or TODm < 0:
                    flash("Invalid input for time in minutes." ,category='error')
                elif duration < 0:
                    flash("Duration must be greater than 0 seconds." ,category='error')
                else:
                    schedules = Schedule.query.all()                    
                    new_schedule = Schedule( name = name_of_schedule ,timeh = int(convert24(str(TODh)+" "+ per_of_day)) , timem = TODm,time12=time_format(TODh,TODm,per_of_day), per_of_day = per_of_day , duration = duration , data_name= len(schedules) +1,user_id = current_user.id)
                    db.session.add(new_schedule)
                    db.session.commit()
                    trigger = CronTrigger(year="*", month="*", day="*", hour=str(new_schedule.timeh), minute=str(new_schedule.timem), second="0" )
                    scheduler.add_job(myfunc,trigger=trigger,args=["hello world",new_schedule.duration,new_schedule.timeh,new_schedule.timem],id=new_schedule.name,replace_existing=True)
                    print(scheduler.get_jobs())
                   
                    schedules = Schedule.query.all()
                    for i in schedules:
                        print(i.name)
                    flash("Added succesfully" , "succes")
                    return redirect(url_for('views.schedule'))
            else:

                flash("You have to input a value for duration." ,category='error')
        else:
            flash("You have to input a value for time." ,category="error")
    return render_template("add_sched.html", user=current_user)
@views.route("/delete-sched",methods=['POST'])
def delete_sched():
    sched = json.loads(request.data)
    schedid = sched['schedId']
    note = Schedule.query.get(schedid)
    if note:
        scheduler.remove_job(note.name)
        db.session.delete(note)
        db.session.commit()
        
    return jsonify({})