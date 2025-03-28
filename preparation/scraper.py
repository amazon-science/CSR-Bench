# AI ML Topics Scraper
import requests
import json
import time
import os
from joblib import Parallel, delayed
import zipfile

NAME = 'gsr-bench'

def fetch_data(name, per_page=50):
    def get_repos_by_category(category, sort='stars', order='desc'):
        url = f"https://api.github.com/search/repositories?q=topic:{category}&sort={sort}&order={order}&per_page={per_page}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['items']
        else:
            print("Failed to retrieve data:", response.status_code)

    categories = {
        "AI": ["IJCAI", "AAAI"],
        "ML": ["ICLR", "ICML", "NeurIPS"],
        "NLP": ["ACL", "EMNLP", "NAACL"],
        "CV": ["CVPR", "ICCV", "ECCV"],
        "DM": ["SIGKDD", "ICDM", "CIKM", "WSDM"],
        "Robotics": ["ICRA", "IROS"], # "CoRL"
    }

    repo_data = {}
    for category, subcategories in categories.items():
        for subcategory in subcategories:
            key = f"{category}_{subcategory}"
            repo_data[key] = get_repos_by_category(subcategory)
            time.sleep(5)

    repo_data = {k: v for k, v in repo_data.items() if v is not None}

    # Save the repo data to a JSON file
    with open(f'./data/{name}_meta_data.json', 'w') as f:
        json.dump(repo_data, f, indent=4)

# Example usage
# fetch_data(NAME, per_page=200)


def download_repo_zip(name, max_repo=200, n_jobs=4):
    def download_and_unzip_repo(repo, category_path):
        full_name = repo['full_name']
        default_branch = repo['default_branch']
        save_path = os.path.join(category_path, f"{repo['full_name'].split('/')[-1]}.zip")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        if not os.path.exists(save_path):
            zip_url = f"https://github.com/{full_name}/archive/refs/heads/{default_branch}.zip"
            response = requests.get(zip_url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=256):
                        file.write(chunk)
                print(f"Downloaded {full_name} to {save_path}.")
            else:
                print(f"Failed to download {full_name}. Status code: {response.status_code}")
                return  # Exit if download fails

        unzip_directory = os.path.dirname(save_path)
        # Skip if the repository has already been unzipped
        if os.path.exists(os.path.join(unzip_directory, full_name.split('/')[-1])):
            print(f"{full_name} has already been unzipped.")
            return

        repo_name = full_name.split('/')[-1]
        target_dir = os.path.join(unzip_directory, repo_name)
        
        try:
            with zipfile.ZipFile(save_path, 'r') as zip_ref:
                os.makedirs(target_dir, exist_ok=True)
                zip_ref.extractall(target_dir)
            print(f"Unzipped {save_path} into {target_dir}.")
            json.dump(repo, open(os.path.join(target_dir, 'meta.json'), 'w'), indent=4)

        except zipfile.BadZipFile:
            print(f"Bad zip file: {save_path}")
    
    def download_repos_by_category(data, max_repo=max_repo, n_jobs=n_jobs):
        for category, repos in data.items():
            print(f"Processing category: {category}")
            category_path = os.path.join(f'./data/{name}/', category)
            tasks = (delayed(download_and_unzip_repo)(repo, category_path) for repo in repos[:max_repo])
            Parallel(n_jobs=n_jobs)(tasks)

    data = json.load(open(f'./data/{name}_meta_data.json', 'r'))
    download_repos_by_category(data)

# Example usage
# download_repo_zip(NAME, max_repo=200, n_jobs=4)
