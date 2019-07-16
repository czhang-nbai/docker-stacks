FROM orion/tensorflow-notebook-final

USER root

ADD . /home/$NB_USER/tmp/jupyterlab-converter
RUN conda install --quiet --yes \
    'nbconvert' \
    'flask-login' \
    'wtforms'
RUN  conda install -c conda-forge --quiet --yes \
    'pipreqs' \
    'flask-socketio'
RUN  conda clean --all -f -y
#    fix-permissions $CONDA_DIR && \
#    fix-permissions /home/$NB_USER && \
RUN npm cache clean --force && \
    chown -R $NB_USER:$NB_GID /home/$NB_USER/tmp && \
    chown -R $NB_USER:$NB_GID /opt/conda/share/jupyter/lab && \
    chmod -R 775 /opt/conda/share/jupyter/lab && \
    chmod -R 775 /home/$NB_USER/tmp  && \
    cp -R /home/$NB_USER/tmp/jupyterlab-converter/NBAIConverter /usr && \
    chown -R $NB_USER:$NB_GID /usr/NBAIConverter && \
    chmod -R 775 /usr/NBAIConverter

USER $NB_UID

RUN cd /home/$NB_USER/tmp/jupyterlab-converter/jplab-extensions/jupyterlab-enhanced && \
    npm install && \
    npm run build && \
    jupyter labextension install . && \
    cd /home/$NB_USER/tmp/jupyterlab-converter/jplab-extensions/jupyterlab-runall && \
    npm install && \
    npm run build && \
    jupyter labextension install . && \
    rm -rf /home/$NB_USER/tmp/jupyterlab-converter
