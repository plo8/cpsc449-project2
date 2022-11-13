PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS "userData";
CREATE TABLE IF NOT EXISTS "userData" (	
	"username"	TEXT UNIQUE CHECK(length(username)>0 OR username!= null),
	"password"	TEXT CHECK(length(password)>0 OR password!= null),
	PRIMARY KEY("username")
);
COMMIT;