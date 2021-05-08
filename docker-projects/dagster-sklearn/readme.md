# A trivial, contrived example of using Dagster to build a scikit-learn pipeline

## PURPOSE
Create a dagster example that is a little more complex than your typical
"hello world" examples, but not too complex that would overwhelm
someone new to workflow management or task orchestration libraries.  Yet,
it is an example that is practical enough where we are extracting data,
transforming data, and then providing an end result.  I personally found the 
examples in the official tutorial a bit overwhelming or hard to follow. 
It was not readily apparent to me how the pieces of the various dagster abstractions
come together due to not seeing all the example code structured in a cohesive manner or 
not being able to see see all the code in one place.  I think just seeing a portion of the 
code at a time in the examples make it difficult to follow or causes you to have to scroll up or down to see the rest of the code.

### Getting Started
With this repo, you can run the example with Docker or without.  Clone this repo.  Then modify the [workspace.yaml](src/workspace.yaml) file and replace the path to the python executable with the path to your python executable for the environment which has dagster installed.  There is also a `workspace_docker.yaml` file that you can use if using Docker.  Otherwise, you can ignore it.

Then create a `DAGSTER_HOME` environment variable.  A sensible location could be:<br>
`export DAGSTER_HOME=$HOME/.dagster` for Linux/Mac<br>
`set DAGSTER_HOME=%USERPROFILE%\.dagster` for Windows

Then save the `dagster.yaml` file into your `.dagster` folder per your `DAGSTER_HOME` location.  By default, when
you execute your pipeline, sqlite databases will be saved in the `.dagster` folder.  These 
sqlite databases will save your pipeline logs, runs, and event statuses.  You can also use a different
database such as Postgres or MySQL, instead of sqlite.  If you don't specify a `DAGSTER_HOME` environment variable,
then logs, runs, and event statuses will be saved in-memory, instead of the filesystem storage.
See [documentatiion](https://docs.dagster.io/deployment/dagster-instance) for information about default
dagster behavior and how to configure it.

### Development workflow
In dagster, you define tasks with [solids](src/solids/sklearn_solids.py).  Then you define dependencies between solids in a 
[pipeline](src/pipelines/sklearn_pipeline.py) definition.  Then you can group one or more pipelines in a 
[repository](src/repositories/sklearn_repository.py) definition.  With the [workspace.yaml](src/workspace.yaml) file, you can tie a 
repository to a specific Python executable.  You can schedule execution of your pipeline by creating a [schedule](src/schedules/sklearn_schedule.py) definition which you then refer to it in the [repository](src/repositories/sklearn_repository.py) definition (lines 12 through 14).  These are the most basic abstractions and features of dagster.  There are many more such as
sensors for event-based triggering, resources and modes, integration with jupyter notebooks, etc.

### Code Organization
For me at least, it makes sense to place solids, pipelines, schedules, and respositories in 
their own folder for better code organization.  Then we can just import them accordingly.  Then
place the workspace.yaml at the top level above them where you would call the `dagit` command.

Folder tree:

src<br>
├── pipelines<br>
│       └── sklearn_pipeline.py<br>
├── repositories<br>
│       └── sklearn_repository.py<br>
├── schedules<br>
│       └── sklearn_schedule.py<br>
├── solids<br>
│       └── sklearn_solids.py<br>
├── workspace_docker.yaml<br>
└── workspace.yaml<br>

### Next Steps
- ~~Dockerize the application without Docker Compose - make use of Docker network and Docker volume~~
- ~~Dockerize using Docker Compose~~