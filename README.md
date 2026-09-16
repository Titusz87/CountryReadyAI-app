# CountryReady.ai


<!-- ABOUT THE PROJECT -->
### About The Project



### Features


### Built With

Backend



Frontend

* Flutter


<!-- GETTING STARTED -->
## Getting Started


### Prerequisites


### Installation

Clone the repository:
   ```sh
git clone https://github.com/Titusz87/CountryReadyAI-app.git
cd /CountryReadyAI-app
   ```
Configure the database connection in the backend application properties:
```sh
spring.datasource.url=jdbc:postgresql://localhost:5432/restaurantdb 
spring.datasource.username=postgres 
spring.datasource.password=your_password
```

Start the backend:
```sh
mvn spring-boot:run
```
Start the frontend:
```sh
cd frontend/client-application
npm install
npm start
```
## Application Services

| Service | Port | Purpose |
|----------|----------|----------|
| Frontend (Flutter) | 3000 | Customer-facing web application |
| ML Service | 8080 |  |
