# airport_api_service
This API creates orders with tickets for traveling by air.
Here admin user can create and handle instances for API, such as
airports, airplanes, airlines, routes, flights and crew members.
Non admin user can create orders with tickets.

# Installing using GitHub:
Install PostgresSql and create db
~~~
git clone https://github.com/RVChornyy/airport_api_service.git
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
set next:
POSTGRES_DB=db hostname
POSTGRES_USER=db user
POSTGRES_PASSWORD=password
POSTGRES_HOST=db host
API_KEY=API key for Weather Api [https://www.weatherapi.com/docs/] 
SECRET_KEY=your secret key
python manage.py migrate
python manage.py loaddata airport_db_data.json
python manage.py runserver
~~~
# Run with Docker:
Docker should be installed
~~~
docker-compose up
~~~
# Users info:
you can create user:
/api/user/register/
access:
api/user/token

# Features:
JWT authentication
Admin panel /admin/
Documentation: /api/doc/swagger/
Observe weather at airports
Filter flights by airports

# Diagram image:
[https://github.com/RVChornyy/airport_api_service/blob/develop/diagram_image.png]


