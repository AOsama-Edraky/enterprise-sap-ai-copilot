.PHONY: test eval demo serve check
test:
	python3 -m unittest discover -s tests -v
eval:
	python3 -m copilot eval
demo:
	python3 -m copilot demo
serve:
	python3 -m copilot serve
check: test eval
