from dataclasses import dataclass, field, asdict
from typing import Dict, List


@dataclass
class JobPosting:
    company_name: str
    career_site: str
    locations: List[str]
    date_posted: str
    has_sponsorship: str = "Unknown"
    roles: Dict[str, str] = field(
        default_factory=dict
    )  # key is role name, and value is role link

    def to_dict(self):
        # Convert the dataclass instance to a dict
        return asdict(self)

    def __repr__(self) -> str:
        # Formatting the roles dictionary entries properly
        roles_repr = ", ".join(
            [f"{repr(role)}: {repr(link)}" for role, link in self.roles.items()]
        )
        # Ensuring locations are displayed as a list of strings
        locations_repr = ", ".join(repr(location) for location in self.locations)
        return (
            f"JobPosting(company_name={repr(self.company_name)}, career_site={repr(self.career_site)}, "
            f"locations=[{locations_repr}], has_sponsorship={repr(self.has_sponsorship)}, "
            f"date_posted={repr(self.date_posted)}, roles={{{roles_repr}}})"
        )

    @classmethod
    def create_job_posting(
        company_name: str,
        career_site: str,
        locations: str,
        has_sponsorship: str,
        date_posted: str,
        roles: Dict[str, str],
    ) -> "JobPosting":
        return JobPosting(
            company_name=company_name,
            career_site=career_site,
            locations=locations,
            has_sponsorship=has_sponsorship,
            date_posted=date_posted,
            roles=roles,
        )
