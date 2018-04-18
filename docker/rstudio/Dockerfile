FROM rocker/rstudio:3.3.3

RUN sudo apt-get update && \
    sudo apt-get install -y --no-install-recommends libjpeg-dev libpng-dev && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

RUN R -e 'install.packages("devtools")'

RUN R -e 'library(devtools); \
          install_version("ggplot2", "2.2.1", repos = "http://cran.us.r-project.org");'

RUN R -e 'library(devtools); \
          install_version("dplyr", "0.7.4", repos = "http://cran.us.r-project.org");'

RUN R -e 'library(devtools); \
          install_version("tidyr", "0.8.0", repos = "http://cran.us.r-project.org");'

RUN R -e 'library(devtools); \
          install_version("data.table", "1.10.4-3", repos = "http://cran.us.r-project.org");'

RUN R -e 'library(devtools); \ 
          install_version("shiny", "1.0.5", repos = "http://cran.us.r-project.org");'

RUN R -e 'library(devtools); \
          install_version("vcd", "1.4-4", repos = "http://cran.us.r-project.org");'
          
RUN R -e 'library(devtools); \
          install_version("ggmap", "2.6.1", repos = "http://cran.us.r-project.org");'

