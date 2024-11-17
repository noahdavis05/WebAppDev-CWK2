# app/views.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event, db, Ticket
from .forms import SignupForm, LoginForm, EventForm, TicketForm
from . import app
from datetime import datetime
from sqlalchemy.exc import OperationalError
import json


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Use current_user to get the logged-in user's username
    username = current_user.username 
    
    # get the events created by the user
    events = Event.query.filter_by(event_owner=current_user.id).all()
    
    # get all events by any user that are in the future
    future_events = Event.query.filter(Event.date >= datetime.now()).all()
    
    # get all the tickets for the user
    user_tickets = Ticket.query.filter_by(ticket_owner=current_user.id, ticket_used=0).all()
    used_tickets = Ticket.query.filter_by(ticket_owner=current_user.id, ticket_used=1).all()


    # Prepare the QR code data for each ticket
    ticket_data = []
    for ticket in user_tickets:
        event = Event.query.get(ticket.event_id)
        qr_data = {
            'ticket_id': str(ticket.id),
            'event_name': str(event.event_name),
            'event_date': str(event.date),
            'event_time': str(event.time),
            'ticket_owner': str(ticket.ticket_owner),
            'event_description': event.event_description,  # Add event description
            'event_location': event.location  # Add event location
        }
        # Append the ticket data along with its QR code data into the list
        ticket_data.append(qr_data)

    # Setup the event creation form
    

    return render_template('index.html', message=f"Hello, {username}!", 
                           future_events=future_events, ticket_data=ticket_data, used_tickets=used_tickets)


@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    # get all the user's events
    events = Event.query.filter_by(event_owner=current_user.id).all()
    form = EventForm()
    if form.validate_on_submit():
        # Create the new event
        event = Event(
            event_name=form.event_name.data,
            event_description=form.event_description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            event_owner=current_user.id,
            guests=form.guests.data,
            price=form.price.data
        )

        db.session.add(event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('home'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('events.html', events=events, form=form)

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


@app.route('/event/<int:event_id>/buy', methods=['GET', 'POST'])
@login_required
def buy_ticket(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('home'))

    # Count the tickets initially (for display purposes only)
    ticket_count = Ticket.query.filter_by(event_id=event_id).count()

    if ticket_count >= event.guests:
        flash('All tickets for this event have been sold.', 'danger')
        return redirect(url_for('home'))

    form = TicketForm()
    if form.validate_on_submit():
        try:
            # Begin a transaction and lock during ticket creation
            with db.session.begin_nested():  # Nested transaction ensures proper rollback
                tickets = Ticket.query.filter_by(event_id=event_id).with_for_update().all()
                ticket_count = len(tickets)

                if ticket_count < event.guests:
                    # Create and add the new ticket
                    ticket = Ticket(ticket_owner=current_user.id, event_id=event_id)
                    db.session.add(ticket)
                    db.session.commit()  # Commit locks and updates
                    flash('Ticket purchased successfully!', 'success')
                    return redirect(url_for('home', event_id=event_id))
                else:
                    flash('Sorry, tickets have sold out.', 'danger')
                    return redirect(url_for('home', event_id=event_id))
        except OperationalError:
            flash('An error occurred while processing your request. Please try again.', 'danger')
            return redirect(url_for('home'))

    return render_template('buy_ticket.html', event=event, form=form, ticket_count=ticket_count)


@app.route('/scan-ticket', methods=['GET', 'POST'])
def scan_ticket():
    if request.method == 'POST':
        print("Received POST request")
        print(request.get_json())
        try:
            # Get QR code data from the AJAX request (JSON)
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON data received.'}), 400

            qr_code = data.get('qr_code')  # Extract QR code data from the received JSON
            if qr_code:
                print(f"Received QR Code: {qr_code}")  # Print the QR code to the console
                # now process the qr code
                data = json.loads(qr_code)
                # now get the ticket from the database
                ticket = Ticket.query.get(data['ticket_id'])
                if not ticket:
                    return jsonify({'success': False, 'message': 'Ticket not found.'}), 404
                # now validate the other variables match that of the ticker
                event = Event.query.get(ticket.event_id)
                if not event:
                    return jsonify({'success': False, 'message': 'Invalid ticket.'}), 404
                if event.event_name != data['event_name']:
                    return jsonify({'success': False, 'message': 'Invalid ticket.'}), 400
                if event.date.strftime('%Y-%m-%d') != data['event_date']:
                    return jsonify({'success': False, 'message': 'Invalid ticket.'}), 400
                if event.time.strftime('%H:%M:%S') != data['event_time']:
                    return jsonify({'success': False, 'message': 'Invalid ticket.'}), 400
                if str(ticket.ticket_owner) != str(data['ticket_owner']):
                    return jsonify({'success': False, 'message': 'Invalid ticket.'}), 400
                # now check if the ticket has already been used
                if ticket.ticket_used:
                    return jsonify({'success': False, 'message': 'Ticket has already been used.'}), 400
                # now update the ticket to show it has been used
                print("trying to save")
                ticket.ticket_used = True
                db.session.commit()

                print(data)
                return jsonify({'success': True, 'message': f'Ticket successfully scanned'})
            else:
                return jsonify({'success': False, 'message': 'No QR code data received.'}), 400

        except Exception as e:
            # Catch any other errors and return a 500 error with the error message
            return jsonify({'success': False, 'message': f'Error processing QR code: {str(e)}'}), 500

    # For GET requests, render the scanner page
    return render_template('scan_ticket.html')