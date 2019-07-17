CREATE DATABASE pa1;
USE pa1;
DROP TABLE Photos CASCADE; 
DROP TABLE Users CASCADE;
DROP TABLE Albums CASCADE;
DROP TABLE Friends CASCADE;
DROP TABLE Tags CASCADE;
DROP TABLE Comments CASCADE;
DROP TABLE CommentInPhoto CASCADE;
DROP TABLE TagInPhoto CASCADE;
DROP TABLE AlbumOwnerUser CASCADE;
DROP TABLE PhotoInAlbum CASCADE;


CREATE TABLE Users (
    user_id         integer       NOT NULL,
    email           varchar(255)  NOT NULL,
    password        varchar(255)  NOT NULL,
    firstName       varchar(255)  NOT NULL,
    lastName        varchar(255)  NOT NULL,
    birthday        varchar(255)  NOT NULL,
    gender          varchar(255)  NOT NULL,
    hometown        varchar(255)  NOT NULL,
    bio             varchar(255),
    pPic        longblob,
    PRIMARY KEY (user_id)
);
CREATE TABLE Albums (
  #might need to assume that within a users' album the album name has to be unique 
    album_id       integer       NOT NULL,
    album_name     varchar(255)  NOT NULL,
    user_id       integer       NOT NULL,
    creationDate  varchar(255)  NOT NULL,
    PRIMARY KEY (album_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
  );

#SELECT * FROM Users INNER JOIN (SELECT friend_id FROM Friends WHERE user_id = 1) as test ON Users.user_id = test.friend_id;
CREATE TABLE Photos
(
  picture_id integer NOT NULL,
  album_id integer NOT NULL,
  user_id integer NOT NULL,
  imgdata longblob ,
  caption VARCHAR(255),
  PRIMARY KEY (picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);


#INSERT INTO Comments (comment_id, user_id, commentDate, commentData) VALUES (1, 1, "1996/12/23", "TEST");
#INSERT INTO CommentInPhoto (picture_id, comment_id) VALUES (1,1);
  CREATE TABLE Tags (
    tag_id     integer       NOT NULL, #unique
    tag_name   varchar(255)  NOT NULL, #unique 
    tag_count  integer       NOT NULL,
    PRIMARY KEY (tag_id)
  );

    CREATE TABLE Comments (
    comment_id       integer       NOT NULL,
    name           varchar(255)       NOT NULL,
    commentDate     varchar(255)  NOT NULL, 
    commentData     varchar(255)  NOT NULL,
    PRIMARY KEY (comment_id)
  );
-- INSERT INTO Users (user_id, firstName, lastName, email, password, birthday, gender, hometown, bio) 
-- VALUES (1,"Tom", "Kang", "tom851223@gmail.com", "3333", "1996/12/23", "male", "Taipei", NULL);

-- INSERT INTO Users (user_id, firstName, lastName, email, password, birthday, gender, hometown, bio) 
-- VALUES (2,"Chris", "Kang", "fat60221@bu.edu", "3333", "1994/12/23", "male", "Taipei", NULL);

-- INSERT INTO Users (user_id, firstName, lastName, email, password, birthday, gender, hometown, bio) 
-- VALUES (3,"Wenyen", "Kang", "agl60221@bu.edu", "3333", "1995/12/23", "male", "Taipei", NULL);


CREATE TABLE Friends (
    user_id    integer   NOT NULL,
    friend_id  integer   NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT friendsPK PRIMARY KEY (user_id, friend_id)
  );

-- INSERT INTO Friends (user_id, friend_id) VALUES (1,2);
-- INSERT INTO Friends (user_id, friend_id) VALUES (2,1);
-- INSERT INTO Friends (user_id, friend_id) VALUES (2,3);
-- INSERT INTO Friends (user_id, friend_id) VALUES (3,2);
-- INSERT INTO Friends (user_id, friend_id) VALUES (1,3);
-- INSERT INTO Friends (user_id, friend_id) VALUES (3,1);


CREATE TABLE LikeInPhoto(
picture_id   integer   NOT NULL,
user_id    integer   NOT NULL,
FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
FOREIGN KEY (picture_id) REFERENCES Photos(picture_id) ON DELETE CASCADE,
CONSTRAINT likePK PRIMARY KEY (picture_id, user_id)
);

  CREATE TABLE TagInPhoto (
    picture_id   integer   NOT NULL,
    tag_id   integer   NOT NULL, 
    FOREIGN KEY (picture_id) REFERENCES Photos(picture_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tags(tag_id) ,
    CONSTRAINT taginphotoPK PRIMARY KEY (picture_id, tag_id)
  );

CREATE TABLE CommentInPhoto (
    picture_id   integer   NOT NULL,
    comment_id   integer   NOT NULL,
    FOREIGN KEY (picture_id) REFERENCES Photos(picture_id) ON DELETE CASCADE,
    FOREIGN KEY (comment_id) REFERENCES Comments(comment_id),
    CONSTRAINT commentinphotoPK PRIMARY KEY (picture_id, comment_id)
  );

CREATE TABLE AlbumOwnerUser (
    user_id    integer   NOT NULL,
    album_id   integer   NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    CONSTRAINT albumowneruserPK PRIMARY KEY (user_id, album_id)
  );



-- CREATE TABLE PhotoInAlbum (
--     album_id    integer   NOT NULL,
--     picture_id      integer   NOT NULL,
--     FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
--     FOREIGN KEY (picture_id) REFERENCES Photos(picture_id),
--     CONSTRAINT picinalbumPK PRIMARY KEY (album_id, picture_id)
--   );
