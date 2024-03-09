### Goals:

To subscribe to github API to retrieve the latest commit to this [New grad 2024 repo](https://github.com/ReaVNaiL/New-Grad-2024)

### How this repo work?

Everytime a new commit is made approving a new job post, the `README.md` will be updated with new jobs to apply to

--> Strategy: So I have to create a service that subscribe to this Github repo and check if the README.md is updated, aka: checking if a new commit is made
Then extract what is the new job post

### The format of a job listing

```
| Name         | Location     | Roles                | Citizenship/Visa Requirements | Date Added <br> mm/dd/yyyy |
| ------------ | ------------ | -------------------- | ----------------------------- | --------------------------- |

# A single link
| [Applied Intuition](https://www.appliedintuition.com/careers) | - Mountain View, CA | ✅ [Software Engineer - New Grad](https://boards.greenhouse.io/appliedintuition/jobs/4296158005)  | Unknown | 03/02/2024 |


# Multiple links
| [Epic](https://www.epic.com/) | - Madison, WI | ✅ [Integration Engineer](https://app.ripplematch.com/v2/public/job/71312c11/details?utm_source=Github&utm_medium=organic_social&utm_campaign=growth_github&utm_content=account&utm_term=null) <br> ✅ [VMware Engineer](https://app.ripplematch.com/v2/public/job/b4673762/details?utm_source=Github&utm_medium=organic_social&utm_campaign=growth_github&utm_content=account&utm_term=null) <br> ✅ [Windows Engineer](https://app.ripplematch.com/v2/public/job/15395ee2/details?utm_source=Github&utm_medium=organic_social&utm_campaign=growth_github&utm_content=account&utm_term=null) <br> ✅ [Software Developer](https://app.ripplematch.com/v2/public/job/fe328b97/details?utm_source=Github&utm_medium=organic_social&utm_campaign=growth_github&utm_content=account&utm_term=null) | Does not offer sponsorship | 02/27/2024 |


# Closed job
| [Snap](https://snap.com/en-US) | - Los Angeles, CA <br> - Seattle, WA <br> - Palo Alto, CA <br> - New York, NY | 🔒 [Software Engineer - Snap Up Apprentice]() | - | 01/16/2024 |

```

#### Dilema - should the bot run every 60 seconds to retrieve the latest commit?

When the bot run every 60 seconds, it will fetch the latest commit
But what if there's no new commit in the next bot-run, it will fetch the same latest commit again --> this is bad, but we can keep track of last commit we already fetched and compare to the new one to see if theyre the same

So is there a way to make the bot subscribe to github API that notifies whenever there's a new commit?

from enum import Enum, auto


# a data in the table can be a string, a embedded string link, or a image embedded with link
class GithubTableDataFormatEnum(Enum) :
    STRING = auto() # normal parsing
    STRING_LIST = auto() # parsing multple line split by <br>
    EMBEDDED_STRING_LINK = auto() # parsing with [name](url) format
    EMBEDDED_STRING_LINK_LIST = auto() # parsing multiple strings with with [name](url) format
    EMBEDDED_IMAGE_LINK = auto() # parsing with <img><href> format