FROM orion/tensorflow-notebook

USER root

RUN conda install --quiet --yes \
    'conda-forge::pipreqs' \
    'nbconvert' && \
    conda clean --all -f -y && \
    jupyter labextension install @jupyterlab/google-drive && \
    mkdir templates

COPY template /home/$NB_USER/templates

RUN chown -R $NB_USER:$NB_GID /home/$NB_USER/templates && \
    chmod 500 /home/$NB_USER/templates && \
    chmod 400 /home/$NB_USER/templates/*
