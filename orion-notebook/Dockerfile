FROM orion/tensorflow-notebook

# make changes on images created from official dockerfile
# 1. delete folder /home/jovyan/work
# 2. create folder /home/jovyan/sync
# 3. copy template files to /home/jovyan/sync/templates
# 4. make sync folder owned by a user
# 5. make template folder read-only
# 6. change user to root
# 7. replace config file with customized configfile
# 8. add required file for IFrame

# 6. change user to root
USER root

RUN conda install --quiet --yes \
    'conda-forge::pipreqs' \
    'nbconvert' && \
    conda clean --all -f -y && \
    jupyter labextension install @jupyterlab/google-drive

# 2. create folder /home/jovyan/sync
# 3. copy template files to /home/jovyan/sync/template
COPY template /home/$NB_USER/sync/templates

RUN \
# 1. delete folder /home/jovyan/work
    rm -r /home/$NB_USER/work && \
# 4. make sync folder owned by a user
    chown -R $NB_USER:$NB_GID /home/$NB_USER/sync && \
# 5. make template folder read-only
    chmod 500 /home/$NB_USER/sync/templates && \
    chmod 400 /home/$NB_USER/sync/templates/*

# 7. replace config file with customized configfile
COPY jupyter_notebook_config.py /etc/jupyter/

# 8. add required file for IFrame
COPY custom /etc/jupyter/custom