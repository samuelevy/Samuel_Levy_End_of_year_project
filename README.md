# Implementation of a rating system
A Django-based chess game recording and player rating system using Elo and Glicko-2 rating algorithms.

# Prerequisites
The following need to be installed: Python 3.8, pip Python package (install through Python), and XAMPP software for database management. The project was run and tested on a Windows OS so thpugh it should run on other systems, it is advised to use Windows. XAMPP must be accessed through the user's personal account.

# Basic setup
## Database setup

1. Download and install XAMPP from [apachefriends.org] (https://www.apachefriends.org/)
2. Launch the XAMPP Control Panel as an administrator (launching it normally risks encountering some issues)
4. Change SQL port to *3307*. To do that, follow the steps below
5. Start the **Apache** and **MySQL** modules.


**Change MySQL port**
If you want to use the default port 3306:
- Edit `settings.py` and change `'PORT': '3307'` to `'PORT': '3306'`
**This choice is better if your port 3306 is not already taken, as it allows you to make the project function more easily**

**OR (CHANGE THE PORT):**
1. Click on "Config" next to the MySQL module, open the _my.ini_ file in a text editor
2. Look for element:

`# The MySQL server
default-character-set=utf8mb4
[mysqld]
port=3306
socket="E:/xampp/mysql/mysql.sock"`

and change "3306" to 3307.

3. Save and close the file.
4. Go in the "Config" element next to the Apache module, open the _config.inc.php_ file in a text editor
5. Look for element `$cfg['Servers'][$i]['host'] = '127.0.0.1';`
6. Below that line, add a new line: `$cfg['Servers'][$i]['port'] = '3307';`
7. The port is now 3307 by default instead of 3306, which is what we want.

**Import Database**
1. Access phpMyAdmin by clicking on the _Admin_ button next to the MySQL module.
2. Create a new database called `fypdb` (this stands for 'final year database', and is the name used for the database file, hence the name)
3. Click on the `fypdb` just created
4. Go on the **"Import"** tab
5. Click **"Choose File"** and select the `fypdb.sql` file from the project root
6. Click **"Go"** at the bottom of the page
7. Wait for the success message confirming the import
8. The database is now imported in phpMyAdmin.

## Setting up the project
Start by downloading the files in a directory. We can then start setting up our virtual environment for Django.

### Set up environment
Open a terminal in the project directory location.

**On Windows :**

`python -m venv .venv`

`.venv\Scripts\activate`

**On macOS/Linux:**

`python3 -m venv .venv`

`source .venv/bin/activate`

### Install dependencies
Enter the following commands in the terminal (still in the project directory):

`pip install django==5.0.1`

`pip install mysqlclient`

`pip install djangorestframework`

`pip install pymysql`


# Run the web application
## Prerequisites (to do every time you want to run the web application):
1. Ensure both the Apache and the MySQL servers are running on XAMPP
2. Activate the virtual environment (see below)

**How to activate the virtual environment:**

### Using Powershell:

Navigate to your project directory:
`cd path\to\your\endofyear_project`

Activate virtual environment:
`.venv\Scripts\Activate.ps1`

### Using Command Prompt:
`cd path\to\your\endofyear_project`

`.venv\Scripts\activate.bat`

### Using Mac or Linux terminal (not tested):
`cd path/to/your/endofyear_project`

`source venv/bin/activate`

If the virtual environment runs properly, the terminal environment should change to reflect that, showing `(.venv)` before the other commands.

Once that is done, we can run the server.

**Running the server**
In the `venv` environment, simply type : `python manage.py runserver`.

The server should now be running. When that is done, you can start navigating through the webpages. The best way to start is to access the _Log in_ page, which should be accessible at `http://127.0.0.1:8000/signin/login/`, but this URL could change depending on how you are running your server, so we suggest to try other URLs if this one doesn't work.

# Using the web app
To create a user account, you wan simply use the _Log in_ and _Sign up_ pages. A default admin user is already created in the database, allowing you to log in as such and create a new admin useer; you can then delete the default admin for security reasons.

## Creating an admin user
1. Go the _Log in_ page of the web app and navigate to sign up.
2. Create a new account of what you want to be your admin user. Create a username and a password.
3. Once this account created, log out and go back to the _Log in_ page.
4. Use default admin credentials to log in. Username : `Admin`, Password: `admin123`
5. Once logged in, navigate to the created user's profile and promote them to admin.
6. Once that is done, go the the database on `phpMyAdmin` and delete the default admin entry. MAKE SURE THAT YOU NOW HAVDE TWO ADMIN USERS IN THE DATABASE BEFORE DOING SO.
7. You should now only have one admin user that you created yourself.
