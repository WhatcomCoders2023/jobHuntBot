from typing import List

class FileHandler:
    @staticmethod
    # write repos latest commits' changes, aka latest job posting into a file
    # updates should be coming from github.Commit.Commit.files[0].patch
    def save_latest_update_into_file(filename: str, updates: str):
        try:
            with open(filename,"w", encoding='utf-8') as file:
                file.write(updates)
            print("File saved successfully")
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")
    
    @staticmethod
    def read_lines_from_file(filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.readlines()
