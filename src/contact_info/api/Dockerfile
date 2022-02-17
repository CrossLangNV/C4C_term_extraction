# Reuse dockerfile
FROM python_contact_info

COPY main.py /work

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1234"]
