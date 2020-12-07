from rest_framework.test import APISimpleTestCase
from base64 import b64encode
from http import HTTPStatus
from django.core import serializers
from .serializers import UserSerializer

from django.contrib.auth.models import User
from bonds.models import Bond

# helper function that returns Basic auth string encoding the "username:name" string
def get_auth_data(username, password):
    string = username + ":" + password
    return "Basic " + b64encode(str.encode(string)).decode("ascii")

# Test HelloWorld
class HelloWorld(APISimpleTestCase):
    def test_root(self):
        resp = self.client.get("/")
        assert resp.status_code == 200

# Test Users
class Users(APISimpleTestCase):
    databases = '__all__'

    @classmethod
    def setUpClass(cls):

        # Setup data for superuser, uesr1 and user2
        cls.superuser = {
            "username": "superuser",
            "password": "12wq!@WQ",
            "email": ""
        }
        cls.user1 = {
            "username": "user1",
            "password": "12wq!@WQ",
            "email": ""
        }
        cls.user2 = {
            "username": "user2",
            "password": "12wq!@WQ",
            "email": ""
        }
        cls.superuser_auth = get_auth_data(cls.superuser["username"], cls.superuser["password"])
        cls.user1_auth = get_auth_data(cls.user1["username"], cls.user1["password"])

    @classmethod
    def tearDownClass(cls):

        # Delete all users
        User.objects.all().delete()

    def setUp(self):

        # Add superuser
        User.objects.create_superuser(username=self.superuser['username'], password=self.superuser['password'], email="")

    def tearDown(self):

        # Delete all users from db after each test
        User.objects.all().delete()

    def post_users(self, auth_string, data, expected_status):

        self.client.credentials(HTTP_AUTHORIZATION=auth_string)
        res = self.client.post("/users/", data, format='json')
        assert res.status_code == expected_status, "Wrong status code received!"
        return res.json()

    def get_users(self, auth_string, expected_status):

        self.client.credentials(HTTP_AUTHORIZATION=auth_string)
        res = self.client.get("/users/")
        assert res.status_code == expected_status, "Wrong status code received!"

        return res.json()
    
    def get_users_id(self, id, auth_string, expected_status):

        self.client.credentials(HTTP_AUTHORIZATION=auth_string)
        res = self.client.get("/users/{}/".format(id))
        assert res.status_code == expected_status, "Wrong status code received!"

        return res.json()

    def delete_users_id(self, id, auth_string, expected_status):

        self.client.credentials(HTTP_AUTHORIZATION=auth_string)
        res = self.client.delete("/users/{}/".format(id))
        assert res.status_code == expected_status, "Wrong status code received!"

    def test_post_users_superuser_true(self):

        self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)

    def test_get_users_superuser_true(self):

        self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        res = self.get_users(self.superuser_auth, HTTPStatus.OK)
        assert len(res) == 2, "Wrong number of users returned!"

    def test_post_users_simpleuser_false(self):

        self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        self.post_users(self.user1_auth, self.user2, HTTPStatus.FORBIDDEN)

    def test_get_users_simpleuser_false(self):

        self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        self.get_users(self.user1_auth, HTTPStatus.FORBIDDEN)

    def test_get_users_id_simpleuser_false(self):

        res = self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        self.get_users_id(res['id'], self.user1_auth, HTTPStatus.FORBIDDEN)

    def test_get_users_id_superuser_true(self):

        res = self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        self.get_users_id(res['id'], self.superuser_auth, HTTPStatus.OK)
    
    def test_delete_users_id_simpleuser_false(self):

        res = self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        self.delete_users_id(res['id'], self.user1_auth, HTTPStatus.FORBIDDEN)

    def test_delete_users_id_superuser_true(self):

        res = self.post_users(self.superuser_auth, self.user1, HTTPStatus.CREATED)
        self.delete_users_id(res['id'], self.superuser_auth, HTTPStatus.NO_CONTENT)

