default:

clean:
	rm -f `find . -name "*.pyc" ! -path "./venv/*"`
	rm -f *.log network/*.log
