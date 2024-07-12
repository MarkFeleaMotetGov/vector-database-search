import os
from dotenv import load_dotenv
load_dotenv()

# import arg parser
import argparse

from colorama import Fore, Style

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_vector_store(name):
    vector_store = client.beta.vector_stores.create(name=name)
    return vector_store

def retrieve_vector_store(vector_store_id):
    vector_store = client.beta.vector_stores.retrieve(vector_store_id)
    return vector_store

def upload_files_to_vector_db(vector_store_id, folder_path):
    """
    Uploads all files from a specified folder to an existing vector database and polls until the upload is complete.

    Parameters:
    vector_store_id (str): The ID of the existing vector store.
    folder_path (str): Path to the folder containing files to be uploaded.

    Returns:
    dict: Status and file counts of the uploaded batch.
    """
    
    # Get all file paths from the specified folder
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    # Open the files to be uploaded
    file_streams = [open(path, "rb") for path in file_paths]

    try:
        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams
        )

        # Print and return the status and the file counts of the batch
        print(file_batch.status)
        print(file_batch.file_counts)

        return file_batch.status, file_batch.file_counts
    
    finally:
        # Close the file streams
        for stream in file_streams:
            stream.close()

def create_assistant(name):
    assistant = client.beta.assistants.create(
        name=name,
        instructions="You are an assistant specialized in retrieving and compiling relevant conditions from documents.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )
    return assistant

def retrieve_assistant(assistant_id):
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

def attach_vector_store_to_assistant(assistant_id, vector_store_id):
    assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    return assistant

def search_for_conditions(search_subject):
    query = f"What conditions are related to {search_subject}? Mention the names of the conditions, their condition number, and the document the condition is from. If there are duplicates in different files, still list them separately. Also mention how the condition is relevant to the subject."

    thread = client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": query
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id="asst_YtJjYlPR3rLJgTZvV2pxk25R"
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    annotations = message_content.annotations

    print("ANNOTATIONS")
    print(annotations)

    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    print(message_content.value)
    print("\n".join(citations))

    return message_content.value

if __name__ == "__main__":
    # assistant = create_assistant("test3_assistant")
    # print(assistant)
    # print(Fore.GREEN + f"Assistant ID is: {assistant.id}" + Style.RESET_ALL)

    # # assistant = retrieve_assistant("asst_gV7AcjjUpzqzmlN4qs38fai5")
    # # print(assistant)

    # vector_store = create_vector_store("test3_vector_store")
    # print(vector_store)
    # print(Fore.GREEN + f"Vector Store ID is: {vector_store.id}" + Style.RESET_ALL)

    # # vector_store = retrieve_vector_store("vs_aumesGPDljviAKD33vGRwr8q")
    # # print(vector_store)

    # status, file_counts = upload_files_to_vector_db(vector_store.id, "./test_documents")

    # attach_vector_store_to_assistant(assistant.id, vector_store.id)
    # print(Fore.GREEN + "Attached vector store to assistant" + Style.RESET_ALL)

    # -----------------------

    # arg parser for search_subject
    parser = argparse.ArgumentParser(description='Retrieve conditions related to a specific subject.')
    parser.add_argument('search_subject', type=str, help='The subject to search for conditions related to.')
    args = parser.parse_args()

    # check if the search_subject is provided by counting num of arguments, if not print usage and exit
    if not args.search_subject:
        parser.print_usage()
        exit(1)

    search_subject = args.search_subject
    search_for_conditions(search_subject)



    # -----------------------

