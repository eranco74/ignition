all: pep8 pylint tests build

.PHONY: build pep8 pylint tests

style:
	pycodestyle --max-line-length=120 ignition tests

pylint:
	mkdir -p reports
	PYLINTHOME=reports/ pylint ignition

tests:
	py.test --cov=ignition --cov-report=term-missing tests


build:
	docker build -t eranco/extract:latest  -f Dockerfile.ignition-extract .

push:
	docker push eranco/extract:latest