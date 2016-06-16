FROM centos:7

RUN yum install -y tar wget git
RUN wget http://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo -O /etc/yum.repos.d/epel-apache-maven.repo
RUN yum install -y epel-release gcc python-devel mesos
RUN yum groupinstall -y "Development Tools"
RUN yum install -y python-devel zlib-devel libcurl-devel openssl-devel cyrus-sasl-devel cyrus-sasl-md5 apr-devel subversion-devel apr-util-devel python-setuptools
RUN easy_install pip
RUN wget http://downloads.mesosphere.io/master/centos/7/mesos-0.23.0-py2.7-linux-x86_64.egg -O /tmp/mesos-0.23.0-py2.7-linux-x86_64.egg
RUN easy_install /tmp/mesos-0.23.0-py2.7-linux-x86_64.egg
RUN pip install pycrypto

ADD make_zipapp.sh /root/make_zipapp.sh
RUN chmod +x /root/make_zipapp.sh

VOLUME ["/opt/build"]

CMD ["/root/make_zipapp.sh"]
