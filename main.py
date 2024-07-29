import logging
from email_services import EmailService
from github_services import GitHubService
from variables import *
import html2text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def filter_pull_requests(closed_prs):
    merged_prs = []
    closed_not_merged_prs = []
    for pr in closed_prs:
        if pr.get('pull_request', {}).get('merged_at'):
            merged_prs.append(pr)
        else:
            closed_not_merged_prs.append(pr)
    return merged_prs, closed_not_merged_prs

def generate_reports_and_send_email(reports):
    email_report = ""
    for repo_name, (open_prs, closed_prs) in reports.items():
        email_report += f"<h1>Here is the summary of pull requests for the past week: for {repo_name} Repository:</h1>"
        if open_prs == 'access_denied' or closed_prs == 'access_denied':
            email_report += f"<h3>Access Denied: Unable to fetch pull requests for {repo_name} due to insufficient permissions</h3>"
        elif open_prs == 'error' or closed_prs == 'error':
            email_report += f"<h3>Error: Unable to fetch pull requests for {repo_name} due to an error</h3>"
        else:
            merged_prs, closed_not_merged_prs = filter_pull_requests(closed_prs)
            repo_report = GitHubService.generate_email_report(open_prs, closed_prs, merged_prs, closed_not_merged_prs)
            GitHubService.generate_excel_file(open_prs, closed_prs, merged_prs, closed_not_merged_prs, repo_name)
            email_report += repo_report

    plain_text_report = html2text.html2text(email_report)
    print(plain_text_report)

    # Email setup
    email_service = EmailService(
        sender=EMAIL_FROM, 
        to=EMAIL_TO, 
        email_username=SMTP_USERNAME, 
        password=SMTP_PASSWORD, 
        server=SMTP_SERVER, 
        email_use_tls=EMAIL_USE_TLS, 
        port=SMTP_PORT,
        cc=EMAIL_CC,
        bcc=EMAIL_BCC
    )
    email_service.send_email(email_report)

def main(repos=GITHUB_REPOS, days_to_look_back=DAYS_TO_LOOK_BACK):
    reports = {}
    for repo in repos:
        repo_owner = repo['owner']
        repo_name = repo['name']
        github_token = repo.get('token')  # Get the token for the specific repository
        github_service = GitHubService(github_token, repo_owner, repo_name, days_to_look_back)
        
        open_prs = github_service.get_pull_requests('open')
        closed_prs = github_service.get_pull_requests('closed')

        reports[repo_name] = (open_prs, closed_prs)

    generate_reports_and_send_email(reports)

if __name__ == "__main__":
    main()
