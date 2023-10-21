FROM public.ecr.aws/lambda/python:3.11

ARG MODEL_NAME
ENV MODEL_NAME=$MODEL_NAME

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt --extra-index-url=https://download.pytorch.org/whl/cpu

# Copy function code
COPY models/${MODEL_NAME} ${LAMBDA_TASK_ROOT}/${MODEL_NAME}
COPY service.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "service.handler" ]