default:
	git submodule update
	./setup_tensorflow.sh

clean:
	rm -f `find . -name "*.pyc" ! -path "./venv/*"`
	rm -f *.log network/*.log
