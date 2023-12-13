How we designed our Bridge webapp?

We wanted to create a social media app that would enable basic functions of a social media app. We focused on:
1. Connecting users by enabling them to search and view profile information for people from various countries and univerisities.

2. Allowing users to interact with the feed by creating, liking, commenting on, and viewing posts both of their own and other users.

3. Allowing users to access events in their community by searching for specific events by title and posting their own events.

4. Allowing users to access opportunities in their community by searching for specific opportunities by title and posting their own opportunities.

5. Allowing users to edit and create their own profile with fun aspects like the questions about their country.


Now, we will explain how each of the functionalties was implemented in the order of how user interacts with the webapp.


1. Registering and creating a profile

To establish a good foundation for our social media app, we initiated the creation of a user table. This table encompassed essential fields such as id, name, password (hashed) email, location, country, and college, ensuring we had the most relevant information for user profiles. This thoughtful selection of fields laid the foundation for functionalities like searching for users from specific countries because that information could be accessed through ids.

To enhance the depth of user information, we implemented specific tables: 'socials', 'college', 'country', and 'profile_questions', all linked to a specific user with a foreign key. For instance, we employed foreign keys, using country and college IDs, in the user table. Similarly, the user ID was utilized as a foreign key in the 'profile_questions' and 'socials' tables. The socials contained the text fields for links or username that a particular user has on Facebook, Instagram and Linkedin. The profile_questions table holds answers to the prompted questions which the user can answer when he edits his profile in the 'my profile' section. The interrelation of these tables allowed us to gather comprehensive user data and show it in the 'my profile' page. This was done by extracting all of the relevant information for a specific user, which we accomplished with a function get_user_profile() in the helpers.py. We passed on the relevant data on to the template which could later be accessed though the jinja notation for displaying. This structured approach to database design ensured that our social media app has the necessary interconnected data to be able to show all the relevant information in the my profile section, but also for the data to be changed, and updated via the edit_profile function. Adding a 'edit profile' button and rendering the specific edit_profile.html achieved this functionality.


2. Feed page

To create the feed page, we designed a function that retrieves all posts from the database and passes the information to the template for display. First, we established the 'post', 'post_like', and 'post_comment' tables to store post-related data such as captions, post creation times, and image paths. For likes and comments, we utilized separate tables, storing foreign keys for post_id and user_id, along with the timestamp. Additionally, a content field was added to the comment table to store the user's comment text. This was the base for our functions so we can get the data from the forms, store them and later extract them for presenation to the user. To efficiently load post information, update like counts, and display comments, we implemented helper functions. These functions retrieve all comments, obtain like counts, and fetch usernames associated with posts or comments. The formatted information for each post, including comments, likes, the posting user's username, and all of the comments that include the relevant information in the comment table, was then passed to the 'feed' function which added all of the information from the posts into a formated _post list of post so that we can display all the information more easily in the templates.

Also, we implemented the `create_post` method to allow users to make posts. The `create_post` template was created to allow this, and it checks for filled-in data (specifically the image and caption). When a user posts, this information is inserted into the 'post' table in the database. Subsequently, the feed function retrieves and displays the newly posted content along with other posts.

In order to keep a user from being able to give a post as many likes as they want, we created a `like_post` function. It works by adding to the database when a user likes a post only if the pair between that post and the user does not exist yet. If it doesn not, the user has not liked the post and we can update the number of likes on the post to everytime that post id shows up in the table storing the relationship between the users likes and the posts.


3. Connect page

To implement the Connect page, our goal was to display users based on the search parameters provided by the user. If the user input is null, we executed a database command to retrieve all users. Otherwise, the query would return an appropriate result based on the country, college and username parameters and the extracted information would then be passed to the template and loaded for display.

Efficiency was a key consideration in our code design. Instead of relying on numerous if/else statements, we opted for a dynamic query approach. This allowed the code to efficiently adjust and create queries based on user-provided parameters such as username, country, or college. This streamlined the search process and enhanced the overall performance of the Connect page.

Additionally, we incorporated a function in the helpers.py file that would load the user prodile data if the user for example want to look up the profile of a specific user. This function retrieves all user data based on the user_id value obtained from a button click on the Connect page. When triggered, this function loads the user's profile page in the profile.html template and shows all the details in socials, profile_questions as well as elementary data from users.


4. Events and Opportunities Implementation:

For Events, we established an 'event' table to store essential event information such as location, description, date, and title. Our aim was to allow users to search the database for specific events by title. This was achieved by filtering information based on the title parameter provided by the user. If no parameter was given or it was null, all events were displayed. Simultaneously, we wanted users to have the ability to create their own events. To facilitate this, we designed a dedicated page for users to input specific event details and post their event. Upon submission, the event details were inserted into the database table. When users were redirected to the Event page, their newly created events were immediately loaded alongside all other events. These events are ordered by soonest to latest. The same logical flow was applied to the Opportunities page. The main difference between the pages is that the Event page is more informal while the Opportunities page is meant for job offers, as an exmaple. This is why opportunity posts lead to an external link that gives more information about the opportunity.


More specific implementations:

1. Image display
We handled showing the user images by first checking if the user has uploaded an image. If no image is present, a default avatar image URL is assigned. Alternatively, if the user has uploaded an image, the code converts the image bytes to a base64-encoded string and constructs a data URI scheme, creating a valid image URL. This approach enables dynamic rendering of user profile images, showing a default avatar when no image is available and the user's uploaded image otherwise. This is why we inserted an image field in the user table that has a type TEXT.

2. Registration
The `register` function in the Flask application handles both GET and POST requests for user registration. It retrieves country and college information for user selection on the registration page. When receiving a POST request, the function validates form data, ensuring all required fields are filled, checking for username uniqueness, and enforcing password strength criteria. If validation is successful, the function hashes the password and inserts user data into the 'user' table. Subsequently, it fetches the user ID and uses it to insert entries into 'profile_questions' and 'socials' tables. After a successful registration, the user is redirected to the login page. The GET request renders the registration template with country and college options for selection. Overall, the implementation ensures secure registration with password hashing and additional user-related information storage in separate tables.
