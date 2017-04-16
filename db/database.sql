CREATE TABLE file (
	file_id INTEGER PRIMARY KEY AUTOINCREMENT,
	file_type VARCHAR(13),
	file_name VARCHAR(255),
	file_path VARCHAR(255),
	date_added NOT NULL DEFAULT CURRENT_TIMESTAMP,
	file_data VARCHAR,
	file_size INTEGER
);

CREATE TABLE keyword (
	keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
	file_id INTEGER,
	keyword VARCHAR(255),
	count INTEGER,
	FOREIGN KEY (file_id) REFERENCES file(file_id)
);