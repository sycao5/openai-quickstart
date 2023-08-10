import sys
import os
import gradio as gr
import openai
from utils.logger import Logger
from book.content import ContentType

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator
from gradio.components import Textbox,Audio,Radio
import gradio.components as gr_comp

LOG = Logger(debug=True).logger

def translate_pdf(pdf_file_path, file_format, target_language, output_file_path, pages: int = 5):

    print(f"pdf_file_path={pdf_file_path}, file_format={file_format}, target_language={target_language}, output_file_path={output_file_path}, pages={pages}")
    translator = PDFTranslator(model)
    translated_results = translator.translate_pdf(pdf_file_path, file_format, output_file_path=output_text)

    formatted_results= []
    for obj in translated_results:
        if obj.type == ContentType.TABLE:
            formatted_table = format_as_table( obj.translation)
            formatted_results.append(formatted_table)
        else:
            formatted_text = format_and_display(obj.translation)
            formatted_results.append(formatted_text)

    return formatted_results


def format_and_display(input_string):
    # Remove the enclosing square brackets and split the string into individual parts
    parts = input_string[1:-1].split(', ')
    # Format each part to remove leading/trailing whitespaces and newline characters
    formatted_parts = [part.strip().replace("\\n", "\n") for part in parts]
    # Join the formatted parts into a single string
    formatted_result = "\n\n".join(formatted_parts)
    return formatted_result

def format_as_table(input_str):
    rows = input_str.strip().split('\n')
    header = rows[0]
    data = rows[1:]

    # Create the table header
    header_cells = "".join("<th>{}</th>".format(cell.strip()) for cell in header.split('\t'))
    table = "<table><tr>{}</tr>".format(header_cells)

    # Create the table rows
    for row in data:
        row_cells = "".join("<td>{}</td>".format(cell.strip()) for cell in row.split('\t'))
        table += "<tr>{}</tr>".format(row_cells)

    table += "</table>"

    return table

global model, pdf_file_path

if __name__ == "__main__":
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
    model = OpenAIModel(model=model_name, api_key=api_key)


    pdf_file_path = args.book if args.book else config['common']['book']
    # file_format = args.file_format if args.file_format else config['common']['file_format']

    input_interface = [
        # gr_comp.File(label="Upload a PDF"),
        gr_comp.Textbox(label="Pdf File path"),
        gr_comp.Textbox(label="File Format (e.g., PDF)"),
        gr_comp.Textbox(label="Target Language (e.g., 中文)"),
        gr_comp.Textbox(label="Output File Path (optional)"),
        gr_comp.Number(label="Number of Pages (optional)"),
    ]

    # Output interface
    output_text = gr.outputs.HTML(label='Transcribed/Translated text')

    app = gr.Interface(
        fn= translate_pdf, 
        inputs=input_interface, 
        outputs=output_text, 
        title="PDF Analyzer and Translation").launch()
