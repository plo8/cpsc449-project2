PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS "userData";
CREATE TABLE IF NOT EXISTS "userData" (	
	"username"	TEXT UNIQUE CHECK(username != '' OR username!= null),
	"password"	TEXT CHECK(username != '' OR username!= null),
	PRIMARY KEY("username")
);
COMMIT;