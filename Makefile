install:
	python -m virtualenv --python python2.7 venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && python setup.py develop

lint:
	flake8 ./ec2_patching
test:
	pytest --capture=no -vvvv tests

test-integration:
	pytest --capture=no -vvvv integration-tests

clean:
	rm -rf .tox .Python bin .cache include lib man iam_reporter.egg-info pip-selfcheck.json venv
