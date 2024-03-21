import re
from typing import Dict, Optional, Tuple, List
from parser.FileHandler import FileHandler
from parser.JobPosting import JobPosting

GITHUB_ADDITION_MARKER = '+'

class GithubTableMarkdownParser:
    def __init__(self, 
                 file_name:str
                 ) -> None:
        self.file_name = file_name

    def parse(self) -> List[JobPosting]:
        # fetch the latest commit
        # latest_commit = self.get_latest_commit()
        # changes = latest_commit.files[0].patch
        # print(changes)

        # save the latest commit changes into a file
        # test_changes = self.repo.get_commit('ceb7fdb92a994b589d1fe1b1a0dd4a0b4c2edec9').files[0].patch
        # test_changes = self.repo.get_commit('51dd5d7').files[0].patch
        # self.save_latest_update_into_file(test_changes)
        
        job_postings = []
        # read job info from the file and create JobPosting object
        lines = FileHandler.read_lines_from_file(self.file_name)
        updated_lines_index = self.get_updated_lines(lines)
        for index in updated_lines_index:
            job_postings.append(self.get_data_for_reaVNail_job_posting_table(lines[index]))

        return job_postings

    def get_updated_lines(self, lines: List[str]) -> List[int]:
        updated_lines = []
        for i in range(len(lines)):
            if lines[i][0] == GITHUB_ADDITION_MARKER:
                updated_lines.append(i)
        return updated_lines

    
    def get_data_for_reaVNail_job_posting_table(self, line: str) -> JobPosting:
        #Link to repo https://github.com/ReaVNaiL/New-Grad-2024
        name, location, roles, has_sponsor, date_added = self.split_table_row(line)
        

        company_name, career_site_url = self.get_name_data(name)
        job_location= self.get_location_data(location)
        roles_and_url = self.get_roles_data(roles)
        has_sponsorship = self.get_sponsorship_data(has_sponsor)
        posting_date = self.get_date_data(date_added)
        job_posting = JobPosting(company_name=company_name, 
                                 career_site=career_site_url, 
                                 locations=job_location, 
                                 roles=roles_and_url,
                                 date_posted=posting_date,
                                 has_sponsorship=has_sponsorship)
        return job_posting
    

    def get_name_data(self, line: str) -> Tuple[str, str]:
        name, url = self.parse_name_and_link_from_github_table(line)
        return (name, url)
    
    def get_location_data(self, line: str) -> List[str]:
        locations = []
        list_of_locations = self.split_multiple_lines_from_github_table(line)
        for location in list_of_locations:
            locations.append(location.strip())
        return locations
    
    def get_roles_data(self, line: str) -> Dict[str,str]:
        roles = {}
        roles_list = self.split_multiple_lines_from_github_table(line)
        for role in roles_list:
            name_and_link = self.parse_name_and_link_from_github_table(role)
            if name_and_link:
                position, url = name_and_link
                roles[position] = url
        return roles

    def get_sponsorship_data(self,line:str) -> str:
        result = self.parse_string_from_github_table(line)
        if result == '-':
            return 'No 😭'
        return result
    
    def get_date_data(self,line:str) -> str:
        return self.parse_string_from_github_table(line)
    

    # strip leading and trailing whitespace
    def parse_string_from_github_table(self, string: str) -> str:
        # Parse github table data that is only a string
        return string.strip()
    
    # for pattern: [name](url_link)
    def parse_name_and_link_from_github_table(self, string: str) -> Optional[Tuple[str, str]]:
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        match = re.search(pattern, string)
        # NOTE: closed role will have empty link: [closed_role_name](), hence parsing result will be None
        if match :
            key = match.group(1)
            value = match.group(2)
            return (key,value)
        return None
    
    def split_table_row(self,row:str) -> List[str]:
        return row.split('|')[1:-1]
        
    # for any job info with multiple line seperated by <br>
    def split_multiple_lines_from_github_table(self, string) -> List[str]:
        return string.split('<br>')
