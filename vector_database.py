import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


assistant = client.beta.assistants.create(
  name="Conditions Retrieval Assistant",
  instructions="You are an assistant specialized in retrieving and compiling relevant conditions from documents.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
)

# Create a vector store called "Client Conditions"
vector_store = client.beta.vector_stores.create(name="Condition Documents")

# Ready the all PDF files in /test_documents for upload
file_paths = []
for root, dirs, files in os.walk("./test_documents"):
    for file in files:
        file_paths.append(os.path.join(root, file))

file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# search_subject = "water use"
# search_subject = "transmission lines"
# search_subject = "moose"
search_subject = "noise pollution"
# search_subject = "First Nations/Indigenous/Aboriginal Peoples"
# search_subject = "forest fires" # Hallucinates a lot because there isn't much about forest fires in the documents
# search_subject = "air quality"
# search_subject = "emissions"

# query = f"What are ALL of the conditions related to {search_subject}? Mention just the names of the conditions, thier condition number and the copy the exact part that relates to {search_subject}."
query = f"What are ALL of the conditions related to {search_subject}? Mention just the names of the conditions and thier condition number."

# Create a thread to handle the query
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": query
    }
  ]
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

message_content = messages[0].content[0].text
annotations = message_content.annotations
citations = []
for index, annotation in enumerate(annotations):
    message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
    if file_citation := getattr(annotation, "file_citation", None):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f"[{index}] {cited_file.filename}")

print(message_content.value)
print("\n".join(citations))
