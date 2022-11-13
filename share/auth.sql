PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS "userData";
CREATE TABLE IF NOT EXISTS "userData" (	
	"username"	TEXT UNIQUE NOT NULL,
	"password"	TEXT,
	PRIMARY KEY("username")
);
COMMIT;