import subprocess

def execute_cmd(command):
    # Run the command and capture the output and error
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    
    # Get the standard output
    stdout = result.stdout
    # Get the standard error
    stderr = result.stderr
    # Get the return code
    return_code = result.returncode

    print("Standard Output:\n", stdout)
    print("Standard Error:\n", stderr)
    print("Return Code:\n", return_code)
    
    return stdout, stderr, return_code


if __name__ == "__main__":
    # Define the command to execute
    command = "ls -l"
    
    # Execute the command
    execute_cmd(command)


if __name__ == "__main__":
    # Example usage
    # command = "ls -l"

    command = "pip install numpy"

    stdout, stderr, return_code = execute_cmd(command)

    env_cmd = "pip install -r requirements.txt"
    # env_stdout = runner(env_cmd)
    env_stdout, env_stderr, env_return_code = execute_cmd(env_cmd)

    demo1_cmd = "python3 demo.py -f examples/inputs/emma.jpg --onnx # -o [2d_sparse, 2d_dense, 3d, depth, pncc, pose, uv_tex, ply, obj]"
    demo1_stdout, demo1_stderr, demo1_return_code = execute_cmd(demo1_cmd)

    # python3 demo_video.py -f examples/inputs/videos/214.avi --onnx
    demo2_cmd = "python3 demo_video.py -f examples/inputs/videos/214.avi --onnx"
    demo2_stdout, demo2_stderr, demo2_return_code = execute_cmd(demo2_cmd)

    # python3 demo_video_smooth.py -f examples/inputs/videos/214.avi --onnx
    demo3_cmd = "python3 demo_video_smooth.py -f examples/inputs/videos/214.avi --onnx"
    demo3_stdout, demo3_stderr, demo3_return_code = execute_cmd(demo3_cmd)

    # python3 demo_webcam_smooth.py --onnx
    demo4_cmd = "python3 demo_webcam_smooth.py --onnx"
    demo4_stdout, demo4_stderr, demo4_return_code = execute_cmd(demo4_cmd)