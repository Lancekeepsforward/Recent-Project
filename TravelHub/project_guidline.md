- Project starts on Jun 12th

# Websit Development Project - "TravelHub" 

The basic structure is to use MySQL as my database, Python as my coding language, HTML, CSS, and Javascript as website development, and flask as connection.

For database:
    1. I want to create a database called "TravelHub"
    2. I need several tables: user, resorts, user_resorts
    3. user table has fields like: id, username, passwords (required to be 8-13 letters in upper and lower cases and at least one special character), datetime of creating account, etc; 

    resorts table has fields like: id, country, state, city, county, resort_name, picture_local_address (for presentation on website), resort_type (try to cover enough type of resorts in enum for searching), etc; 

    user_resorts table has fields like id, created_at, recommendation (a number from 1 to 10), expenditure, comment, etc.
    4. users in users table can log in the websit, at least an admit account (username: admit, passwords: world_peace)

For the website:
    1. Homepage is a matrix-shaped grid presenting the highest average score of resort information (picture and location); A toolbar on top listing login, etc.
    2. Login page
    3. Personal page
    4. user don't have to login again if they go back to the homepage to check out the info.

