# Educa Project

## Docker Build Instructions

Before building the project with Docker, **please move the following files and folder to the parent directory** (one level above the current project folder):

- `Dockerfile`
- `docker-compose.yml`
- `config` folder
- `requirements.txt`

This ensures that Docker can access all necessary files during the build process.

## Steps

1. Move the files and folder:
    - `Dockerfile` → parent directory
    - `docker-compose.yml` → parent directory
    - `config/` → parent directory
    - `requirements.txt` → parent directory

2. From the parent directory, build and run the Docker containers:
    ```sh
    docker-compose up --build
    ```
