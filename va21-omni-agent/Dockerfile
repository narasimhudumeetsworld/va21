# Stage 1: Build the frontend
FROM node:18 AS build
WORKDIR /app/frontend
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build the backend
FROM python:3.10-slim
WORKDIR /app
COPY --from=build /app/frontend/build ./frontend/build
COPY backend/ .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
