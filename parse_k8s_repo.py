import requests
from requests.structures import CaseInsensitiveDict
from collections import defaultdict, Counter

baseurl = "https://api.github.com/repos/kubernetes/kubernetes/"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/vnd.github.v3+json"

# 1. list all contributors in the repository and classify the with permission(user_type)
def classify_contributors(baseurl = baseurl, headers = headers, per_page = 30, total_page = 5):
    """
    # https://docs.github.com/en/rest/reference/repos#list-repository-contributors

    Args:
        baseurl (string): github api base URL
        per_page (int, optional): page Size. Defaults to 30.
        total_page (int, optional): page number. Defaults to 5.
    Lists contributors to the specified repository and sorts them by the number of commits per contributor in descending order. 
    this api only grab 500 at the most, the rest are marked as anonymous
    """
    permission_user_dict = defaultdict(set)
    for page in range(1, total_page + 1):
        url = baseurl + "contributors?per_page=" + str(per_page) + "&page=" + str(page)
        resp = requests.get(url, headers=headers).json()
        for r in resp:
            permission_user_dict[r['type']].add(r['login'])
    # print(len(permission_user_dict['User']))  got 367, correct

    return permission_user_dict


# 2 stat top 30 user which based on the commit count
def stat_top30commit_number_user(baseurl = baseurl, headers = headers):
    """
    # https://docs.github.com/en/rest/reference/repos#list-repository-contributors
    
    Args:
    baseurl (string): github api base URL
    Lists contributors to the specified repository and sorts them by the number of commits per contributor in descending order. which match the requirement
    TODO upgrade the return info if necessary.
    """
    name_set = set()
    resp = requests.get(baseurl + "contributors", headers=headers).json()
    for r in resp:
        name_set.add(r['login'])
    return name_set

# 3 calc top 30 user commit line quantity
def stat_top30commit_line_user(baseurl = baseurl, headers = headers):   
    """
    https://docs.github.com/en/rest/reference/metrics#get-all-contributor-commit-activity

    Args:
        baseurl (str): github api base URL
    github api only return top 100 result.
    TODO: calculate the add + delete lines number
    """
    top30_commit_line = dict()
    resp = requests.get(baseurl + "stats/contributors", headers=headers).json()
    for r in resp:
        name = r['author']['login']
        editor_no = 0
        for w in r['weeks']:
            editor_no  += w['a'] +  w['d']
        top30_commit_line[name] = editor_no
    # print(len(top30_commit_line)) return 100, seems this api can only return 
    return Counter(top30_commit_line).most_common(30)
    # return top30_commit_line



def stat_pull_request(baseurl = baseurl, headers = headers):
    """_summary_

    Args:
        baseurl (str): _description_
        headers (str): _description_
    """
    resp = requests.get(baseurl + "pulls?state=all", headers=headers).json()
    labels = Counter()
    top5_labels = dict()
    for r in resp:
        labels += Counter([x['name'] for x in  r["labels"]])
    for key, val in labels.most_common(5):
        top5_labels[key]= val
    print("the top 5 PR is: "+ str(list(top5_labels.keys())))
    
    names = set()
    for r in resp:
        label = Counter([x['name'] for x in  r["labels"]])
        for _ in  label.keys() & top5_labels.keys():
            names.add(r['user']['login'])
    return names
    
    
    
    
    
    
if __name__ == '__main__':
    # print(classify_contributors(per_page=100, total_page=5))
    # print(stat_top30commit_number_user())
    # print(stat_top30commit_line_user())
    print(stat_pull_request())