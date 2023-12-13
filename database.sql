-- college entity to store all the colleges (in our case only top 20) that people might be affiliated to
CREATE TABLE
  college (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL
  );

-- index on college name because searches in the connect page will be performed based on the name
CREATE INDEX idx_college_name ON college (name);

-- like entity to know if the user liked the profile and which posts he liked
CREATE TABLE
  post_like (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES post (id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES USER (id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (post_id, user_id)
  );

-- comment entity to store all the comments written by the user to a specific post
CREATE TABLE
  post_comment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    post_id INTEGER NOT NULL REFERENCES post (id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES USER (id) ON DELETE CASCADE
  );

-- post entity to store the relevant information upon creation, and extract for the feed
CREATE TABLE
  post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caption TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL REFERENCES USER (id) ON DELETE CASCADE,
    image TEXT (255),
    likes INTEGER DEFAULT 0
  );

-- opportunity entity to store all the information about opportunities
CREATE TABLE
  opportunity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    linked_application VARCHAR(120) NOT NULL,
    deadline DATE NOT NULL
  );

-- country entity to store all the countries and to be able to load them so that the user can choose one of them
CREATE TABLE
  country (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL CHECK (
      name IN (
        'Bosnia and Herzegovina',
        'Croatia',
        'North Macedonia',
        'Montenegro',
        'Serbia',
        'Slovenia',
        'Yugoslavia'
      )
    )
  );

-- user table that stores important user info, password, email,
-- the country of origin and affiliated universit
CREATE TABLE
  USER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(120) UNIQUE NOT NULL,
    fname VARCHAR(65) NOT NULL,
    lname VARCHAR(65) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    image TEXT (255),
    country_id INTEGER NOT NULL REFERENCES country (id) ON DELETE CASCADE,
    college_id INTEGER NOT NULL REFERENCES college (id) ON DELETE CASCADE,
    location VARCHAR(100) DEFAULT '',
    bio VARCHAR(150) DEFAULT ''
  );

-- socials entity to store all the linked social media acoounts or usernames for other social media
CREATE TABLE
  socials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instagram VARCHAR(100) NOT NULL DEFAULT '',
    facebook VARCHAR(100) NOT NULL DEFAULT '',
    linkedin VARCHAR(120) NOT NULL DEFAULT '',
    user_id INTEGER UNIQUE NOT NULL REFERENCES USER (id) ON DELETE CASCADE
  );

-- profile_questions entity that stores the answers to predetermined questions and links them to a specific user
CREATE TABLE
  profile_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    answer1 TEXT NOT NULL DEFAULT '',
    answer2 TEXT NOT NULL DEFAULT '',
    answer3 TEXT NOT NULL DEFAULT '',
    user_id INTEGER UNIQUE NOT NULL REFERENCES USER (id) ON DELETE CASCADE
  );

-- event table to be able to create events, store the dat, description and location
CREATE TABLE
  event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    DATE DATE NOT NULL,
    location VARCHAR(100) NOT NULL
  );

-- fill the country entity with the 6 Yugoslav countries and the 7 option Yugoslavia for older generations
INSERT INTO
  country (name)
VALUES
  ('Bosnia and Herzegovina'),
  ('Croatia'),
  ('North Macedonia'),
  ('Montenegro'),
  ('Serbia'),
  ('Slovenia'),
  ('Yugoslavia');

-- insert all the univeristy names to be able to load them as options for the user
INSERT INTO
  college (name, state)
VALUES
  ('Harvard University', 'MA'),
  ('Stanford University', 'CA'),
  (
    'Massachusetts Institute of Technology (MIT)',
    'MA'
  ),
  (
    'California Institute of Technology (Caltech)',
    'CA'
  ),
  ('Princeton University', 'NJ'),
  ('Yale University', 'CT'),
  ('Columbia University', 'NY'),
  ('University of Chicago', 'IL'),
  ('University of Pennsylvania', 'PA'),
  ('Northwestern University', 'IL'),
  ('Johns Hopkins University', 'MD'),
  ('Duke University', 'NC'),
  ('University of Michigan - Ann Arbor', 'MI'),
  ('University of California - Berkeley', 'CA'),
  (
    'University of California - Los Angeles (UCLA)',
    'CA'
  ),
  ('New York University (NYU)', 'NY'),
  ('University of Virginia', 'VA'),
  (
    'University of North Carolina at Chapel Hill',
    'NC'
  ),
  ('University of Southern California (USC)', 'CA'),
  ('Carnegie Mellon University', 'PA');