# Technical Test (Python Developer)

As part of the selection process, we require all candidates for Python developer
positions to complete a technical test.

You can take as much time as you need to complete the exercises, but we’d
suggest you spend no more than 2 hours even if you did not complete all the
steps.

The solution should be submitted as a link to a public git repository (gitlab, github, etc),
or else an archive (zip, tar, etc) shared by email or file-link.

## Task Description

A _vector_ is an object describing one or more spatial entities like points, lines or
polygons.  In a geospatial context, a vector has a Coordinate Reference System (CRS)
that defines the type of coordinates in the vector, eg longitudes and lattitudes.  There are
many different CRSs and it's a common geospatial task to convert between them.

This repository contains a stub HTTP web application for converting vectors
between different CRSs.  The application has user accounts and each user has a
list of CRSs that are permitted as targets.

The users and CRSs are defined in a provided SQLite database called `db.sqlite`.
The database contains three tables:

  - `user`. A list of users by id with username and encrypted password strings.
  - `crs`. A list of CRSs with their EPSG code as a text string.
  - `user_crs`. A list of users along with the target CRS ids that are permitted.

Amongst these tables is captured the following information:

| Username | Password  | Permitted target CRSs            |
| -------- | --------- | -------------------------------- |
| user1    | password1 | epsg:4326, epsg:3857, epsg:32630 |
| user2    | password2 | epsg:4326, epsg:3857             |

The tasks that follow require the application to be populated with an
implementation, tested and packaged into a Docker image.

The web-application should have the following end-points.

  - `/login`. Returns an authentication token for subsequent requests to the
    application.
  - `/projections`. Returns the supported CRSs for a user.
  - `/vector/reproject`. Reprojects a vector between CRSs.

Sample code has been provided to perform the reprojection operation.

We'll look around your code to see how you approached the tasks. We will run
your solution by running `docker-compose up -d` and test it with HTTP calls to
the API running on localhost port 5000 (more on the docker bit of the task
later).  If you have any thoughts, observations or anything else you'd like to
communicate to us, feel free to edit [CANDIDATE_NOTES.txt](CANDIDATE_NOTES.txt).

## Task 1: Setup

  - Clone this repository to a development machine.
  - Install the dependencies with pipenv.
    - [Pipfile](Pipfile) uses Python 3.7.  This can be changed as required by
      your environment.
    - Install any other dependencies you require.
  - Jump into the environment with `pipenv shell`
  - Run the tests with `invoke test`.
    - NB. There are no tests currently!

## Task 2: Initial implementation

In order to get you going directly onto the fun stuff, we've included a stub
Flask application at [reproject/app.py](reproject/app.py).

  - Implement POST `/login`.
    - Grants authorization tokens to a user.
      - The format and content of the token is up to you.
    - Request:
      - Body with JSON like `{"username": "foo", "password": "bar" }`.
    - Response:
      - Body with JSON like `{"access_token": "mytoken"}`.
  - Implement GET `/projections`.
    - Returns the allowed projections for the (authorised) calling user.
    - Request:
      - Headers including `Authorization: Bearer mytoken`.
    - Response:
      - Body with JSON like `["epsg:4326", "epsg:3857"]`

## Task 3: Dockerize the application

Package up the application into a docker container.

  - Add a Dockerfile for containerizing the application.
    - It is recommended to extend [osgeo/proj](https://hub.docker.com/r/osgeo/proj) in order
      to side-step any issues with native library dependencies for pyproj library.
  - Add a `docker-compose.yaml` for starting a single instance of the
    application with Docker Compose.
      - The application should be exposed on localhost port 5000
  - Build the image with `docker-compose build`.

## Tast 4: Add some tests

The test task `invoke test` currently runs no tests.

  - Make `invoke test` run some useful tests.

## Task 5: Implement the reprojection end-point

Extend the implementation to include the reprojection end-point.

  - Implement POST `/vector/reproject`.
    - Returns a vector converted to another CRSs
      - Only GeoJSON formatted vectors are required to be supported.
      - Users without permission to convert to the target CRS should get an error.
    - Request:
      - Headers including `Authorization: Bearer mytoken`.
      - Multipart form body:
        - Files:
          - `geojson`: The GeoJSON file.
        - Data:
          - `target_crs`: The target CRS to convert the GeoJSON file into.
    - Response:
      - Body with GeoJSON content.

## (Optional) Other Tasks:

Any other relavant improvements that you want to make in order to show off your
skills.

It's not our intention to make this test take too long with these optional
tasks. We only wish to convey that the tasks above are open to extend in other
ways that you choose.  You might even just add code comments to describe how you
might do things and where you'd do them.

Examples might include:

  - Add a logging framework
  - Add some more tasks to [tasks.py](tasks.py) for useful stuff like:
    - Performing static code analysis or lint checks.
    - Building the docker image.
    - Running a code formatter.
  - Support other geospatial vector formats, eg ESRI Shapefiles.
  - Support other conventional ways of specifying the target CRS.
  - Add test coverage reports.
  - Add POST and DELETE to `/projections` based on a user permissions model.
