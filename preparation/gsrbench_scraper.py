import os
import requests
import zipfile
import io
import json
import shutil
import time

def get_repo_metadata(user_repo):
    api_url = f"https://api.github.com/repos/{user_repo}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"Repository not found: {user_repo}")
    elif response.status_code == 403:
        print(f"Rate limit exceeded for {user_repo}. Please try again later.")
    else:
        print(f"Failed to get metadata for {user_repo}. HTTP Status Code: {response.status_code}")
    
    return None

def download_and_extract_zip(url, extract_to):
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            temp_dir = extract_to + "_temp"
            z.extractall(temp_dir)
            
            # Move files from temp_dir to extract_to
            for item in os.listdir(temp_dir):
                s = os.path.join(temp_dir, item)
                d = os.path.join(extract_to, item)
                if os.path.isdir(s):
                    for sub_item in os.listdir(s):
                        sub_s = os.path.join(s, sub_item)
                        sub_d = os.path.join(extract_to, sub_item)
                        shutil.move(sub_s, sub_d)
                else:
                    shutil.move(s, extract_to)
            shutil.rmtree(temp_dir)
            
        print(f"Downloaded and extracted {url} to {extract_to}")
    else:
        print(f"Failed to download {url}. HTTP Status Code: {response.status_code}")




def get_latest_commit_id(repo_url, default_branch):
    # api_url = repo_url.replace("https://github.com", "https://api.github.com/repos") + "/commits/main"
    api_url = repo_url.replace("https://github.com", "https://api.github.com/repos") + f"/commits/{default_branch}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data['sha']
    else:
        print(f"Failed to fetch commit ID for {repo_url}. HTTP Status Code: {response.status_code}")
        return None


def download_github_repos(file_path, folder):
    os.makedirs(folder, exist_ok=True)
    
    with open(file_path, 'r') as file:
        links = file.readlines()

    commit_ids = {}

    for link in links:
        link = link.strip()
        if link:
            user_repo = link.rstrip('/').replace('https://github.com/', '')
            repo_name = user_repo.split('/')[-1]
            
            metadata = get_repo_metadata(user_repo)
            if metadata:
                default_branch = metadata.get('default_branch', 'main')
                zip_url = f"https://github.com/{user_repo}/archive/refs/heads/{default_branch}.zip"
                extract_to = os.path.join(folder, repo_name)
                os.makedirs(extract_to, exist_ok=True)
                
                download_and_extract_zip(zip_url, extract_to)
                
                # Save metadata as JSON
                metadata_file_path = os.path.join(extract_to, 'metadata.json')
                with open(metadata_file_path, 'w') as json_file:
                    json.dump(metadata, json_file, indent=4)
                print(f"Saved metadata for {user_repo} to {metadata_file_path}")
            
            time.sleep(60)
            # Fetching commit IDs and storing them in a dictionary
            commit_id = get_latest_commit_id(link, default_branch)
            if commit_id:
                commit_ids[link] = (commit_id, default_branch)

            time.sleep(60)

    # Saving the dictionary as a JSON file
    with open('../data/meta/GSRBench100_commit_ids.json', 'w') as file:
        json.dump(commit_ids, file, indent=4)


# Path to the text file containing the GitHub links
file_path = '../data/meta/GSRBench100.txt'

# Target folder
folder = '../data/GSRBench100/'

download_github_repos(file_path, folder)
