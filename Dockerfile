FROM python
RUN pip install requests
COPY . .
CMD ["python", "test-cf.py"]