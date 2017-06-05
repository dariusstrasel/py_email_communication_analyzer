
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import pprint
from datetime import datetime, timezone

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'SLA Tracker'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sla-tracker.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

"""Get Message with given ID.
"""

import base64
import email
from apiclient import errors

def GetThread(service, user_id, thread_id):
  """Get a Thread.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    thread_id: The ID of the Thread required.

  Returns:
    Thread with matching ID.
  """
  try:
    thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
    messages = thread['messages']
    print('thread id: %s - number of messages '
           'in this thread: %d' % (thread['id'], len(messages)))
    thread_metadata = {'thread_id': thread_id,
                       'message_count': len(messages),
                       'messages': messages
                       }
    return thread_metadata
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def parse_thread_timeline(service, user_id, thread_id):
    """ Get a thread and return timeline metrics. """
    thread_metadata = GetThread(service, user_id, thread_id)
    timeline = []
    pp = pprint.PrettyPrinter(width=41, compact=True)
    for message in thread_metadata['messages']:
        #print(message['internalDate'])
        message_headers = message['payload']['headers']
        #print([object for object in message_headers])
        # pp.pprint(data)
        message_date = int(message['internalDate']) / 1000.0
        message_date_formated = datetime.fromtimestamp(message_date).strftime('%Y-%m-%d %H:%M:%S')
        message_data_store = {'Date': message_date_formated}
        # Grab message details from headers
        for property in message_headers:
            if property['name'] in ['To', 'Subject', 'From']:
                message_data_store[property['name']] = property['value']
        timeline.append(message_data_store)
        # Map data in date-sorted arrays
        """[{'From': 'Liz Masik <lmasik@preventure.com>'},
            {'Date': 'Tue, 9 May 2017 15:16:19 -0500'},
            {'Subject': 'Re: 2nd Monitor for Laptop request'},
            {'To': 'Darius Strasel <dstrasel@preventure.com>'}]"""
        #time_series = sorted(message_data_store, key=lambda message: print(message))
    pp.pprint(sorted(timeline, key=lambda message: datetime.strptime(message['Date'], '%Y-%m-%d %H:%M:%S')))


def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    print('Message snippet: %s' % message['snippet'])

    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def GetMimeMessage(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

    print('Message snippet: %s' % message['snippet'])

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    mime_msg = email.message_from_string(msg_str)

    return mime_msg
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def ListMessagesMatchingQuery(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    print(parse_thread_timeline(service, 'me', '15b5e87e410e2009'))
    # print(ListMessagesMatchingQuery(service, 'me', 'vertikal6'))


if __name__ == '__main__':
    main()