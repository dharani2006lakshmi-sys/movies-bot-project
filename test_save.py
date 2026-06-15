import subprocess

url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
subprocess.run(["python", "-m", "spotdl", "save", url, "--save-file", "test.spotdl"])

with open("test.spotdl", "r") as f:
    data = f.read()
    print("Length of file:", len(data))
    # see what it looks like
    print(data[:500])
