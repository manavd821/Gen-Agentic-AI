import subprocess

# task 1
# subprocess.run('dir', shell=True)
# subprocess.run('ls', shell=True)

# # task 2
subprocess.run("g++ add.cpp -o add", check=True)
res = subprocess.run(["./add.exe"], capture_output=True, text=True)
print(res.stdout)

# task 3
subprocess.run("g++ hello_world.cpp -o hello_world",check=True)
result = subprocess.run(["./hello_world.exe"], input="Manav",text=True, capture_output=True)
print(result.stdout)

# task 4 and 5, can you do it chatgpt!