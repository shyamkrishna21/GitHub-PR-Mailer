# GitHub-PR-Mailer
GitHub PR Mailer is a lightweight script designed to help developers and teams keep track of their pull requests effortlessly. With real-time updates and detailed email reports, you can monitor open, closed, merged, and unmerged PRs based on your defined time period, ensuring seamless collaboration and efficient code review processes.

## Setup Instructions

Follow these steps to set up the project and run the script.

### Prerequisites

- Python 3.x installed on your machine
- pip (Python package installer)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/shyamkrishna21/GitHub-PR-Mailer.git
    cd GitHub-PR-Mailer
    ```

2. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```sh
        source venv/bin/activate
        ```

4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

5. Run the script:
    ```sh
    python main.py
    ```

## Configuration

Make sure to configure the necessary variables in the `variables.py` file, such as GitHub token, repository details, email configurations, etc.

## Features

- Track open, closed, merged, and closed-but-not-merged pull requests.
- Generate a detailed email report.
- Generate an Excel file summarizing the pull requests.
