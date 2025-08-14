# Bookstore API

A Django REST API for managing books, categories, orders, and reviews.  
Includes interactive documentation via Swagger and Redoc.

---

## 🚀 Features

- **Books**: List, filter, search, and paginate books.
- **Categories**: Organize books by category.
- **Orders**: Authenticated users can place and view orders.
- **Reviews**: Only users who purchased a book can review it.
- **JWT Authentication**: Secure endpoints with JSON Web Tokens.
- **Interactive API Docs**: Swagger and Redoc UIs for exploring and testing endpoints.

---

## 🐳 Quick Start (Docker)

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd bookstore
   ```

2. **Configure environment variables:**
   - Copy `sample.env` to `.env` and fill in your secrets.

3. **Build and run containers:**
   ```sh
   docker-compose up --build
   ```

4. **Access the API and docs:**
   - API: [http://localhost:8000/](http://localhost:8000/)
   - Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
   - Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 🧪 Running Tests

To run tests inside the Docker container:

```sh
docker-compose exec web sh
export DJANGO_SETTINGS_MODULE=bookstore.settings
pytest store/tests.py
```

---

## 📚 API Documentation

- **Swagger UI** and **Redoc** provide interactive docs.
- You can view all endpoints, see request/response formats, and try out requests directly from the browser.

---

## 📝 How to Use

- Clone the repo and start the containers.
- Register a user via the API or admin panel.
- Use Swagger/Redoc to explore and test endpoints.
- All business logic is handled via REST API—no frontend required.

---

## 🗂 Project Structure

```
bookstore/
├── bookstore/         # Django project settings
├── store/             # Main app: models, views, serializers, tests
├── Dockerfile         # Docker build file
├── docker-compose.yml # Docker Compose setup
├── requirements.txt   # Python dependencies
├── .env               # Environment variables (not tracked)
├── sample.env         # Example env file
└── README.md          # Project info
```

---

## ⚠️ Notes

- Do **not** commit your `.env` file—keep secrets safe!
- All data is stored in PostgreSQL (via Docker).
- For development, use the provided Docker setup.

---

## 💡 Contributing

Pull requests and issues are welcome!

---
