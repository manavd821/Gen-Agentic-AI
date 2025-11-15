import io
import sys

# old_output = sys.stdout
# old_input = sys.stdin
# var = input("Write name: ")
# sys.stdout = open("myfile.txt", "w")
# print(var)
# sys.stdin = open("myfile.txt", "r")
# var = input()
# sys.stdout = old_output
# sys.stdin = old_input
# print(var)

# task 1
std_output = sys.stdout
buffer = io.StringIO()
sys.stdout = buffer
print("My name is Manav.")
sys.stdout = std_output
print(f"{buffer.getvalue()=}")

# task 2
std_input = sys.stdin
buffer = io.StringIO(initial_value="Namste, mera name manav hai bhai")
sys.stdin = buffer
print(f"{input()=}")
sys.stdin = std_input

# task 3
fake_args = ["file.py", "hello", "manav", "123"]
sys.argv = fake_args
print(sys.argv)   
print(sys.argv[1:])  

# task 4
# sys.path.append('mylib')
# import hello
# print(sys.path)
# print(hello.greet())