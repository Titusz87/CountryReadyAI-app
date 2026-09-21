# CountryReady.ai


<!-- ABOUT THE PROJECT -->
### About The Project



### Features


### Built With

Backend
FastAPI


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
spring.datasource.url=jdbc:postgresql://localhost:5432/
spring.datasource.username=postgres 
spring.datasource.password=your_password
```

Start the backend:
```sh
cd backend
uvicorn app.main:app --reload
```
Start the frontend:
```sh
cd client
flutter run
```
## Application Services

| Service | Port | Purpose |
|----------|----------|----------|
| Frontend (Flutter) | 3000 | Customer-facing web application |
| ML Service | 8080 |  |
