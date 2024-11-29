
# Airport API

API for airport


---

## Installation from GitHub

1. Clone the repository:
   ```bash
   git clone https://github.com/Stekloduv/airport_api
   ```

2. Navigate to the project directory:
   ```bash
   cd airport_api
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: `venv\Scripts\activate`
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables:
   ```bash
   SECRET_KEY=<your-secret-key>
   DEBUG=<True/False>
   ALLOWED_HOSTS=<comma-separated-allowed-hosts>
   POSTGRES_PASSWORD=<your-postgres-password>
   POSTGRES_USER=<your-postgres-username>
   POSTGRES_DB=<your-database-name>
   POSTGRES_HOST=<your-database-host>
   POSTGRES_PORT=<your-database-port>
   PGDATA=<path-to-postgresql-data>
   ```

6. Apply the database migrations:
   ```bash
   python manage.py migrate
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

---

## Running with Docker

1. Build the Docker images:
   ```bash
   docker-compose build
   ```

2. Start the Docker containers:
   ```bash
   docker-compose up
   ```

---

## Access Management

### Creating a Superuser

* **Locally:** Create a superuser by running:
   ```bash
   python manage.py createsuperuser
   ```

* **From within a Docker container:**
  1. Access the container shell:
     ```bash
     docker exec -it <container_name> bash
     ```
  2. Create a superuser:
     ```bash
     python manage.py createsuperuser
     ```

---

## Registering Regular Users

- To register, use the API endpoint at `/api/user/register`.
- Obtain a JWT authentication token at `/api/user/token`.

---

## Features

- JWT-based authentication
- Request throttling to prevent abuse
- Interactive API documentation at `/api/schema/swagger-ui`
- Manage bookings, tickets, and associated data
- Admin-only endpoints for creating airports, routes, crew members, airplanes, flight types, and schedules
- Advanced filtering for routes and flights