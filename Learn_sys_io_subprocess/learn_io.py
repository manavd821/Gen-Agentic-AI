import io

# task 1
buffer = io.StringIO()
print("Hello from buffer", file=buffer)
print(buffer.getvalue())

# task 2
buffer = io.StringIO(initial_value="""
What you’ll learn: reading from an in-memory stream like a file
Put a long string into StringIO.
Use .read() and .readline() like you would with a real file.
""")
print(f"{buffer.read()=}")
buffer.seek(0)
print(f"{buffer.readlines()=}")
print(f"{buffer.getvalue()=}")

# task 3
buffer = io.StringIO()
user_input = input("Write Name:")
buffer.write(user_input)
print(f"{buffer.getvalue()=}")