.PHONY: test
test:
	flake8 --config=.flake8
	coverage erase
	coverage run \
		--source=submitify,submitify,usermgmt_standalone \
		--omit='*migrations*,*urls.py,*apps.py,*admin.py,*__init__.py,*test*.py' \
		manage.py test --verbosity=2
	coverage report -m --skip-covered
