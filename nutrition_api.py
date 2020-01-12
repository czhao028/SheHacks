import requests
import urllib.request
import time

app_id = "5e584e4b"
api_key = "9cd34c5e59575759d076c31cb8ced90d" # this is for the nutritionx api

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
firApp = firebase_admin.initialize_app(cred)

db = firestore.client()

print('Connection initialized')

def on_snapshot(doc_snapshot, changes, read_time):
    print(doc_snapshot)
    if len(changes) == 0:
        for doc in doc_snapshot:
            print(u'Received document snapshot: {}'.format(doc.id))
    else:
        for change in changes:
            if change.type.name == 'ADDED' or  change.type.name == 'MODIFIED':
                #image classification here: model not ready in time
                print(u'New city: {}'.format(change.document.id))
                print(u'Modified city: {}'.format(change.document.id))

                #"gcsSource": { "inputUris": [ "gs://folder/document1.pdf" ]
                #replace with the link to the image in the cloud

            elif change.type.name == 'REMOVED':
                print(u'Removed city: {}'.format(change.document.id))
                #do nothing

# {

#   // Union field payload can be only one of the following:
#   "image": {
    #     {
    #   "thumbnailUri": string,
    #   "contentUri": string,
    #
    #   "inputConfig": {
    #     object (InputConfig)
    #   }
    #   // End of list of possible types for union field data.
    # }
#   },

#   // End of list of possible types for union field payload.
# }


doc_ref = db.collection('pictures')
doc_watch = doc_ref.on_snapshot(on_snapshot)

print(doc_watch)
while True:
    time.sleep(1)
    print('processing...')