from google import genai
from mistralai import Mistral
from pathlib import Path
from mistralai import ImageURLChunk, TextChunk
import json
import base64


gemini = genai.Client(api_key="AIzaSyBamFhrjI14XdIqVtJ_RfTiJDxVbR1yRHA")
mistral = Mistral(api_key="U4Lp0fYgnsLZ8EvKYWoQEGeAvDTlb4Jm")


def analyse_image_gemini(img_path:str, querry:str):
    # Upload the image
    uploaded_file = gemini.files.upload(file=img_path)

    # Use the uploaded image in your request
    response = gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=[uploaded_file, querry]
    )
    print(response.text)
    return response.text


def analyse_image_mistral(img_path:str, querry:str, use_pixtral:bool):
    # Verify image exists
    image_file = Path(img_path)
    assert image_file.is_file()

    # Encode image as base64 for API
    encoded = base64.b64encode(image_file.read_bytes()).decode()
    base64_data_url = f"data:image/jpeg;base64,{encoded}"

    if not use_pixtral:
        # Process image with OCR
        image_response = mistral.ocr.process(
            document=ImageURLChunk(image_url=base64_data_url),
            model="mistral-ocr-latest"
        )

        # Convert response to JSON
        response_dict = json.loads(image_response.model_dump_json())
        json_string = json.dumps(response_dict, indent=4)
        print(json_string)
        return json_string
    else:
        chat_response = mistral.chat.complete(
            model="pixtral-12b-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        ImageURLChunk(image_url=base64_data_url),
                        TextChunk(
                            text=(
                                f"{querry}.The output should be strictly be json with no extra commentary"
                            )
                        ),
                    ],
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        # Parse and return JSON response
        response_dict = json.loads(chat_response.choices[0].message.content)
        print(json.dumps(response_dict, indent=4))
        return response_dict



def test():
    img_path = "/Users/souymodip/Downloads/IMG_2540.jpg"
    querry = "Make a list of names of the book and the authors"
    # analyse_image_gemini(img_path, querry)
    analyse_image_mistral(img_path, querry, use_pixtral=False)


if __name__ == "__main__":
    test()
