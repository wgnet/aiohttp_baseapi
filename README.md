# aiohttp_baseapi

This is a micro framework for building HTTP APIs on a high level of abstraction on top of aiohttp.
It allows to create jsonapi-like HTTP interface to models in declarative way and leaves it possible to fine tune at any level.

## Quick start
Install the package 

    pip install aiohttp_baseapi
Creates project directory structure in current directory (it also contains two sample apps)

    baseapi-start-project
Install the dependencies

    cd src/
    pip install -r .meta/packages
Configure Postgres DB connection

    echo "DATABASE = {'host':'localhost','port':5432,'database':'test','user':'test','password':'test','minsize':1,'maxsize':10}" > ./settings_local.py
Create migrations

    alembic revision --autogenerate -m "init"
Run migrations

    alembic upgrade head
Run the application

    python ./main.py --port=9000

That's it! You can try the API. 
It contains "default" app - it just prints all existing API methods under "/" location. And "demo" app - it contains two sample models. 

    http GET :9000
    http POST :9000/authors <<< '{"data":{"name":"John", "surname": "Smith"}}'
    http POST :9000/books <<< '{"data":{"category": "Fiction","name":"Birthday","is_available":true, "author_id": 1}}'
    http GET ":9000/books?filter[name]=Birthday&include=authors"
    http GET :9000/books/1
    http PUT :9000/books/1 <<< '{"data":{"is_available":false}}'
    http DELETE :9000/books/1
    
## Features 

There are some built-in features you can use: 

 * filtration
 * sorting
 * fields selection
 * pagination
 * inclusion
 * validation

Request and response formats are inspired by jsonapi.org, but have some differences.

Retrieved information can be filtered using `filter` GET-parameter.
You can filter by multiple fields: `filter[fieldname1]=foo&filter[fieldname2]=bar`.
In this case in response there are values for which the `fieldname1` equals to `foo` and `fieldname2` equals to `bar`.
Also you can filter enumerating desired values: `filter[fieldname]=foo,bar`.
In this case in response there are values for which the `fieldname` equals to `foo` or `bar`.

Retrieved information can be sorted using `sort` GET-parameter.
Also you can sort enumerating multiple values: `sort=fieldname1,-fieldname2`.
In this case values in response will be sorted by `fieldname1` ascending, and then by `fieldname2` descending.

Using parameter `fields` you can retrieve only those fields which you need.
For example: `fields=fieldname1,fieldname2`. In this case values in response will have only `fieldname1` and `fieldname2` fields.

Pagination (limit and offset) can be performed using `page` parameter.
Usage: `page[limit]=10&page[offset]=20` - standard pagination (20 items skipped, maximum 10 returned).

Also there is possibility to attach related entities using parameter `include`.
One can apply described above features (filtration, sorting, etc.) to included entities. It will affect only included entities.
Examples:
`filter[entity.fieldname]=foo` - filtration;
`sort[entity]=fieldname` - sorting;
`fields[entity]=fieldname` - choosing fields;
`page[entity.limit]=10` - pagination.

The data passed in modifying requests (POST, PUT, etc.) can be validated using json-schema (which can be auto-generated from model description) or manually.
Default data provider is database, but you can use anything you wish. 

## Unit tests

Run:

    $ pip install -r .meta/packages_unit
    $ cd src
    $ make unit-test
