from transformers.convert_graph_to_onnx import convert
from pathlib import Path
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(
        prog="ConvertModelToOnnx",
        description="Converts a model to ONNX"
    )
    parser.add_argument(
        "-ip","--input-model-path",
        type=str,
        help="The path to the input modelpackage"
    )
    parser.add_argument(
        "-if","--input-model-framework",
        type=str,
        help="The framework of the model in the package (IE \"pt\")"
    )
    parser.add_argument(
        "-o","--output-path",
        type=str,
        help="The path to write the ONNX binary to"
    )
    parser.add_argument(
        "-op","--opset",
        type=str,
        help="The path to write the ONNX binary to"
    )
    return parser.parse_args().__dict__

def main(input_model_framework: str,input_model_path,output_path,opset) -> None:
    convert(
        framework=input_model_framework, 
        model=input_model_path,
        output=Path(output_path), 
        opset=opset
    )

if __name__ == "__main__":
    args = parse_args()
    main(**args)