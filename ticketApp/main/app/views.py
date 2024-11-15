# app/views.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event, db
from .forms import SignupForm, LoginForm, EventForm
from . import app
from datetime import datetime

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Use current_user to get the logged-in user's username
    username = current_user.username 
    # get the events created by the user
    events = Event.query.filter_by(event_owner=current_user.id).all()
    # get all events by any user that are in the future
    future_events = Event.query.filter(Event.date >= datetime.now()).all()
    # setup the create event form
    form = EventForm()
    if form.validate_on_submit():
        # Create the new event
        event = Event(
            event_name=form.event_name.data,
            event_description=form.event_description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            event_owner=current_user.id
        )

        db.session.add(event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('home'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')
    return render_template('index.html', message=f"Hello, {username}!", events=events, form=form, future_events=future_events)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    
    if form.validate_on_submit():
        # Create the new user
        user = User(username=form.username.data, email=form.email.data)
        
        # Hash the password before storing it
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        login_user(user)  # Log in the user
        return redirect(url_for('login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')
    
    # Render the template with form and error messages if there are validation errors
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get the user by email
        user = User.query.filter_by(email=form.email.data).first()

        # Check if user exists
        if user is None:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
        elif user and user.check_password(form.password.data):  # Check if password matches
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def newEvent():
    form = EventForm()
    if form.validate_on_submit():
        # Create the new event
        event = Event(
            event_name=form.event_name.data,
            event_description=form.event_description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            event_owner=current_user.id
        )

        db.session.add(event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('home'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')
    
    return render_template('new_event.html', form=form)