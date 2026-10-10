import re
import urllib.request
import json
import os

USERNAME = "MinkWungNe"
SVG_PATHS = [
    "svg/04_stats/stats-card.svg",
    "svg/04_stats/stats-card-mobile.svg"
]

def fetch_profile_views():
    try:
        url = f"https://komarev.com/ghpvc/?username={USERNAME}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            svg = response.read().decode('utf-8')
            matches = re.findall(r'>([0-9,]+)</text>', svg)
            if matches:
                return matches[-1]
    except Exception as e:
        print(f"Error fetching profile views: {e}")
    return None

def fetch_total_commits(headers):
    try:
        url = f"https://api.github.com/search/commits?q=author:{USERNAME}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            total = data.get("total_count")
            if total is not None:
                return total
    except Exception as e:
        print(f"Error fetching commits: {e}")
    return None

def format_approx_commits(count):
    if count is None:
        return None
    if count < 10:
        return f"{count}"
    elif count < 50:
        step = 5
    elif count < 200:
        step = 10
    elif count < 1000:
        step = 50
    else:
        step = 100
    approx = (count // step) * step
    return f"{approx}+"

def fetch_github_stats():
    headers = {"User-Agent": "Mozilla/5.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    stats = {}
    try:
        # Fetch user info
        user_url = f"https://api.github.com/users/{USERNAME}"
        req = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            user_data = json.loads(response.read().decode())
        
        public_repos = user_data.get("public_repos", 10)
        stats["repos"] = f"{public_repos}"
        
        # Fetch repos to calculate stars
        repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
        req = urllib.request.Request(repos_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            repos_data = json.loads(response.read().decode())
        
        total_stars = sum(r.get("stargazers_count", 0) for r in repos_data)
        stats["stars"] = f"★ {total_stars}" if total_stars > 0 else "★ ACTIVE"
    except Exception as e:
        print(f"Error fetching github stats: {e}")

    # Fetch total commits and format approximately
    commit_count = fetch_total_commits(headers)
    if commit_count is not None:
        stats["commits"] = format_approx_commits(commit_count)

    # Fetch profile views
    views = fetch_profile_views()
    if views:
        stats["views"] = views

    return stats if stats else None

def update_svg():
    stats = fetch_github_stats()
    if not stats:
        print("No stats fetched.")
        return

    for path in SVG_PATHS:
        if not os.path.exists(path):
            print(f"File {path} not found.")
            continue
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Update commits
        if "commits" in stats:
            content = re.sub(
                r'(<text id="stat-commits"[^>]*>)[^<]*(</text>)',
                rf'\g<1>{stats["commits"]}\g<2>',
                content
            )

        # Update repos
        if "repos" in stats:
            content = re.sub(
                r'(<text id="stat-repos"[^>]*>)[^<]*(</text>)',
                rf'\g<1>{stats["repos"]}\g<2>',
                content
            )
        
        # Update stars
        if "stars" in stats:
            content = re.sub(
                r'(<text id="stat-stars"[^>]*>)[^<]*(</text>)',
                rf'\g<1>{stats["stars"]}\g<2>',
                content
            )

        # Update profile views
        if "views" in stats:
            content = re.sub(
                r'(<text id="stat-views"[^>]*>)[^<]*(</text>)',
                rf'\g<1>{stats["views"]}\g<2>',
                content
            )
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Successfully updated {path}.")

if __name__ == "__main__":
    update_svg()
