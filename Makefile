install:
	python -m virtualenv --python python2.7 venv
#	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && python setup.py develop

clean:
	rm -rf .tox .Python bin .cache include lib man iam_reporter.egg-info pip-selfcheck.json
