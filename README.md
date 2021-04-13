# BankSubscriberAccount
Operations with subscriber account

---

##Overview

Provided BankAccount model with fields:

- id: uuidV4
- owner_name
- balance
- hold

API:

- `api/{pk}/add` adding value to `balance`
- `api/{pk}/sbtract` subtract value from `balance` by adding in to `hold`
- `api/{pk}/status` get account information

Also provided Celery periodic task that every 10 minutes subtract `hold` value from `balance` and set `hold` as 0.

---  

## I. Technology Stack:  

- Python3  
- Django  
- PostgreSQL
- Celery
- Redis
- Docker

## II. Install and run

### Prerequisites

You will need:

- `docker` with [version at least](https://docs.docker.com/compose/compose-file/#compose-and-docker-compatibility-matrix) `18.02`
- Install `docker` and `docker-compose`
- [`editorconfig`](http://editorconfig.org/) plugin (**required**)

### Steps

1. Put `.env` file to `docker-app/config` directory (See `docker-app/config/.env.template`)


2. For build and run container, run in terminal:
    ```shell
    sh docker-app/run_and_build/build_and_run.sh
    ```
    It will init postgres and migrate.
   

3. For create superuser, run in another terminal (after build):  
   **IMPORTANT! RUN IT DURING PREVIOUS STEP IS STILL WORKING**
    ```shell
    sh docker-app/run_and_build/create_superuser.sh
    ```
   
## III. Tests

For run test, execute in terminal:
```shell
sh docker-app/tests/run_tests.sh
```
