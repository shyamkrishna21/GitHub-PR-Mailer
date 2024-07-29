import requests
from datetime import datetime, timedelta
import logging
import time
import pandas as pd

class GitHubService:
    def __init__(self, github_token, repo_owner, repo_name, days_to_look_back):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.days_to_look_back = days_to_look_back
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'

    def get_pull_requests(self, state):
        date_since = (datetime.utcnow() - timedelta(days=self.days_to_look_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
        query = f'repo:{self.repo_owner}/{self.repo_name} is:pr is:{state} updated:>={date_since}'
        params = {
            'q': query,
            'sort': 'updated',
            'order': 'desc',
            'per_page': 100
        }

        prs = []
        page = 1
        while True:
            params['page'] = page
            try:
                response = requests.get("https://api.github.com/search/issues", headers=self.headers, params=params)
                response.raise_for_status()

                if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers.get('X-RateLimit-Remaining'))
                    if remaining == 0:
                        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                        sleep_time = max(0, reset_time - time.time())
                        logging.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)
                        continue

                page_data = response.json().get('items', [])
                if not page_data:
                    break
                prs.extend(page_data)
                page += 1
            except requests.HTTPError as e:
                if e.response.status_code in (401, 403):
                    logging.error(f"Access denied: {e}")
                    return 'access_denied'
                else:
                    logging.error(f"Error fetching pull requests: {e}")
                    return 'error'
            except requests.RequestException as e:
                logging.error(f"Error fetching pull requests: {e}")
                return 'error'
        return prs

    @staticmethod
    def format_pr_summary(prs):
        summary = ""
        for pr in prs:
            summary += f"<b>ID:</b>  {pr.get('number')}<br>"
            summary += f"<b>Title:</b>  {pr.get('title')}<br>"
            summary += f"<b>User:</b>  {pr.get('user', {}).get('login')}<br>"
            summary += f"<b>URL:</b>  {pr.get('html_url')}<br>"
            summary += f"<b>Updated At:</b>  {pr.get('updated_at')}<br><br>"
        return summary

    @staticmethod
    def generate_email_report(open_prs, closed_prs, merged_prs, closed_not_merged_prs):
        summary = "<h2>Summary:</h2>"
        if not open_prs:
            summary += "<p><b>No open PRs:</b> There's no open PRs.</p>"
        else:
            summary += f"<p><b>Open PRs:</b> {len(open_prs)}</p>"
        summary += f"<p><b>Closed PRs:</b>  A total of {len(closed_prs)} PRs were closed </p>"
        summary += f"<p><b>Merged PRs:</b>  {len(merged_prs)} out of {len(closed_prs)} closed PRs were merged into the codebase.</p>"
        summary += f"<p><b>Closed but Not Merged PRs:</b>  {len(closed_not_merged_prs)}</p><br>"

        report = summary
        report += f"<h3>Open PR: {len(open_prs)}</h3>"
        report += GitHubService.format_pr_summary(open_prs)
        report += f"<h3>Closed PR: {len(closed_prs)}</h3>"
        report += GitHubService.format_pr_summary(closed_prs)
        report += f"<h3>Merged PR: {len(merged_prs)}</h3>"
        report += GitHubService.format_pr_summary(merged_prs)
        report += f"<h3>Closed-Not Merged: {len(closed_not_merged_prs)}</h3>"
        report += GitHubService.format_pr_summary(closed_not_merged_prs)

        return report

    @staticmethod
    def generate_excel_file(open_prs, closed_prs, merged_prs, closed_not_merged_prs, repo_name):
        data = {
            'Open PR': [(pr.get('number'), pr.get('title'), pr.get('user', {}).get('login'), pr.get('html_url'), pr.get('updated_at')) for pr in open_prs],
            'Closed PR': [(pr.get('number'), pr.get('title'), pr.get('user', {}).get('login'), pr.get('html_url'), pr.get('updated_at')) for pr in closed_prs],
            'Merged PR': [(pr.get('number'), pr.get('title'), pr.get('user', {}).get('login'), pr.get('html_url'), pr.get('updated_at')) for pr in merged_prs],
            'Closed but Not Merged PRs': [(pr.get('number'), pr.get('title'), pr.get('user', {}).get('login'), pr.get('html_url'), pr.get('updated_at')) for pr in closed_not_merged_prs]
        }

        with pd.ExcelWriter(f'pull_requests_summary_{repo_name}.xlsx') as writer:
            for sheet_name, prs in data.items():
                df = pd.DataFrame(prs, columns=['ID', 'Title', 'User', 'URL', 'Updated At'])
                df.to_excel(writer, sheet_name=sheet_name, index=False)
