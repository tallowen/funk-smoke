import base64
import urllib2
from hashlib import sha256, sha1
import simplejson as json
import random

from funkload.utils import Data


def create_user(email,password,self):
    username=extract_username(email)
    uri='user/1.0/%s'%(username)
    put_data = {
        "password":password,
        "email":email,
    }
    package=Data('application/JSON',json.dumps(put_data))

    self.put(self.server_url+uri, 
             package,
             description='Create Sync User'
    )

    return self.getBody()

def get_collection_info(email,password, self):
    username=extract_username(email)
    getCollectionsString = "1.0/%s/info/collections" % (username)
    self.get(self.server_url+getCollectionsString,description="Get collection info") 
    return json.loads(self.getBody())

def basic_sync(email,password, self):
    collections = [
            {'name':'bookmarks'},
            {'name':'forms'},
            {'name':'passwords'},
            {'name':'history'},
            {'name':'prefs'},
    ]

    username=extract_username(email)

    server_collections=get_collection_info(email,password,self)
    for collection in collections:
        collection['wbos']=[]
        try:
            server_collections[collection['name']]
        except KeyError:
            collection['time']=0
        else:
            collection['time']=server_collections[collection['name']]

    ###Post someting to each of our collections
    for collection in collections:
        postCollectionsString = "1.0/%s/storage/%s" % (username, collection['name'])
        data = payload(username)

        #Store the collection to verify later
        collection['wbos'].append(data)

        #Wrap the payload in a funkload Data object
        package=Data('application/JSON',json.dumps(data))
        self.post(
            self.server_url+postCollectionsString,
            package,
            description='Posting data to server',
        )

        #make sure that the server is giving out a newer time
        self.assert_(self.getBody()>collection['time'], "Collection time not updated")
        collection['time']=self.getBody()

    ###Verify the Data
    for collection in collections:
        #Grab a WBO collection that we know about
        wbo=collection['wbos'][0]
        getCollectionsString = "1.0/%s/storage/%s?full=1" % (username, collection['name'])
        self.get(self.server_url+getCollectionsString,description="Get %s collection"%(collection['name']))

        #Get all the objects from the server
        server_objects=json.loads(self.getBody())

        #Find our matching object
        for server_wbo in server_objects:
            if int(server_wbo['id'])==int(wbo['id']):
                matching_wbo=server_wbo
                break

        #Make sure they have the same data
        self.assert_(matching_wbo['payload']==wbo['payload'])

def chunked_ascii():
    return_values=[]
    for i in range(0,128,8):
        chunk=''
        for j in range(i,i+8):
            chunk+=chr(j)

        return_values.append(chunk)

    return return_values



def payload(username):
    data={
        "id": random.randint(1,100000), 
        "payload": username*random.randint(50,200)
    }
    return data


####Utils for extracting a username from an email####
def email_to_idn(addr):
    """ Convert an UTF-8 encoded email address to it's IDN (punycode)
        equivalent

        this method can raise the following:
        UnicodeError -- the passed string is not Unicode valid or BIDI
        compliant
          Be sure to examine the exception cause to determine the final error.
    """
    # decode the string if passed as MIME (some MIME encodes @)
    addr = urllib2.unquote(addr).decode('utf-8')
    if '@' not in addr:
        return addr
    prefix, suffix = addr.split('@', 1)
    return "%s@%s" % (prefix.encode('idna'), suffix.encode('idna'))

def extract_username(username):
    if '@' not in username:
        return username
    username = email_to_idn(username).lower()
    hashed = sha1(username).digest()
    return base64.b32encode(hashed).lower()


