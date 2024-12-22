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
        search_url = f"https://api.github.com/search/issues?q=is:pr+created:{start_date}..{end_date}+commenter:{username}"
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


def analyze_comments(comments, token):
    """
    Analyze comment data and fetch user's comments on each PR

    Args:
        comments (list): List of comment data
        token (str): GitHub personal access token

    Returns:
        dict: A dictionary mapping PRs to the user's comment count
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

    pr_comment_counts = defaultdict(int)
    pr_comment = defaultdict(int)

    for pr in comments:
        comments_url = pr['pull_request']['url']
        html_url = pr['html_url']

        # Fetch PR comments
        page = 1
        while True:
            response = requests.get(
                comments_url+'/comments',
                headers=headers,
                params={'page': page, 'per_page': 100}
            )

            if response.status_code != 200:
                print(f"failed to fetch comments for PR {html_url}: {response.status_code}")
                break

            data = response.json()
            if not data:
                break

            # Count user's comments on this PR
            pr_comment_counts[f"{html_url}"] = 0
            pr_comment[f"{html_url}"] = []
            for comment in data:
                if 'user' in comment and comment['user']['login'] == username:
                    pr_comment_counts[f"{html_url}"] += 1
                    pr_comment[f"{html_url}"].append(comment['body'])

            page += 1

    #print(f'{pr_comment_counts}')
    return dict(pr_comment_counts)

def main():
    if len(sys.argv) != 3:
        print("usage: python script.py <github_token> <year>")
        sys.exit(1)

    token = sys.argv[1]
    year = int(sys.argv[2])

    try:
        comments = fetch_pr_comments(token, year)
        total_comments = analyze_comments(comments, token)
        counts = sum(c for r, c in total_comments.items())

        print(f"{counts}")

    except Exception as e:
        print(f"exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()