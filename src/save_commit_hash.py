import os
from dvc.repo import Repo
from dvc.exceptions import DvcException

def get_and_save_dvc_commit_hash(output_file="data/commit_hash.txt"):
    """
    Get the current DVC commit hash from the repository and save it to a file.
    
    Args:
        output_file (str): Path to the output file (default: data/commit_hash.txt)
    
    Returns:
        str: The current DVC commit hash
        
    Raises:
        DvcException: If there's an error accessing the DVC repository
        ValueError: If not in a DVC repository
        IOError: If there's an error writing to the file
    """
    try:
        # Initialize DVC repo object
        repo = Repo(".")
        
        # Get the current commit hash
        commit_hash = repo.scm.get_rev()
        
        # Save the hash to a file with UTF-8 encoding
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(commit_hash)
            print(f"Commit hash saved to {output_file}")
        except IOError as e:
            raise IOError(f"Error writing to file {output_file}: {str(e)}")
            
        return commit_hash
        
    except DvcException as e:
        raise DvcException(f"Error accessing DVC repository: {str(e)}")
    except Exception as e:
        raise ValueError(f"Not in a DVC repository or other error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        hash = get_and_save_dvc_commit_hash()
        print(f"Current DVC commit hash: {hash}")
    except (DvcException, ValueError, IOError) as e:
        print(f"Error: {str(e)}")