import requests
import json
from urllib.parse import urlparse
import time


# Function to fetch issues from a GitHub repository
def fetch_github_issues(repo_owner, repo_name, state='closed', per_page=100):
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        params = {
            'state': state,
            'per_page': per_page,
            'page': page
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch issues: {response.status_code}")
            break
        
        page_issues = response.json()
        if not page_issues:
            break
        
        for issue in page_issues:
            # Fetch comments for each issue
            comments_url = issue['comments_url']
            comments_response = requests.get(comments_url)
            if comments_response.status_code == 200:
                issue['comments'] = comments_response.json()
            else:
                issue['comments'] = []

        page_issues = [issue for issue in page_issues if 'issues' in issue['html_url']]
        issues.extend(page_issues)
        page += 1
    
    return issues

# Function to parse repository owner and name from URL
def parse_repo_url(repo_url):
    path_parts = urlparse(repo_url).path.strip('/').split('/')
    if len(path_parts) >= 2:
        repo_owner = path_parts[0]
        repo_name = path_parts[1]
        return repo_owner, repo_name
    else:
        raise ValueError("Invalid GitHub repository URL")

# Main function to run the script
def main(repo_url):
    try:
        repo_owner, repo_name = parse_repo_url(repo_url)
        issues = fetch_github_issues(repo_owner, repo_name)
        
        # Save issues to a JSON file named after the repository
        file_name = f"./assets/{repo_name}.json"
        with open(file_name, 'w') as f:
            json.dump(issues, f, indent=4)
        
        print(f"Fetched {len(issues)} closed issues from {repo_owner}/{repo_name} and saved to {file_name}")
    
    except ValueError as e:
        print(e)

    time.sleep(15)


# Example usage
if __name__ == "__main__":
    # Demo scraper
    repo_url = "https://github.com/facebookresearch/contriever"
    main(repo_url)

    data = open('/home/yijia/git-bench/data/meta/GSRBench100.txt', 'r').readlines()
    for item in data:
        main(item.strip())
