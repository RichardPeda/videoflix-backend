# Videoflix API
 This is the API of Videoflix App written with Django 5.1.
 
 You can download the corresponding frontend app of Videoflix
 [Videoflix-Frontend-App](https://github.com/RichardPeda/videoflix-frontend)


### Requirements
You have to install the latest Python version on your computer.
[Download Python](https://www.python.org/downloads/)


 ## Installation
 1. Clone this repository
 2. Create a virtual environment `python -m venv env`
 3. Activate the virtual environment `"env/Scripts/activate"`
 4. then you can run
    
 ```
 pip install requirements.txt
```
 3. Go to the folder "Videoflix_backend"
 4. Generate the database with command `python manage.py migrate`
 5. Run the command `python manage.py createsuperuser` to have access to the admin page
 6. Run the command `python manage.py runserver` to start the app on your machine

 # Documentation
 The documentation of the endpoints was made with SwaggerUi.
 With your local server running, you can find it at the endpoint: [/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
