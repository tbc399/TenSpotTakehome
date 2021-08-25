# TenSpot Interview Project

Make a very basic book library application using Django and Django Rest Framework.
There does not need to be UI for this system, just an API that can
be interacted with from Postman/cURL/wget, etc.

#### Principles:
- Quality over quantity
- Fully working features are preferred
- Feel free to modify, delete, or add any code you wish, even start completely from scratch; this template is just provided to potentially help save time on initial spinning up the project.
- Work/life balance is really important.  We realize that everyone has stuff going on.  Take as much time as you wish, but if you find yourself coming up on 6(ish) hours and want to call it good and submit whatever you've got, go for it!

#### Guidelines:
- Include adequate unit/integration tests in the codebase
- If you use any third party libraries for functionality, please inlude comments about why you chose that particular library
- Include any notes about design decisions, assumptions made, architecture choices that you feel are relevant
- Please ask any questions about system specs, design, requirements

Feel free to populate your database through whatever method you prefer: data migrations, management command, script, django admin, etc.
You do not need to have a way to register users, just sign them in and out. (creating in django admin is fine)

#### Notes:
- Unauthenticated users do not have access to the API
- Books are checked out for two weeks
- `takehome/library/tests/test_helper.py` has some sample code to help make data for tests; you do not have to use these helpers, adjust as needed for whatever model structure you decide on.

---

## Users

Users should be able to log in, log out, and depending on their type
have access to various actions.

Users come in three categories:

#### General
General users can:
- View a list all the books
- Get details on a specific book
- View a list of all the books they have checked out
- Check out a book
- Return a book

- View a list of all the authors
- Get the details of a specific author (list of books they have written)
- View a list of all the genres

General users can not:
- see other users
- see who has checked a book out if they are not the user
- check out or return books for users other than themselves


#### Editor
Editor users can:
- Do all the things a general user can
- Add a book
- Update a book's details (excluding its checkout status and due date)
- Add an author
- Update an author's details
- Add a genre

Editor users can not:
- same restrictions as general users
- delete records


#### Administrator
Administrator users can:
- Do all the things an editor can
- Get a list of all the users with the books they have checked out
- Delete an author
- Delete a book
- Delete a genre
- Update a book's checkout status and due date
- View a list of all the books that are overdue

Administrator users can not:
- Treat administrators as essentially super users and can do whatever you give them access to

---

## Data

#### Authors
- First name
- Last name
- List of books they have written


#### Books
- Title
- Author(s)
- Year published
- Genre
- Checked out status
- Due date
- Who has it checked out


#### Genre
- Name


#### Users
- First name
- Last name
- type of user
- list of books they have checked out
