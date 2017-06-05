import json

import flask
from flask import render_template
import httplib2

from apiclient import discovery
from oauth2client import client

app = flask.Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


def get_data():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http_auth)
        files = service.users().messages().list(userId='me', q="today").execute()
        return json.dumps(files)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/gmail.readonly',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    # flow.params['include_granted_scopes'] = 'true'
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))

@app.route('/data')
def data_route():
    return get_data()



if __name__ == '__main__':
    import uuid

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.secret_key = str(uuid.uuid4())
    app.debug = False
    app.run()
