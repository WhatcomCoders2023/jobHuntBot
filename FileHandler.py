from typing import List


FILE_NAME = "latest_commit_changes_multiple_roles.md"
#FILE_NAME = "latest_commit_changes.md"

class FileHandler:

   
    @staticmethod
     # write repos changes into a file
    def save_latest_update_into_file(self, updates: str):
        with open(FILE_NAME,"w", encoding='utf-8') as file:
            file.write(updates)

    @staticmethod
    def read_lines_from_file(filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.readlines()
