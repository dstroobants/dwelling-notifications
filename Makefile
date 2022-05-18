dev:
	docker-compose down
	docker system prune
	docker build -t dwellings:latest .
	docker-compose up --force-recreate

run:
	docker build -t dwellings:latest .
	docker-compose up --force-recreate

logs-script:
	sudo cat $(shell docker inspect --format='{{.LogPath}}' dwellings_script_1)

logs-db:
	sudo cat $(shell docker inspect --format='{{.LogPath}}' dwellings-db_1) 
