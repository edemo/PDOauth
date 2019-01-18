FROM ubuntu:bionic
RUN apt-get -y update
RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y upgrade
RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y install python3 make python3-pip openjdk-11-jre\
    curl docbook-xsl apache2 swig libffi-dev\
    libnss3-tools unzip\
    git python3-dev libssl-dev xvfb postgresql python3-psycopg2\
    python3-pykcs11 libsofthsm2 python3-coverage wget firefox \
    software-properties-common vnc4server opensc sudo \
    python3-lxml chromium-chromedriver apache2-dev \
    fvwm vim python libapache2-mod-wsgi python-crypto\
    syslog-ng-core python-pydoctor python-sourcecodegen python-pip
RUN service postgresql start &&\
    sudo -u postgres createuser root &&\
    sudo -u postgres createdb root -O root&&\
    service postgresql stop
RUN pip3 install Flask Flask-Login Flask-Mail Flask-Migrate Flask-SQLAlchemy Flask-Script \
    Flask-WTF SQLAlchemy beautifulsoup4 pyoauth2-shift selenium pyOpenSSL uritools \
    mod_wsgi enforce polib
RUN pip install vnc2flv j2cli

RUN ln -s /usr/local/lib/python3.5/dist-packages/mod_wsgi/server/mod_wsgi-*.so /usr/lib/apache2/modules/mod_wsgi_py3.so

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz &&\
    cd /usr/local/bin&&\
    tar xvzf /tmp/geckodriver.tar.gz &&\
    rm -f /tmp/geckodriver.tar.gz
RUN sed -i 's/peer/trust/' /etc/postgresql/*/main/pg_hba.conf
RUN cd /usr/local/lib &&\
    wget -q http://downloads.sourceforge.net/project/saxon/Saxon-HE/9.4/SaxonHE9-4-0-2J.zip &&\
    unzip SaxonHE9-4-0-2J.zip &&\
    rm -f SaxonHE9-4-0-2J.zip 
RUN curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
RUN apt-get -y install nodejs

RUN npm install -g rollup jsdom qunit-cli
RUN mkdir -p /dependencies/javascript
RUN curl http://code.jquery.com/qunit/qunit-1.18.0.js -o /dependencies/javascript/qunit-1.18.0.js
RUN curl http://code.jquery.com/qunit/qunit-1.18.0.css -o /dependencies/javascript/qunit-1.18.0.css
RUN curl https://raw.githubusercontent.com/JamesMGreene/qunit-reporter-junit/master/qunit-reporter-junit.js -o /dependencies/javascript/qunit-reporter-junit.js
RUN curl https://raw.githubusercontent.com/alex-seville/blanket/89266afe70ea733592f5d51f213657d98e19fc0a/dist/qunit/blanket.js -o /dependencies/javascript/blanket.min.js
RUN curl https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css -o /dependencies/javascript/bootstrap.min.css
RUN curl https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js -o /dependencies/javascript/bootstrap.min.js
RUN curl https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js -o /dependencies/javascript/jquery.min.js

ADD src/end2endtest/certs.JSON /etc/chromium-browser/policies/managed/certs.json
ADD src/end2endtest/certs.JSON /etc/opt/chrome/policies/managed/certs.json

CMD /bin/bash


