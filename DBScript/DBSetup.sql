CREATE TABLE IF NOT EXISTS Groups (
 GroupID integer PRIMARY KEY,
 GroupName text,
 GroupType text,
 RestrictedGroup integer
);
CREATE TABLE IF NOT EXISTS Keys (
 GroupID integer,
 Token text,
 Expiry text,
 UserEmail text,
 FOREIGN KEY (GroupID) REFERENCES Groups (GroupID)
);