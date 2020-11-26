# Discount API
Discount API is a REST-API using Flask, Nginx, and Redis.
The API enables a brand to create discount codes. Also allows a user to get
a discount code if available. 

## How to build from code
Clone the code:
```bash
git clone git@github.com:m12i/discount.git
cd discount
```

Create a virtual environment and activated it:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install libraries:
```bash
pip install -r requirements.txt
```

Run tests:
```bash
python -m unittest test_storage.py
```

## How to run
To run the server you need to deploy it using `Docker Compose`.

### Install Docker and Docker Compose:
An easy wat to do so on MacOS is to install [Docker Desktop](https://docs.docker.com/docker-for-mac/install/):
When the installation is done and Docker server is running, you can deploy the 
app with two replicas. 

```bash
docker-compose up --build -d --scale app=2
```

To check if the deployment is successful:

First check the process:
```bash
 docker ps --format "table {{.ID}}\t{{.Names}}"
```
You should see an output like below if all containers are up and running:
```bash
CONTAINER ID        NAMES
959ec3076d1e        nginx
92e9319daf97        discount_app_2
6decd75b9088        discount_app_1
2168db4a1c08        discount_redis_1
```

To see if the app is healthy send the following request which should
get `OK` in return :
```bash
curl -XGET 'http://localhost/healthy'
```

## How to use the API
The API endpoints are as follows:

| end point             | method | description                 |
|-----------------------|--------|-----------------------------|
| /healthy              | GET    | health check                |
| /discount             | POST   | insert a new discount        |
| /discount             | GET    | get a list of all discounts        |
| /discount/{id}/grant  | GET    | Get discounts for a user     |

When running the server using docker-compose, the host will be:
`localhost` and port `80`.

The following sections describes how to satisfy different usecases using the API.

### Create a discount
**Use Case 1:** A brand requests a new discount to be generated.

Let's say `IKEA` sends a request to create a discount.
To do so, a `POST` request should be sent to `/discount` endpoint with
the data in the body as shown below: 
```bash 
curl -XPOST 'http://localhost/discount'  \
    -H 'Content-Type: application/json' \
    -d '{"brand_id": "IKEA", 
         "discount_code": "Christmas 2020 discount", 
         "total_count": 100}'
```
The response will be like:
```json
{
  "brand_id": "IKEA", 
  "created_at": "2020-11-26T10:27:57.202420Z", 
  "discount_code": "Christmas 2020 discount", 
  "id": "dsc-_t7rAPfmQbCXyPytq77a6A", 
  "total_count": 100
}
```

### Fetch all discounts
**Use Case 2:** Fetch all discounts. 

To do so, send a `GET` request to `/discount` like below:

```bash
curl -XGET 'http://localhost/discount'
```

Response expected:
```json
{
  "discounts": [
    {
      "brand_id": "IKEA", 
      "created_at": "2020-11-26T10:27:57.202420Z", 
      "discount_code": "Christmas 2020 discount", 
      "id": "dsc-_t7rAPfmQbCXyPytq77a6A", 
      "total_count": 100
    }
  ]
}
```

### Grant a discount
**Use Case 3:** Grant a discount code to a user. 

To do so, send a `POST` request to `/discount/dsc-_t7rAPfmQbCXyPytq77a6A/grant` with body as:
with
the data in the body as shown below: 
```bash 
curl -XPOST 'http://localhost/discount/dsc-_t7rAPfmQbCXyPytq77a6A/grant'  \
    -H 'Content-Type: application/json' \
    -d '{"user_id": "User 1"}'
```

Response expected:
```json
{
  "discount_id": "dsc-_t7rAPfmQbCXyPytq77a6A", 
  "granted": true
}
```

# The Server Design
As shown in the following diagram a the server is behind a load-balancer (Nginx) and can be
run in multiple replicas to support scaling horizontally. Redis' in memory data store 
is used to store the data in a way that it's shared between the replications of the API.
 
 ![Diagram](https://github.com/m12i/discount/blob/main/doc/diagram.png?raw=true)

### Assumptions and improvements
 1. The current implementation uses an in-memory database. The design
 allows adding a persistent layer e.g. a database. In that case, Redis can be used slightly
 differently, this time as only a caching mechanism (holding parts of the data).
 1. Setting up a Redis cluster can bring redundancy and scalability to the in-memory database and caching.
 1. The current implementation user and brand auth and validation.
 1. The load balance is set up as round-robin. A customized method of load balancing
 based on user's information, geographical region, etc can be developed to route
 the requests in a more performant way.
 
 ### ToDos
 1. Integration test
 2. Move the python source to `src` for better code organization.
 3. Add more error handling and test for edge cases of data and possible errors when dealing with Redis
   