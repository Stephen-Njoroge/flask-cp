[![Coverage Status](https://coveralls.io/repos/github/Stephen-Njoroge/flask-cp/badge.svg?branch=master)](https://coveralls.io/github/Stephen-Njoroge/flask-cp?branch=master)
[![Build Status](https://travis-ci.org/Stephen-Njoroge/flask-cp.svg?branch=master)](https://travis-ci.org/Stephen-Njoroge/flask-cp)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6ca466caff99427fbfb9b51ae54e0a1c)](https://www.codacy.com/app/stephen-njoroge/flask-cp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Stephen-Njoroge/flask-cp&amp;utm_campaign=Badge_Grade)
# flask-cp
A flask bucket list app 

> This application is a Flask API for a bucket list service that allows users to create, update and delete bucket lists.
> In addition users can create, edit and update items in the bucketlist. 

## Endpoints

1. `POST /auth/login`
2. `POST /auth/register`
3. `GET /bucketlists/`: returns all bucket listing of all buckets list
4. `GET /bucketlists/<id>`: returns the bucket list with the specified ID
5. `PUT /bucketlist/<id>`: updates the bucket list with the specified with the provided data
6. `DELETE /bucketlist/<id>`: deletes the bucket list with the specified ID
7. `POST /bucketlists/<id>/items/`: adds a new item to the bucket list with the specified ID
8. `PUT /bucketlists/<id>/items/<item_id>`: updates the item with the given item ID from the bucket list with the provided ID
9. `DELETE /bucketlists/<id>/items/<item_id>`: deletes the item with the specified item ID from the bucket list with the provided ID

## Installation & Setup
1. Download & Install Python
 	* Head over to the [Python Downloads](https://www.python.org/downloads/) Site and download a version compatible with your operating system
 	* To confirm that you have successfully installed Python:
		* Open the Command Prompt on Windows or Terminal on Mac/Linux
		* Type python
		* If the Python installation was successfull you the Python version will be printed on your screen and the python REPL will start
2. Clone the repository to your personal computer to any folder
 	* On GitHub, go to the main page of the repository [Flask-cp](https://github.com/Stephen-Njoroge/flask-cp.git)
 	* On your right, click the green button 'Clone or download'
 	* Copy the URL
 	* Enter the terminal on Mac/Linux or Git Bash on Windows
 	* Type `git clone ` and paste the URL you copied from GitHub
 	* Press *Enter* to complete the cloning process
3. Virtual Environment Installation
 	* Install the virtual environment by typing: `pip install virtualenv` on your terminal
4. Create a virtual environment by running `python mkvirtualenv bl-venv`. This will create the virtual environment in which you can run the project.
5. Activate the virtual environment by running `source bl-venv/bin/activate`
6. Enter the project directory by running `cd flask-cp`
7. Once inside the directory install the required modules
 	* Run `pip install -r requirements.txt`
8. Inside the application folder run the app.py file:
 * On the terminal type `python app/app.py` to start the application
9. To run Tests.
 * `nosetests --with coverage`
