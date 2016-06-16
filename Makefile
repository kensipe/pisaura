sdist:
	python setup.py sdist

build_zip_centos7: sdist
	mv dist/*.tar.gz builds/centos7 && rm -rf *.egg-info dist && \
	cd builds/centos7 && \
	docker build -t centos7_build_env . && \
	docker ps -a -f name=centos7_build_sandbox -q | xargs -I {} docker rm {}; \
	docker run -v `pwd`:/opt/build --name centos7_build_sandbox -it centos7_build_env
	docker ps -a -f name=centos7_build_sandbox -q | xargs -I {} docker rm {}; \
	rm builds/centos7/*.tar.gz

centos7_sandbox: build_zip_centos7
	docker ps -a -f name=centos7_build_sandbox -q | xargs -I {} docker rm {}; \
	docker run -v `pwd`:/opt/build --name centos7_build_sandbox -it centos7_build_env /bin/bash; \
	docker ps -a -f name=centos7_build_sandbox -q | xargs -I {} docker rm {}
