# Paypal IPN Listener for Google Appengine

This is a Google App Engine python app which acts as an endpoint for PayPal Instant Payment Notifications. By default any new, verified payment notifications will be stored in the project's Cloud Datastore. Further operations must be implemented by the end user.

"Instant Payment Notification (IPN) is a message service that notifies you of events related to PayPal transactions. You can use IPN messages to automate back-office and administrative functions, such as fulfilling orders, tracking customers, or providing status and other transaction-related information."

Documentation for PayPal's IPN system can be found here:
https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNIntro/

## Installation

1. Install the App Engine Python SDK from https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python
2. Create a new project from the Google developer console: https://console.developers.google.com
3. Fork or download the source code from this repository.
4. Change the application name in app.yaml to the ID of the project you created in Google developer console.
5. Change ACCOUNT_EMAIL in main.py to your PayPal email address.
6. Add this new project to the GoogleAppEngineLauncher app and deploy.

## Usage

After deployment, you will need to configure your PayPal account's IPN settings:

	1. Visit https://www.paypal.com/cgi-bin/customerprofileweb?cmd=_profile-ipn-notify
	2. Select 'Choose IPN Settings', input http://your-application-id.appspot.com as the Notification URL, and enable IPN notifications.

You can test your IPN listener using PayPal's IPN Simulator:
https://developer.paypal.com/webapps/developer/applications/ipn_simulator
