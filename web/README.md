# Python APIs to perform 2 different tasks:
    1. Find similarities between 2 texts
        Libraries: spacy 
        Model: en_core_web_sm

    2. Recognize an Image
        Libraries: TensorFlow with Keras 
        Models: InceptionV3
    
All APIs are using MongoDB at the back-end as a based DB for users store and transaction counts. 
Using MongoDB web service version hosted in MongoDB clouds. 


## Image Classification API:

- **TensorFlow** - python library helping to work with Machine Learning models

- **Keras** - is an API designed to help to operate libraries created for AI and ML. Keras acts as an interface for the TensorFlow library.
    Keras is like a friendly guide which will help to use all the tools and elements that TensorFlow provides. 

    Will be using Keras to load already pre-trained model **InceptionV3** for image recognition


### To test the Program:
    First, make sure MongoDB cluster is up and running. 

    Second, start the program on the server (or locally):
        **python app.py**
- **To Register User:** 
    Third, make sure the user is registered and can be found in MongoDB DB. 
        Send request to **/register** url with the following body parameters:
    ```json
        {
            "username": "Demi Moor",
            "password": "Welcome123456",
        }
    ```
    Every user will get default number of tokens to use for future requests. 

    Now test the program by sending requests to the following url:
        POST request to: **[BASE_URL]/classify**
    
        Body: row JSON:
        ```json
        {
            "username": "Demi Moor",
            "password": "Welcome123456",
            "url": "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
        }
        ```

## Find Similarities in the text API:
Using spacy python library for documents comparison. 
    Currently this library/model is downloaded into our source code folder. This is done for a reason not to depend on the online web upload. 
    If required, the same model can be downloaded and installed on the fly directly from spacy web site. 
    This can be specified in Dockerfile as following:
        RUN pip install -U spacy
        RUN python -m spacy download en_core_web_sm
    
    Preferable way to keep the model in the same folder with the app in case the web site is down or to avoide version upgrade/web site letancy time etc.
