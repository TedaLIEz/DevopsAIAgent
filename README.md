# DevOps AI Agent

## Build Environment Setup

Follow these steps to set up the build environment for the DevOps AI Agent project.

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Clone the Repository

First, clone the repository to your local machine:

```sh
git clone https://github.com/yourusername/devops_ai_agent.git
cd devops_ai_agent
```

### Install Dependencies

We recommend using `virtualenv` to create an isolated Python environment for development. Install `virtualenv` if you haven't already:

```sh
pip install virtualenv
```

Create a virtual environment and activate it:

```sh
virtualenv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required Python packages using pip:

```sh
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory of the project and add your environment variables. For example:

```env
OPENAI_API_KEY=your_openai_api_key
```

### GitHub Actions

This project includes a GitHub Actions workflow that runs a basic "Hello World" command on each push. The workflow file is located at `.github/workflows/hello-world.yml`.

### Ignored Files

The `.gitignore` file includes the following entries to ensure sensitive and unnecessary files are not committed to the repository:

```ignore
local.properties
data/
.env
env/
```

### Running the Project

To run the project, execute the following command:

```sh
python src/agent.py
```

This will start the DevOps AI Agent using the specified configurations.
