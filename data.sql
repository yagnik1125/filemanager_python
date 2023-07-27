-- For storing data first we have to create teh below table in database

CREATE TABLE USER_DATA(
    EMAIL VARCHAR2(40),
    USERNAME VARCHAR2(40),
    PASS VARCHAR2(40),
    FACE BLOB
);


-- to view the content of the talbe 

SELECT * FROM USER_DATA;
