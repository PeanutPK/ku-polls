## KU Polls: Online Survey Questions 

[![Django CI](https://github.com/PeanutPK/ku-polls/actions/workflows/django.yml/badge.svg)](https://github.com/PeanutPK/ku-polls/actions/workflows/django.yml)
[![flake8 lint](https://github.com/PeanutPK/ku-polls/actions/workflows/flake8.yml/badge.svg)](https://github.com/PeanutPK/ku-polls/actions/workflows/flake8.yml)

An application to conduct online polls and surveys based
on the [Django 5.1 Tutorial project](https://docs.djangoproject.com/en/5.1/intro/tutorial01/), with
additional features.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).

## Running the Application

1. Before running the application make sure to [install](INSTALLATION.md) all requirements.
2. Activate virtual environment
   - For macOS/Linux
    ```commandline
    source env/bin/activate
    ```
   - For Windows
    ```commandline
    env\Scripts\activate
    ```
3. Load poll data from a file
    ```commandline
    python manage.py loaddata data/<filename>
    ```
   For example, in V1.0.0 use this commandline
   ```commandline
   python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
   ```
4. Run django server
    ```commandline
    python manage.py runserver
    ```

## Demo superuser
| **list** | **Username** | **Password**        |
|----------|--------------|---------------------|
| 1        | admin        | MyStrongPassword123 |


## Demo users
| **list** | **Username** | **Password** |
|----------|--------------|--------------|
| 1        | demo1        | hackme11     |
| 2        | demo2        | hackme22     |
| 3        | demo3        | hackme33     |

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).

- [Vision Statement](../../wiki/Vision%20and%20Scope)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project%20Plan)
- [Domain Model](../../wiki/Domain%20Model)

To run docker
- build `docker build -t ku-polls .`
- run `docker run --rm -d -p 8000:8000 ku-polls`

To run docker compose
- build `docker compose --env-file docker.env up --build`
  - If the data isn't shown properly
    - Open docker desktop and go to exec in app section and run
        - `python ./manage.py migrate`
        - `python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json`
        ![docker_img.png](images/dockerhome.png)
        ![exec.png](images/dockerexec.png)
- stop `docker compose down`