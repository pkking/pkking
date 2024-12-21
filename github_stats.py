import requests
from datetime import datetime
import sys
from collections import defaultdict

def fetch_pr_comments(token, year):
    """
    Fetch all PR comments for the specified year
    
    Args:
        token (str): GitHub personal access token
        year (int): Year to analyze
    
    Returns:
        list: List of comment data
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # get uesr info
    user_response = requests.get('https://api.github.com/user', headers=headers)
    if user_response.status_code != 200:
        print(f"failed to get user info: {user_response.status_code}")
        sys.exit(1)
    
    username = user_response.json()['login']
    
    # time span
    start_date = f"{year}-01-01T00:00:00Z"
    end_date = f"{year}-12-31T23:59:59Z"
    
    comments = []
    page = 1
    
    while True:
        # get commented PR in time range by user
        search_url = f"https://api.github.com/search/issues?q=commenter:{username}+created:{start_date}..{end_date}+is:pr"
        response = requests.get(
            search_url,
            headers=headers,
            params={'page': page, 'per_page': 100}
        )
        
        if response.status_code != 200:
            print(f"api request failed: {response.status_code}")
            break
            
        data = response.json()
        if not data['items']:
            break
            
        comments.extend(data['items'])
        page += 1
        
        # limit check
        if 'X-RateLimit-Remaining' in response.headers:
            if int(response.headers['X-RateLimit-Remaining']) == 0:
                print("api limit reached")
                break
    
    return comments

def analyze_comments(comments):
    """
    Analyze comment data
    
    Args:
        comments (list): List of comment data
    
    Returns:
        tuple: (total comment count, dictionary of comment URLs)
    """
    comment_urls = defaultdict(list)
    
    for comment in comments:
        repo_name = comment['repository_url'].split('/')[-1]
        pr_number = comment['number']
        comment_url = comment['html_url']
        comment_urls[f"{repo_name}#{pr_number}"].append(comment_url)
    
    return len(comments), dict(comment_urls)

def main():
    if len(sys.argv) != 3:
        print("usage: python script.py <github_token> <year>")
        sys.exit(1)
    
    token = sys.argv[1]
    year = int(sys.argv[2])
    
    try:
        comments = fetch_pr_comments(token, year)
        total_comments, comment_urls = analyze_comments(comments)
        
        print(f"{total_comments}")

    except Exception as e:
        print(f"exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()