import subprocess


def run_bielik():
    command = ("docker exec -it ollama ollama run Bielik-11B-v2_6-Instruct_Q4_K_M")
    subprocess.run(command, shell=True, check=True, text=True)