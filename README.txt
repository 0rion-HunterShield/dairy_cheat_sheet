scan barcodes into csv file at work using 'barcode to sheet'
	fields are:
		"barcode","name",price"

import csv data into 'sqlite Master Pro' using table name format 'dairy products {section}'
	-due to comma at end of each line tables must have 1 extracolumn at end

upload Dairy.db file to google drive 'data sheets' folder
download file from google drive onto pc

run `python manage.py runserver`

run `curl 127.0.0.1:8000/uploader/{section}/ -H "Content-Type: Application/Octet-Stream" --upload-file {path_to_db_file.db}` 
