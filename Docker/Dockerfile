FROM bioconductor/bioconductor_docker
 
RUN apt-get update && apt-get install -y \
    libxml2-dev libcurl4-openssl-dev libssl-dev libpng-dev libjpeg-dev libfontconfig1-dev \
    && R -e "install.packages('tidyverse', repos='https://cloud.r-project.org')"

#install essential apps
RUN apt-get update
RUN apt-get -y install wget git git-lfs vim


# install required R libraries
RUN R -e "install.packages('igraph',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('BiocManager',dependencies=TRUE, repos='http://cran.rstudio.com/')"

RUN R -e "BiocManager::install(ask = F)" 
RUN R -e "BiocManager::install('HelloRanges', dependencies=TRUE,force=TRUE)"

#install Medalt
RUN mkdir /medalt_home
WORKDIR /medalt_home

RUN git clone https://github.com/KCHEN-lab/MEDALT.git

RUN apt-get update && apt-get install -y wget build-essential \
 && wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz \
 && tar xzf Python-2.7.18.tgz \
 && cd Python-2.7.18 && ./configure && make altinstall \
 && ln -s /usr/local/bin/python2.7 /usr/bin/python

#RUN ln -s /usr/bin/python2.7 /usr/bin/python
#RUN ln -s /usr/bin/python3 /usr/bin/python



