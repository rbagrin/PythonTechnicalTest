# Origin Markets Backend Test

### How to run the application

Inside a virtual environment running Python 3:
- `pip install -r requirements.txt`
- `./manage.py makemigrations`
- `./manage.py migrate`
- `./manage.py createsuperuser` - to create superuser (!!! only superuser can add other users)
- `./manage.py runserver` to run server.
- `./manage.py test` to run tests.

#### To dev-test the application:

##### Init
- create **superuser**
- open **Postman**

##### To dev-test /users
- use '`localhost:8000/users/` as URL
- In **Authorization** tab choose **Basic Auth** and complete the **Username** and **Password** fields using superuser's credentials
- To add a user choose **POST** method, go to **Body** tab and check **raw** data, then select **JSON** and add the next JSON-object to the body field:
~~~
    {
       "username": "<new_user>",
       "password": "<user_password>"
    }
~~~
- To get all users list choose **GET** method (!!! requests are allowed only if superuser's credentials are used for authentication)

##### To dev-test /bonds
- use '`localhost:8000/bonds/` as URL
- In **Authorization** tab choose **Basic Auth** and complete the **Username** and **Password** fields using the user's credentials (any user)
- Test the app as required in the specifications

### Spec:

We would like you to implement an api to: ingest some data representing bonds, query an external api for some additional data, store the result, and make the resulting data queryable via api.
- Fork this hello world repo leveraging Django & Django Rest Framework. (If you wish to use something else like flask that's fine too.)
- Please pick and use a form of authentication, so that each user will only see their own data. ([DRF Auth Options](https://www.django-rest-framework.org/api-guide/authentication/#api-reference))
- We are missing some data! Each bond will have a `lei` field (Legal Entity Identifier). Please use the [GLEIF API](https://www.gleif.org/en/lei-data/gleif-lei-look-up-api/access-the-api) to find the corresponding `Legal Name` of the entity which issued the bond.
- If you are using a database, SQLite is sufficient.
- Please test any additional logic you add.

#### Project Quickstart

Inside a virtual environment running Python 3:
- `pip install -r requirements.txt`
- `./manage.py runserver` to run server.
- `./manage.py test` to run tests.

#### API

We should be able to send a request to:

`POST /bonds/`

to create a "bond" with data that looks like:
~~~
{
    "isin": "FR0000131104",
    "size": 100000000,
    "currency": "EUR",
    "maturity": "2025-02-28",
    "lei": "R0MUWSFPU8MPRO8K5P83"
}
~~~
---
We should be able to send a request to:

`GET /bonds/`

to see something like:
~~~
[
    {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
        "legal_name": "BNPPARIBAS"
    },
    ...
]
~~~
We would also like to be able to add a filter such as:
`GET /bonds/?legal_name=BNPPARIBAS`

to reduce down the results.
