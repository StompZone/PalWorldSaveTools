import requests, subprocess, os, zipfile
def download_from_github(repo_owner, repo_name, version, file_name, download_path):
    url = f"https://github.com/{repo_owner}/{repo_name}/releases/download/{version}/{file_name}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(f"{download_path}/{file_name}", "wb") as f:
            for chunk in response.iter_content(1024): f.write(chunk)
        print(f"File '{file_name}' downloaded successfully to '{download_path}'")
    else: print(f"Error downloading file: {response.status_code}")
def extract_zip(directory, partial_name, extract_to):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip') and partial_name in file:
                with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref: zip_ref.extractall(extract_to)
                print(f"Extracted {file} to {extract_to}")
def main():
    file_path, download_file = "psp_windows/psp.exe", ""
    if os.path.exists(file_path): print("Opening Palworld Save Pal..."), os.chdir("psp_windows"), subprocess.Popen("psp.exe")
    else:
        response = requests.get("https://github.com/oMaN-Rod/palworld-save-pal/releases/latest")
        version = response.url.split("/").pop().replace('v', '')
        download_file = f"psp-windows-{version}.zip"
        print("Downloading Palworld Save Pal...")
        download_from_github("oMaN-Rod", "palworld-save-pal", f"v{version}", download_file, ".")
        extract_zip(".", "psp-windows", "psp_windows")
        os.remove(download_file)
        if os.path.exists(file_path): print("Opening Palworld Save Pal..."), os.chdir("psp_windows"), subprocess.Popen("psp.exe")
        else: print("Failed to download Palworld Save Pal...")
if __name__ == "__main__": main()