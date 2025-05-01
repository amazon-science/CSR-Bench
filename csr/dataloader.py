import json
import glob
from torch.utils.data import Dataset

class ReadmeDataset(Dataset):
    def __init__(self, root_dir):
        """
        Initialize the dataset by locating README files and preparing data.

        Args:
            root_dir (string): Directory with all the README.md files structured by category and repository.
        """
        self.root_dir = root_dir
        self.readme_files = []
        # Include both 'README.md' and 'readme.md'
        for pattern in ['README.md', 'readme.md']:
            # path_pattern = f'{root_dir}/*/*/*/{pattern}'
            path_pattern = f'{root_dir}/*/*/{pattern}'
            self.readme_files.extend(glob.glob(path_pattern, recursive=True))

        self.data = []
        self._prepare_data()

    def _prepare_data(self):
        """
        Prepare the dataset by reading and storing data from the file paths.
        """
        for file_path in self.readme_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    readme_content = file.readlines()
                # Load meta.json [same level as readme file]
                meta_path = file_path.replace('README.md', 'meta.json').replace('readme.md', 'meta.json')
                with open(meta_path, 'r') as file:
                    meta_data = json.load(file)

            # except UnicodeDecodeError:
            #     with open(file_path, 'r', encoding='utf-16') as file:
            #         readme_content = file.readlines()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Extract category and repo name from the path
            path_parts = file_path.split('/')
            # category = path_parts[-4]
            # repo_name = path_parts[-3]
            category = path_parts[-3]
            repo_name = path_parts[-2]
            self.data.append({
                'category': category,
                'repo_name': repo_name,
                'readme_path': file_path,
                'content': readme_content,
                'meta': meta_data
            })
        self.data = self.data

    def __len__(self):
        """
        Return the total number of samples in the dataset.
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        Fetch a single data point.
        
        Args:
            idx (int): Index of the data point to fetch.
        
        Returns:
            dict: Contains 'category', 'repo_name', and 'content' for the README.
        """
        return self.data[idx]


class LLMDataset(Dataset):
    def __init__(self, root_dir):
        """
        Initialize the dataset by locating README files and preparing data.

        Args:
            root_dir (string): Directory with all the README.md files structured by category and repository.
        """
        self.root_dir = root_dir
        self.readme_files = []
        # Include both 'README.md' and 'readme.md'
        for pattern in ['README.md', 'readme.md']:
            # path_pattern = f'{root_dir}/*/*/*/{pattern}'
            path_pattern = f'{root_dir}/*/{pattern}'
            self.readme_files.extend(glob.glob(path_pattern, recursive=True))

        self.data = []
        self._prepare_data()

    def _prepare_data(self):
        """
        Prepare the dataset by reading and storing data from the file paths.
        """
        for file_path in self.readme_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    readme_content = file.readlines()
                # Load meta.json [same level as readme file]
                meta_path = file_path.replace('README.md', 'metadata.json').replace('readme.md', 'metadata.json')
                with open(meta_path, 'r') as file:
                    meta_data = json.load(file)

            # except UnicodeDecodeError:
            #     with open(file_path, 'r', encoding='utf-16') as file:
            #         readme_content = file.readlines()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Extract category and repo name from the path
            path_parts = file_path.split('/')
            # category = path_parts[-4]
            # repo_name = path_parts[-3]
            category = path_parts[-3]
            repo_name = path_parts[-2]
            self.data.append({
                'category': category,
                'repo_name': repo_name,
                'readme_path': file_path,
                'content': readme_content,
                'meta': meta_data
            })
        self.data = self.data

    def __len__(self):
        """
        Return the total number of samples in the dataset.
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        Fetch a single data point.
        
        Args:
            idx (int): Index of the data point to fetch.
        
        Returns:
            dict: Contains 'category', 'repo_name', and 'content' for the README.
        """
        return self.data[idx]


# Usage
if __name__ == '__main__':
    # Assuming the data is structured in the './data/conf' directory:
    dataset = ReadmeDataset(root_dir='./data/conf')
    print(dataset[1])  # Print the first entry in the dataset
