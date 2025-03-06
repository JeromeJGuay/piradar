from pathlib import Path
import subprocess
import os


# Directory containing the C++ source code
cpp_directory = "./cpp"

built_directory = "./cpp_built"

# List all .cpp files in the directory
cpp_files = [os.path.join(cpp_directory, f) for f in os.listdir(cpp_directory) if f.endswith(".cpp")]

# Compile the C++ code
compile_command = ["g++", "-o", built_directory] + cpp_files

Path(built_directory).mkdir(exist_ok=True)

subprocess.run(compile_command, check=True)

# Run the compiled executable
run_command = [built_directory]
result = subprocess.run(run_command, capture_output=True, text=True)

# Print the output of the C++ code
print(result.stdout)