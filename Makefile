# cause im lazy
run:
	cd src; python3 main.py
clean:
	find . | grep -E '(__pycache__|\.pyc|\.pyo$|\.DS_Store)' | xargs rm -rf