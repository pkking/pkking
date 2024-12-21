import requests
import sys

def get_username(token):
    url = f"https://gitee.com/api/v5/user"
    params = {"access_token": token}
    # Make the request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the JSON data
    return response.json().get("login")

    
def fetch_and_count_pull_request_comment_events(token, year):
    """
    Fetch JSON data for the given user from Gitee API with the provided token, 
    and count the number of PullRequestCommentEvent types.

    :param user_name: Gitee username to fetch events for.
    :param token: Access token for authentication.
    :return: Count of PullRequestCommentEvent occurrences.
    """
    user_name = get_username(token)
    # Construct the API URL dynamically using the user_name
    url = f"https://gitee.com/api/v5/users/{user_name}/events"
    
    # Add token to the headers or query parameters
    params = {"access_token": token, "limit": 1000}
    
    # Make the request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Parse the JSON data
    events = response.json()
    
    # Count occurrences of PullRequestCommentEvent
    count = sum(
        1 for event in events
        if event.get("type") == "PullRequestCommentEvent" and event.get("created_at", "").startswith(str(year))
    )
    return count

def main():
    if len(sys.argv) != 3:
        print("使用方法: python script.py <github_token> <year>")
        sys.exit(1)
    
    token = sys.argv[1]
    year = int(sys.argv[2])
    

    count = fetch_and_count_pull_request_comment_events(token, year)
    print(f"{count}")

if __name__ == "__main__":
    main()