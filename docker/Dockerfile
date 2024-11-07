FROM python:3.13

COPY dist /dist
RUN pip install /dist/*.whl

# Command to run the server
CMD ["python", "-m", "alpha_motion"]
