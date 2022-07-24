# I know this is probably not how you're supposed to use a Makefile 
# But im lazy to type out these commands so I'm doing this

# Run the API
run:
	@cd src; python3 main.py

# delete all those trash files because even though they are ignored by git IT ANNOYS ME SO MUCH
clean:
	@find . | grep -E '(__pycache__|\.pyc|\.pyo$|\.DS_Store)' | xargs rm -rf

# Test api
test:
	@cd src; uvicorn main:app --reload --host="0.0.0.0" --port=443

# Format all the files
format:
	@black ./