# Copyright 2017 Google Inc. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Sample server that pushes configuration to Google Cloud IoT devices.

This example represents a server that consumes telemetry data from multiple
Cloud IoT devices. The devices report telemetry data, which the server consumes
from a Cloud Pub/Sub topic. The server then decides whether to turn on or off
individual devices fans.

This example requires the Google Cloud Pub/Sub client library. Install it with

  $ pip install --upgrade google-cloud-pubsub

If you are running this example from a Compute Engine VM, you will have to
enable the Cloud Pub/Sub API for your project, which you can do from the Cloud
Console. Create a pubsub topic, for example
projects/my-project-id/topics/my-topic-name, and a subscription, for example
projects/my-project-id/subscriptions/my-topic-subscription.

You can then run the example with

  $ python cloudiot_pubsub_example_server.py \
    --project_id=my-project-id \
    --pubsub_subscription=my-topic-subscription \
"""

import json
import os
import flask
import requests

from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.errors import HttpError

API_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
API_VERSION = 'v1p1beta1'
API_KEY = '<- api key ->'
PROJECT_ID = '<- project id ->'
DISCOVERY_API = 'https://{}.googleapis.com/$discovery/rest'
SERVICE_NAME = 'cloudasset'
PAGE_TOKEN = '<- page token ->'
# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = b'\xf9\xe78\x0e\x86i\x81|G\x83\xe6u^\xb7\xd7F'

class Server(object):
    """Represents the state of the server."""

    def __init__(self, app):
        credentials = service_account.Credentials.from_service_account_file(CLIENT_SECRETS_FILE).with_scopes(API_SCOPES)

        self._app = app

        if not credentials:
            self._app.logger.error('Could not load service account credential '
                     'from {}'.format(CLIENT_SECRETS_FILE))

        discovery_url = '{}?version={}'.format(DISCOVERY_API.format(SERVICE_NAME), API_VERSION)

        self._service = discovery.build(
            SERVICE_NAME,
            API_VERSION,
            discoveryServiceUrl=discovery_url,
            credentials=credentials,
            cache_discovery=False,
            developerKey=API_KEY)

    def get(self, nextPageToken):
        try:
            resourceString = 'projects/{}'.format(PROJECT_ID)
            return self._service.resources().searchAll(scope=resourceString, pageSize=1000, pageToken=nextPageToken).execute()
        except HttpError as e:
            self._app.logger.error('Error executing Cloud Assets get: {}'.format(e))
            return e


@app.route('/')
def index():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '</table>')

@app.route('/test')
def test_api_request():
    page_token = None
    data = { "results": [] }
    while True:
      resp = app.server.get(page_token)
      data["results"].append(resp['results'])
      page_token = resp.get('nextPageToken')
      if not page_token:
        break

    #return flask.jsonify(app.server.get())
    return flask.jsonify(data)

if __name__ == 'main':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.server = Server(app)
