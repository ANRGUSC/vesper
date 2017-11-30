default:

clean:
	rm -f `find . -name "*.pyc" ! -path "./venv/*"`
