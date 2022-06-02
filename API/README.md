# Payment Service 

API Documentation Link: [DocLink](http://localhost:8081/docs/)

--- 

`Payment Service` - One of the Components of the Song Platform App.
It Allows People to make transactions and purchase Song Subscriptions on specific period of time, Also make refunds and so on...

--- 

##Technologies 

For this project I'm using framework FastAPI as a Main Framework with following additions:

`ORM` - `Ormar and SQLAlchemy` as Integrator chosen the `Alembic`.
`Payment Platform` - `Stripe` one of the most popular  .  
`Database` - `postgresSQL`.

#Deployment 

For Deployment process I've chosen Docker. 


#Usage

Clone This Repo to your IDE or Whatever.

    git clone --branch payment_service git@github.com/LovePelmeni/SongPlatformApp.git

Cd to the directory -> API -> deploy and run docker-compose.yaml 


        docker-compose up -d 

Done! Make Sure all module/integration test has run successfully. 
### Go to the Link Above to get more info about API.