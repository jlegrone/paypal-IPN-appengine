import logging
import webapp2
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

"""

Important: After you have authenticated an IPN message (that is, received a VERIFIED response from PayPal), 
you must perform these checks before you can assume that the IPN is both 
legitimate and has not already been processed:

Check that the payment_status is Completed.
If the payment_status is Completed, check the txn_id against the previous PayPal transaction 
that you processed to ensure the IPN message is not a duplicate.

Check that the receiver_email is an email address registered in your PayPal account.

Check that the price (carried in mc_gross) and the currency (carried in mc_currency) 
are correct for the item (carried in item_name or item_number).

"""

# IMPORTANT: Replace seller@example.com with your PayPal email address
ACCOUNT_EMAIL = "seller@example.com"
PP_URL = "https://www.paypal.com/cgi-bin/webscr"

# Set to false if ready for production, true if using PayPal's IPN simulator - https://developer.paypal.com/webapps/developer/applications/ipn_simulator
usePayPalSandbox = False

if usePayPalSandbox:
    # Do not change these values
    ACCOUNT_EMAIL= "seller@paypalsandbox.com"
    PP_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"

class Notification(ndb.Expando):
    # Attributes defined here are referenced in other parts of the application.
    # Using the ndb.Expando type allows us to add additional Attributes later on.
    dateSent = ndb.DateTimeProperty(auto_now_add=True)
    transaction_id = ndb.StringProperty()
    payment_status = ndb.StringProperty()
    custom = ndb.StringProperty()
    verified = ndb.BooleanProperty()

    
    @classmethod
    def transaction_exists(cls, id, status):
        match = Notification.query(ndb.AND(Notification.transaction_id == id, Notification.payment_status == status, Notification.verified == True)).fetch()
        if match:
            return True
        else:
            return False

class IPNHandler(webapp2.RequestHandler):
    def post(self):    
        parameters = None
        if self.request.POST:
            parameters = self.request.POST.copy()
        if self.request.GET:
            parameters = self.request.GET.copy()
     
        if parameters:
            # Send the notification back to Paypal for verification
            parameters['cmd']='_notify-validate'
            params = urllib.urlencode(parameters)
            status = urlfetch.fetch(
                    url = PP_URL,
                    method = urlfetch.POST,
                    payload = params,
                    ).content
    
        payment = Notification(receiver_email = parameters['receiver_email'],
                                transaction_id = parameters['txn_id'],
                                transaction_type = parameters['txn_type'],
                                payment_type = parameters['payment_type'],
                                payment_status = parameters['payment_status'],
                                amount = parameters['mc_gross'],
                                currency = parameters['mc_currency'],
                                payer_email = parameters['payer_email'],
                                first_name = parameters['first_name'],
                                last_name = parameters['last_name'],
                                address_city = parameters['address_city'],
                                address_country = parameters['address_country'],
                                address_street = parameters['address_street'],
                                address_state = parameters['address_state'],
                                address_zip = parameters['address_zip'],
                                verified = False)
        
        # Get and store 'custom' field, if it exists.
        for item in parameters.items():
            if  item[0] == 'custom':
                payment.custom = item[1]

        # Insert new transactions in the database.
        if Notification.transaction_exists(payment.transaction_id, payment.payment_status):
            # This transaction has already been verified and processed.
            logging.debug('Transaction already exists')

        # Verify that the payment is confirmed by PayPal and that it is going to the correct account
        elif status == "VERIFIED" and payment.receiver_email == ACCOUNT_EMAIL:
            
            if payment.payment_status == "Completed":
                payment.verified = True
                # Insert actions to take if a completed transaction is received here:
                
            else:
                payment.verified = False
                # Insert actions to take if a transaction with unverified payment is received here:

            # Insert new (verified) transactions in the database. You may wish to store/log unverified transactions as well as these may be malicious.
            payment.put()
            logging.debug('New transaction added to database')

APPLICATION = webapp2.WSGIApplication([
    ('/', IPNHandler),
], debug=True)
