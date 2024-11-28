# app/views.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event, db, Ticket, StripeKey
from .forms import SignupForm, LoginForm, EventForm, TicketForm, StripeKeyForm
from . import app
from datetime import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
import json
import stripe

YOUR_DOMAIN = 'https://http://localhost:5000'

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Use current_user to get the logged-in user's username
    username = current_user.username 

    # get all events by any user that are in the future
    future_events = Event.query.filter(Event.date >= datetime.now()).all()
    for event in future_events:
        event.price = "{:.2f}".format(event.price)
    
    # get all the tickets for the user
    user_tickets = Ticket.query.options(
        joinedload(Ticket.event)
    ).filter_by(
        ticket_owner=current_user.id, ticket_used=0, deleted=0
    ).join(Event).order_by(Event.date).all()
    future_tickets = []
    for ticket in user_tickets:
        # Convert ticket.event.date to a datetime object if it's a string
        event_date = datetime.strptime(ticket.event.date, '%Y-%m-%d').date() if isinstance(ticket.event.date, str) else ticket.event.date
        
        # Compare the dates (both are now datetime.date objects)
        if event_date >= datetime.today().date():
            future_tickets.append(ticket)

    used_tickets = Ticket.query.filter_by(ticket_owner=current_user.id, ticket_used=1, deleted=0).all()
    # in used tickets make all the datetimes in style dd-mm-yyyy hh-mm
    for ticket in used_tickets:
        if ticket != None:
            if ticket.scanned_at:
                ticket.scanned_at = ticket.scanned_at.strftime("%d-%m-%Y %H:%M")

    #and don't commit so these changes are only visible on the view, but not in db


    # Prepare the QR code data for each ticket
    ticket_data = []
    for ticket in future_tickets:
        event = Event.query.get(ticket.event_id)
        qr_data = {
            'ticket_id': str(ticket.id),
            'event_name': str(event.event_name),
            'event_date': str(event.date),
            'event_time': str(event.time),
            'ticket_owner': str(ticket.ticket_owner),
            'event_description': event.event_description,  # Add event description
            'event_location': event.location,  # Add event location
        }
        # Append the ticket data along with its QR code data into the list
        ticket_data.append(qr_data)

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON data received.'}), 400
            
            ticket_id = data.get('ticket_id')
            if ticket.id:
                print(ticket_id)
                # now make the deleted value true
                ticket = Ticket.query.get(ticket_id)
                ticket.deleted = True
                db.session.commit()
                return jsonify({'success': True, 'message': f'ID valid'})
            else:
                return jsonify({'success': False, 'message': 'invalid id'}), 400
        except Exception as e:
            # Catch any other errors and return a 500 error with the error message
            return jsonify({'success': False, 'message': f'Error processing id: {str(e)}'}), 500

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
    if not current_user.is_authenticated:
        flash('You need to be logged in to log out.', 'danger')
        return redirect(url_for('/'))
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
    tickets = Ticket.query.filter_by(event_id=event_id)
    

    # now check for unpaid tickets older than created more than 30 mins ago, if there are, delete them.
    for ticket in tickets:
        if (datetime.now() - ticket.created_at).total_seconds() > 1800 and ticket.paid == 0:
            db.session.delete(ticket)
            db.session.commit()

    tickets = Ticket.query.filter_by(event_id=event_id)
    ticket_count = tickets.count()

    if ticket_count >= event.guests:
        flash('All tickets for this event have been sold.', 'danger')
        return redirect(url_for('home'))
    
     # get the stripe keys of the event owner
    print(event.event_owner)  # Debugging step
    keys = StripeKey.query.filter_by(user_id=event.event_owner).all()
    # Check if keys are returned and if so, access them
    if keys:
        # Access the decrypted public and private keys
        priv_key = keys[0].private_key
        stripe.api_key = priv_key
        pub_key = keys[0].public_key
        print(f"Private Key: {priv_key}, Public Key: {pub_key}")
    else:
       flash('This ticket vendor has not setup a payment system yet!','danger')
       return(url_for('home'))


    form = TicketForm()
    if form.validate_on_submit():
        try:
            with db.session.begin_nested():
                tickets = Ticket.query.filter_by(event_id=event_id).with_for_update().all()
                ticket_count = len(tickets)

                if ticket_count < event.guests:
                    # Create and add the new ticket
                    ticket = Ticket(ticket_owner=current_user.id, event_id=event_id, created_at=datetime.now())
                    db.session.add(ticket)
                    db.session.commit()

            # Move Stripe session creation here
            expires_at = int(datetime.utcnow().timestamp()) + 1800
            session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'gbp',  # Replace 'usd' with your preferred currency
                            'product_data': {
                                'name': event.event_name,  # Use your event name or another descriptive label
                            },
                            'unit_amount': int(event.price * 100),  # Convert price to cents
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + f'/success/{ticket.id}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=YOUR_DOMAIN + '/cancel',
                expires_at=expires_at,
            )

            return redirect(session.url, code=303)

        except OperationalError:
            flash('An error occurred while processing your request. Please try again.', 'danger')
            return redirect(url_for('home'))


    return render_template('buy_ticket.html', event=event, form=form, ticket_count=ticket_count)





