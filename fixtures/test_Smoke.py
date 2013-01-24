import unittest
import simplejson as json
import uuid
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import Data
from utils import create_user, get_collection_info, basic_sync, chunked_ascii, payload

class Smoke(FunkLoadTestCase):
    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    def test_get_collections(self):
        self.email="fl_testing%s@mozilla.com"%(uuid.uuid4().hex)
        self.password="password"
        self.username = create_user(self.email,self.password,self)
        self.setBasicAuth(self.username,self.password)

        # The description should be set in the configuration file
        get_collection_info(self.email,'passowrd',self)

    def test_basic_sync(self):
        self.email="fl_testing%s@mozilla.com"%(uuid.uuid4().hex)
        self.password="password"
        self.username = create_user(self.email,self.password,self)
        self.setBasicAuth(self.username,self.password)
        basic_sync(self.email, self.username, self)

    def test_ascii_password(self):
        for password in chunked_ascii():
            self.email="fl_testing%s@mozilla.com"%(uuid.uuid4().hex)
            self.password=password
            self.username = create_user(self.email,self.password,self)
            self.setBasicAuth(self.username,self.password)
            basic_sync(self.email,self.password,self)
        # end of test -----------------------------------------------

class Storage(FunkLoadTestCase):
    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')
        self.email="fl_testing%s@mozilla.com"%(uuid.uuid4().hex)
        self.password="password"
        self.username = create_user(self.email,self.password,self)
        self.setBasicAuth(self.username,self.password)
      
    def test_get_collections(self):
        #Make sure we have some data
        basic_sync(self.email,self.password,self)
        #Query get_collection_info twice
        first_times= get_collection_info(self.email,'passowrd',self)
        second_times= get_collection_info(self.email,'passowrd',self)

        #Make sure that the times are the same
        for collection in first_times:
            self.assert_(first_times[collection]==second_times[collection])

        #add some more data
        basic_sync(self.email,self.password,self)

        #get some more times
        third_times= get_collection_info(self.email,'passowrd',self)

        #make sure that the times are bigger (ie newer)
        for collection in first_times:
            self.assert_(first_times[collection]<third_times[collection])


   
       
    def test_get_collection_usage(self):
        #Make sure we have some data
        basic_sync(self.email,self.password,self)

        getCollectionsString = "1.0/%s/info/collection_usage" % (self.username)
        #Get the sizes
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        first_size=json.loads(self.getBody())

        #get the sizes again
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        second_size=json.loads(self.getBody())

        #Make sure that the sizes are the same
        for collection in first_size:
            self.assert_(first_size[collection]==second_size[collection])

        #add some more data
        basic_sync(self.email,self.password,self)

        #get the sizes again
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        third_size=json.loads(self.getBody())

        #make sure that the size is larger (since we added more data)
        for collection in first_size:
            self.assert_(first_size[collection]<third_size[collection])

        #Put up a single collection
        collection_name='history'
        postCollectionsString = "1.0/%s/storage/%s" % (self.username, collection_name)
        data = payload(self.username)

        #Wrap the payload in a funkload Data object and send to server
        package=Data('application/JSON',json.dumps(data))
        self.post(
            self.server_url+postCollectionsString,
            package,
            description='Posting data to server',
        )

        #Get collection sizes, make sure collection grew
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        fourth_size=json.loads(self.getBody())
        self.assert_(third_size[collection_name]<fourth_size[collection_name])

        #delete added collection
        self.delete(self.server_url+"1.0/%s/storage/%s?ids=%s"%(self.username,collection_name,data['id']))
        self.assert_(self.getBody()=='true')

        #Make sure that the collection size is smaller
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        fifth_size=json.loads(self.getBody())
        self.assert_(fifth_size[collection_name]<fourth_size[collection_name])

    def test_get_collection_count(self):
        #Make sure we have some data
        basic_sync(self.email,self.password,self)

        getCollectionsString = "1.0/%s/info/collection_counts" % (self.username)
        #Get the counts
        self.get(self.server_url+getCollectionsString,description="Get collection count info") 
        first_counts=json.loads(self.getBody())

        #get the counts again
        self.get(self.server_url+getCollectionsString,description="Get collection count info") 
        second_counts=json.loads(self.getBody())

        #Make sure that the counts are the same
        for collection in first_counts:
            self.assert_(first_counts[collection]==second_counts[collection])

        #add some more data
        basic_sync(self.email,self.password,self)

        #get the counts again
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        third_counts=json.loads(self.getBody())

        #make sure that the counts is larger (since we added more data)
        for collection in first_counts:
            self.assert_(type(first_counts[collection])==int)
            self.assert_(first_counts[collection]<third_counts[collection])

        #Put up a single collection
        collection_name='history'
        postCollectionsString = "1.0/%s/storage/%s" % (self.username, collection_name)
        data = payload(self.username)

        #Wrap the payload in a funkload Data object and send to server
        package=Data('application/JSON',json.dumps(data))
        self.post(
            self.server_url+postCollectionsString,
            package,
            description='Posting data to server',
        )

        #Get collection counts, make sure collection grew
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        fourth_counts=json.loads(self.getBody())
        self.assert_(third_counts[collection_name]<fourth_counts[collection_name])

        #delete added collection
        self.delete(self.server_url+"1.0/%s/storage/%s?ids=%s"%(self.username,collection_name,data['id']))
        self.assert_(self.getBody()=='true')

        #Make sure that the collection counts is smaller
        self.get(self.server_url+getCollectionsString,description="Get collection storage info") 
        fifth_counts=json.loads(self.getBody())
        self.assert_(fifth_counts[collection_name]<fourth_counts[collection_name])



if __name__ in ('main', '__main__'):
    unittest.main()
