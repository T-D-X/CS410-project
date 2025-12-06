# Final project submission details

### Project implementation details 
Link to documentation: https://github.com/T-D-X/CS410-project/blob/master/implementation_details.md

### Setting up the project
Link to documentation: https://github.com/T-D-X/CS410-project/blob/master/README.md
Link to setup video: https://mediaspace.illinois.edu/media/t/1_ixk8hpp1


# Project Update

### Project plan and progress

The following table will list the tasks in the project as well as the progress on them at this point of time.

| Task                                                                                                                                     | Progress |
|------------------------------------------------------------------------------------------------------------------------------------------|----------|
| Gather data for retrieval (i.e. resumes)                                                                                                 |Done     |
| Create a docker-compose with dockerfiles for: Postgresql + pgvector and Webserver for interface (Python Django)                        |Done      |
| Create script to:  Gather relevant data from each file, Generate embeddings the data for each file and Store them in Postgresql    |Done      |
| Create a simple webpage to perform semantic search & display results in the form of the IDs of the rows containing the document matches. |Done      |

Other miscellanous tasks:
- Updloading the project onto a public GitHub respository 
- Write a README with information on how to run the application 
- Complete the report with the findings of the project

### Challenges/issues

1. Exposing the the interaction layer in a way that makes sense although they are expensive processes
2. Having a way to anyone to easily set the project up and run it


### Other relevant details

**Reference links:**

- https://medium.com/timescale/implementing-filtered-semantic-search-using-pgvector-and-javascript-7c6eb4894c36
- https://www.tigerdata.com/blog/combining-semantic-search-and-full-text-search-in-postgresql-with-cohere-pgvector-and-pgai
- https://hasansajedi.medium.com/understanding-semantic-and-hybrid-search-with-python-and-pgvector-0967e83803e6
- https://github.com/pgvector/pgvector

**Repository link:** https://github.com/T-D-X/CS410-project

# Project Proposal

**Title**: Job candidate seeker

**Team Members**: 

**Project Coordinator**:

**Project Keywords**: #project #proposal #semantic-search #job-matching #recruiter-tool #vectorization #pin

**Project Description**

The purpose of this project is to create a simple tool for recruiters to seek out candidates for a given job with specific skill and experience requirements. This is achieved with a database of job candidates and resumes and a simple webpage as an interface to search and retrieve the relevant resumes.
The project will be broken down into two sections:

**1. Preparation of data (resumes)**

Data, in the form of a collection of PDFs, will go through an ingestion process (aka a data pipeline) to retrieve relevant information for each resume like job experiences, skills, and education. The data will be vectorized and stored in a database which supports vector data storage and search.

There are several methods to evaluate the effectiveness of the data pipeline

Manually pull out relevant information from several resumes and compare them to the output of the first part of the ingestion process.
Use several ranking algorithms (e.g. BM25, pseudo relevance feedback) to rank the resumes based on a query and compare that to the results from the vector search.

**2. Interface layer**

In order to interact with the database, a simple webpage with a webserver can be created to structure the query and search the database. The webserver will not include things like authentication and well designed webpages, it will simply search as an interface to the rest of the project.

**Technologies used**
- Python scripts for the data pipeline
- Pretrained embedding models (e.g. Qwen3-embedding)
- Postgresql database with pgvector extension
- Information retrieval algorithms like BM25 and pseudo relevance feedback for evaluation

**Data source**

Resume dataset from kaggle: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset?resource=download