# Test Bonds
class Bonds(APISimpleTestCase):
    databases = '__all__'

    @classmethod
    def setUpClass(cls):

        cls.superuser = {
            "username": "superuser",
            "password": "12wq!@WQ"
        }
        cls.user1 = {
            "username": "user1",
            "password": "12wq!@WQ"
        }
        cls.user2 = {
            "username": "user2",
            "password": "12wq!@WQ"
        }
        cls.wrong_user = {
            "username": "wrong_user",
            "password": "12wq!@WQ"
        }

        cls.superuser_auth = get_auth_data(cls.superuser["username"], cls.superuser["password"])
        cls.user1_auth = get_auth_data(cls.user1["username"], cls.user1["password"])
        cls.user2_auth = get_auth_data(cls.user2["username"], cls.user2["password"])
        cls.wrong_auth = get_auth_data(cls.wrong_user["username"], cls.wrong_user["password"])

        # Create users
        User.objects.create_superuser(username=cls.superuser['username'], password=cls.superuser['password'], email="")
        User.objects.create_user(username=cls.user1['username'], password=cls.user1['password'])
        User.objects.create_user(username=cls.user2['username'], password=cls.user2['password'])

        cls.test_data = {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "R0MUWSFPU8MPRO8K5P83"
        }

        cls.test_data2 = {
            "isin": "US38259P5089",
            "size": 1000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "7ZW8QJWVPR4P1J1KQY45"
        }

    @classmethod
    def tearDownClass(cls):

        # Delete users and bonds
        User.objects.all().delete()
        Bond.objects.all().delete()

    def setUp(self):
        pass

    def tearDown(self):

        # Delete all bonds from db after each test
        Bond.objects.all().delete()

    def get_bonds(self, auth_string, expected_status, legal_name=None):

        uri = "/bonds/"
        if legal_name:
            uri = "/bonds/?legal_name=" + legal_name

        self.client.credentials(HTTP_AUTHORIZATION=auth_string)
        res = self.client.get(uri)
        assert res.status_code == expected_status, "Wrong status code received!"

        return res.json()
        
    def post_bonds(self, auth_string, data, expected_status):

        self.client.credentials(HTTP_AUTHORIZATION=auth_string)
        res = self.client.post("/bonds/", data, format='json')
        assert res.status_code == expected_status, "Wrong status code received!"

    def test_bonds_get_no_auth_false(self):

        res = self.client.get("/bonds/")
        assert res.status_code == HTTPStatus.FORBIDDEN, "Wrong status code received!"
    
    def test_bonds_get_query_param_no_auth_false(self):

        res = self.client.get("/bonds/?legal_name=BNPPARIBAS/")
        assert res.status_code == HTTPStatus.FORBIDDEN, "Wrong status code received!"
    
    def test_bonds_post_no_auth_false(self):

        res = self.client.post("/bonds/")
        assert res.status_code == HTTPStatus.FORBIDDEN, "Wrong status code received!"
     
    def test_bonds_get_wrong_auth_false(self):

        self.get_bonds(self.wrong_auth, HTTPStatus.FORBIDDEN)

    def test_bonds_get_query_params_wrong_auth_false(self):

        self.get_bonds(self.wrong_auth, HTTPStatus.FORBIDDEN, legal_name="BNPPARIBAS")

    def test_bonds_post_wrong_auth_false(self):

        res = self.get_bonds(self.wrong_auth, HTTPStatus.FORBIDDEN)

    def test_bonds_get_auth_true(self):

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK)
        assert len(res) == 0, "Wrong number of bonds objects returned!"
        
    def test_bonds_get_query_params_auth_true(self):

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK, legal_name="BNPPARIBAS")
        assert len(res) == 0, "Wrong number of bonds objects returned!"

        self.post_bonds(self.user1_auth, self.test_data, HTTPStatus.CREATED)

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK, legal_name="BNPPARIBAS")
        assert len(res) == 1, "Wrong number of bonds objects returned!"

    def test_bonds_post_auth_true(self):

        self.post_bonds(self.user1_auth, self.test_data, HTTPStatus.CREATED)

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK)
        assert len(res) == 1, "Wrong number of bonds objects returned!"

    def test_bonds_user1_bonds_should_be_visible_for_user1_but_not_be_visible_for_user2_true(self):

        self.post_bonds(self.user1_auth, self.test_data, HTTPStatus.CREATED)

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK)
        assert len(res) == 1, "Wrong number of bonds objects returned!"

        res = self.get_bonds(self.user2_auth, HTTPStatus.OK)
        assert len(res) == 0, "Wrong number of bonds objects returned!"

    def test_bonds_get_query_legal_name_true(self):

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK, legal_name="BNPPARIBAS")
        assert len(res) == 0, "Wrong number of bonds objects returned!"

        self.post_bonds(self.user1_auth, self.test_data, HTTPStatus.CREATED)
        self.post_bonds(self.user1_auth, self.test_data2, HTTPStatus.CREATED)

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK)
        assert len(res) == 2, "Wrong number of bonds objects returned!"

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK, legal_name="BNPPARIBAS")
        assert len(res) == 1, "Wrong number of bonds objects returned!"

        res = self.get_bonds(self.user1_auth, HTTPStatus.OK, legal_name="GOOGLELLC")
        assert len(res) == 1, "Wrong number of bonds objects returned!"