@app.route('/scan-ticket', methods=['GET', 'POST'])
@login_required
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
                # get the event from the ticket
                event = Event.query.get(ticket.event_id)
                if current_user.id != event.event_owner:
                    return jsonify({'success': False,'message': 'This ticket is not for your event'})
                # now update the ticket to show it has been used
                print("trying to save")
                ticket.ticket_used = True
                ticket.scanned_at = datetime.now()
                db.session.commit()

                #print(data)
                return jsonify({'success': True, 'message': f'Ticket successfully scanned'})
            else:
                return jsonify({'success': False, 'message': 'No QR code data received.'}), 400

        except Exception as e:
            # Catch any other errors and return a 500 error with the error message
            return jsonify({'success': False, 'message': f'Error processing QR code: {str(e)}'}), 500

    # For GET requests, render the scanner page
    return render_template('scan_ticket.html')


@app.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    # firstly check the logged in user owns the event 
    event = Event.query.get(event_id)
    if event.event_owner != current_user.id:
        flash('You do not have access to this event!', 'danger')
        return redirect(url_for('home'))
    form = EventForm()
    if form.validate_on_submit():
        event.event_name = form.event_name.data
        event.event_description = form.event_description.data
        event.date = form.date.data
        event.time = form.time.data  # No need for strptime conversion
        event.location = form.location.data
        event.event_owner = current_user.id
        event.guests = form.guests.data
        event.price = form.price.data


        db.session.commit()
        flash('Succesfully updated event!', 'success')
        return redirect(url_for('events'))
    
    event_time_str = event.time.strftime("%H:%M")
    return render_template('edit_event.html', form=form, event=event, event_time_str=event_time_str)


@app.route('/event/<int:event_id>')
@login_required
def view_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('home'))
    # get all the tickets for the event
    tickets = Ticket.query.filter_by(event_id=event_id).all()
    return render_template('view_event.html', event=event, tickets=tickets)


@app.route('/success/<int:ticket_id>')
@login_required
def success(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('home'))

    ticket.paid = True
    db.session.commit()
    flash('Ticket purchased successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/add-stripe', methods=['GET', 'POST'])
@login_required
def add_stripe():
    # Check if the user already has a Stripe key saved
    existing_stripe_key = StripeKey.query.filter_by(user_id=current_user.id).first()
    
    # If the user already has a Stripe key, pre-fill the form with their data
    if existing_stripe_key:
        form = StripeKeyForm(public_key=existing_stripe_key.public_key, private_key=existing_stripe_key.private_key)
    else:
        form = StripeKeyForm()

    if form.validate_on_submit():
        # If user already has a Stripe key, update it
        if existing_stripe_key:
            existing_stripe_key.public_key = form.public_key.data
            existing_stripe_key.private_key = form.private_key.data
        else:
            # If no Stripe key exists, create a new one
            new_stripe_key = StripeKey(
                public_key=form.public_key.data,
                private_key=form.private_key.data,
                user_id=current_user.id
            )
            db.session.add(new_stripe_key)

        # Commit the changes to the database
        db.session.commit()

        flash('Your Stripe keys have been saved/updated successfully!', 'success')
        return redirect(url_for('events'))  # Redirect to the page where they can view their saved keys

    return render_template('add_stripe.html', form=form)

