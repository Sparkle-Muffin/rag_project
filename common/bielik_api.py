import subprocess


def call_model(prompt):
	command = ("docker exec -it ollama ollama run Bielik-11B-v2_6-Instruct_Q4_K_M " + prompt)
	subprocess.run(command, shell=True, check=True, text=True)
