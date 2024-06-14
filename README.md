### Installation

1. Clone the repository:
   
   `git clone https://github.com/MarkFeleaMotetGov/vector-database-search.git`

   `cd vector-database-search`
   

2. Set up a virtual environment:
   
    `python -m venv venv`

3. Activate the virtual environment:
   - On Windows:
   
        `venv\Scripts\activate`
   - On Linux/MacOS:
   
        `source venv/bin/activate`

4. Install the required packages:
   
    `pip install -r requirements.txt`

5. Create a file named `.env` in the root directory of the project and add your OpenAI API key:
   ```text
   OPENAI_API_KEY=openai_api_key_here
   ```

### Usage

`python vector_database.py`
