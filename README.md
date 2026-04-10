# Client CRM
A simple CRM system for organizing client information, emphasizing a progression pipeline from lead to client. Designed to help brands identify which stages of the pipeline to prioritize, making it easier to decide whether to focus on converting leads, advancing negotiations, or closing deals.

## Features
- User authentication (register, login, logout)
- Add, edit, and delete client information
- Filter progression pipeline
- Personalized client dashboard

## Tech Stack
- Frontend: HTML with Bootstrap
- Backend: Python (Flask)
- Database: SQLite
- Libraries: SQLite3, flask, werkzeug.security, functools, re, matplotlib, collections

## Backend Overview (app.py)
app.py is the main Python file that uses the Flask framework to operate the backend of the website. It also imports several other libraries, packages, modules, and functions. For example, sqlite3 is a module that allows the creation of a database to store and manage information. From the Flask package, the Flask class is imported to create the application instance, along with functions flash, redirect, render_template, request, and session, all of which are essential for building dynamic web functionality. From the Python library Werkzeug, the module werkzeug.security and its commonly used functions, generate_password_hash and check_password_hash are imported to support user authentication. Finally, wraps from functools is imported to preserve a function’s metadata when it is passed into a decorator. These Python components are used throughout app.py, particularly across the various routes described below.

### Register
The register route enforces several rules when a user registers an account. All fields must be filled in before the POST request is processed. If the input does not meet the requirements, a flash message is displayed and the user is returned to the register page using render_template. If all requirements are met, the username and the hashed password are stored in the sqlite3 database using the generate_password_hash function. Usernames must be unique; if a username is already taken, the user must choose another one. Successful registration redirects the user to the index page.

### Login
The login route checks user inputs when a POST request is made, using data from the sqlite3 database. If the username exists and the password matches the stored hash using the check_password_hash function, the corresponding id from the users table is stored in session["user_id"]. Storing user_id in the session allows users to navigate between pages without having to log in again.

### Logout
The logout route simply clears the session using the clear function. Without user_id in the session, users no longer have access to routes protected by the login_required decorator, which is applied to all routes that require a logged-in account.

### Index
The index route returns all the clients stored in the user’s clients table. The clients’ handle, platform, status, cost, notes, and id are extracted into a variable, which is then passed to render_template and displayed on the HTML page using Jinja.

### Add
The add route allows users to add new clients to the table on their home page by pasting a link and clicking “Add.” When the user’s request method is POST, the link is analyzed using the re (regex) module to determine the platform and the handle of the profile. The handle, platform, and a status of "Lead" are added as a new row in the clients table. The remaining fields are set as empty strings for the user to edit.

### Edit
The edit route allows users to modify information for any existing client in the table. Each row under the actions column has an edit button that users can click. The edit button is associated with that row through the id passed by the index route. Using that id, the corresponding client row can be updated.

### Delete
The delete route works similarly to the edit route, using the id passed by the index route, but instead of editing, it deletes the row. A confirmation page is displayed when users click delete to ensure the action is intentional and to prevent accidental deletion.

### Dashboard
The dashboard route provides users with a visual representation of their client table using the matplotlib.pyplot module. Data such as platform, status, and cost is first extracted from the database. The resulting list of tuples is then converted into a flat list so that it can be passed as valid arguments for graphing. The Counter class from the collections module is also used to count how many times each element appears in the list, allowing these counts to be used as arguments as well. Finally, the graphs are saved as static images to be displayed on the HTML page.

## Installation
1. Clone the repository:
`git clone https://github.com/raymond-v/client-crm.git`

2. Navigate into the folder:
`cd client-crm`

3. Install dependencies:
`pip install -r requirements.txt`

4. Run the app:
`flask run`

5. Open in browser:
`http://127.0.0.1:5000`
