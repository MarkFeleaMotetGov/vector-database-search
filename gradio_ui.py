import gradio as gr
from vector_db_utils import search_for_conditions
with gr.Blocks() as demo:

    with gr.Tab("Magic Conditions Search"):

        # add placeholder text 
        search_topic = gr.Textbox(label="Enter a search topic", placeholder="Noise pollution, moose population, air quality, etc.")
        submit_button = gr.Button("Submit")
        output_markdown = gr.Markdown("Markdown output")

        submit_button.click(
            fn=search_for_conditions,
            inputs=search_topic,
            outputs=output_markdown
        )

    


demo.launch()