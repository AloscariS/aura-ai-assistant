import argparse
import os

import openai
import requests
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from termcolor import colored

from utils import *

# Load global variables
SYS_PROMPT = get_str_from_file("system_prompt.txt")
ASSISTANT_NAME = "Nova"
# Load environment variables from the .env file
load_dotenv()
AI_ML_API_KEY = os.getenv("AIML_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def init_openai_client(aiml_key:str, base_url: str = "https://api.aimlapi.com/v1"):
    client = OpenAI(api_key=AI_ML_API_KEY, base_url=base_url)
    return client


def init_elevenlabs_client(api_key: str):
    elevenlabs = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
    )
    return elevenlabs


# Get the response from a model
def ask_mllm(client:OpenAI, model:str, system_prompt: str, user_prompt: str) -> str:
    """
    Asks the model for a response based on the system and user prompts.
    
    Args:
    - client (OpenAI): The OpenAI client instance.
    - model (str): The model to use for the request.
    - system_prompt (str): The system prompt to provide context.
    - user_prompt (str): The user's prompt or question.
    
    Returns:
    - str: The response from the model.
    """
    # Handle the image understanding and captioning
    if is_visual_request(user_prompt):
        img_fp = "medias/cam.jpg"
        capture_cam(img_fp)
        base64_image = encode_image(os.path.join(os.getcwd(), img_fp))
        completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        model="openai/gpt-4o",  # Recommended model for image understanding
    )
    else:
        # Set the model and compose the message
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=256,
        )
    
    # Check if the response is empty
    if not completion.choices:
        return None
    response = completion.choices[0].message.content
    return response


# Record the user's voice and converts it to text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nI'm listening...")
        audio = r.listen(source)
        try:
            # Recognize speech and convert it to text
            text = r.recognize_google(audio)
            return text
        except:
            print("I didn't catch any speech...Please try again.")
            return None


def load_tts_model(api_key: str, model: str = "#g1_aura-asteria-en"):
    url = "https://api.aimlapi.com/tts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model
        # The text will be added later
    }
    return url, headers, payload


def text_to_speech_aiml(text: str, url:str, headers:dict, payload:dict, output_file: str = "output.mp3"):
    # Add the text to the payload
    payload["text"] = text
    # Make the request to the TTS API
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        # Write the audio to a file
        with open(output_file, "wb") as f:
            f.write(response.content)

    except requests.exceptions.RequestException as e:
        print(colored(f"Error in TTS API request:\n {e}", 'red'))
        raise e


def text_to_speech_elevenlabs(text: str, output_file: str = "output.mp3", client: ElevenLabs = None):
    # Call the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id="FGY2WhTYpPnrIDTdsKH5",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=0.9,
        ),
    )
    # Writing the audio to a file
    with open(output_file, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
 

def conversation_loop(textual_interaction = False, elevenlabs_voice = False):
    # Load openai client
    client = init_openai_client(AI_ML_API_KEY)

    if elevenlabs_voice:
        voice_client = init_elevenlabs_client(ELEVENLABS_API_KEY)
    else:
        voice_client = client
        url, headers, payload = load_tts_model(AI_ML_API_KEY)

    """
    Select the LLM to interact with.
    You can change the model to any other available model.
    Reccomended models (already tested) are:
    gpt-3.5-turbo, gpt-4, gpt-4o,  deepseek/deepseek-r1, gemini-2.0-flash,
    qwen-turbo, gemini-1.5-pro, gemini-1.5-flash, qwen-plus
    """
    model = "gpt-3.5-turbo"

    audio_fp = "medias/response.mp3"
    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(audio_fp), exist_ok=True)

    # Flags to check different interaction states
    waking_up = False   # waiting for the wake word
    chatting = False    # continuing the conversation
    
    # Main loop
    while True:
        if textual_interaction:
            user_prompt = input(colored("Type your prompt: ", 'blue'))
        else:
            # Listen to the user
            user_prompt = speech_to_text()

        # First interaction, check if the user said the wake word
        if user_prompt is not None and chatting == False and ASSISTANT_NAME.lower() in user_prompt.lower():
            waking_up = True
            chatting = True
        elif user_prompt is not None and not textual_interaction:
            print("*" * os.get_terminal_size().columns)
            print(colored(f"User said:\n {user_prompt}", 'blue'))
            print("*" * os.get_terminal_size().columns)

        # Continue the conversation since the wake word was detected
        while chatting:
            # Check if the assistant is just "waking up"
            if waking_up:
                waking_up = False
            else:
                if textual_interaction:
                    user_prompt = input(colored("Type your prompt: ", 'blue'))
                else:
                    # Listen to the user
                    user_prompt = speech_to_text()
            
            if user_prompt != None:
                print("*" * os.get_terminal_size().columns)
                print(colored(f"User said:\n {user_prompt}", 'blue'))

                # If the user says goodbye, stop the conversation
                # until the next wake word is detected.
                if is_goodbye(user_prompt):
                    text=f"Goodbye! Say {ASSISTANT_NAME}, if you'll need more help. See you soon!"
                    # Switch between TTS providers
                    if elevenlabs_voice:
                        text_to_speech_elevenlabs(
                            text=text,
                            output_file=audio_fp,
                            client=voice_client
                        )
                    else:
                        text_to_speech_aiml(
                            text=text,
                            url=url,
                            headers=headers,
                            payload=payload,
                            output_file=audio_fp
                        )
                    print("*" * os.get_terminal_size().columns)
                    print(colored(f"User said:\n {user_prompt}", 'blue'))
                    print(colored(f"\n{ASSISTANT_NAME} said:\n {text}", 'green'))
                    print("*" * os.get_terminal_size().columns)

                    # Play the default goodbye message
                    play_mp3(audio_fp)
                    chatting = False
                    
                    record_history(
                        user_prompt=user_prompt,
                        text_response=text
                    )
                    # Go back to the main loop, waiting for the wake word
                    break
                
                # Ask the model for a response
                try:
                    text_response = ask_mllm(
                        client=client,
                        model=model,
                        system_prompt=SYS_PROMPT,
                        user_prompt = user_prompt
                    )
                # Catch the specific “400” BadRequestError via the openai namespace
                # (Only for debugging purposes)
                except openai.BadRequestError as err:
                    # get the error body
                    body = err.response.json()
                    options = body["meta"][0]["options"]

                    answer = input(colored("Invalid model specified. Show valid models? [y/N] ", "red"))
                    if answer.strip().lower().startswith("y"):
                        print(colored(f"Valid models are:", "cyan"))
                        for m in options:
                            print(colored(f"  •{m}",'cyan'))
                    else:
                        print(colored("OK, model list skipped!", "cyan"))
                    return
                
                if text_response != None:
                    # Reproduce the response using TTS
                    if elevenlabs_voice:
                        text_to_speech_elevenlabs(
                            text=text_response,
                            output_file=audio_fp,
                            client=voice_client
                        )
                    else:
                        text_to_speech_aiml(
                            text=text_response,
                            url=url,
                            headers=headers,
                            payload=payload,
                            output_file=audio_fp
                        )
                    print(colored(f"\n{ASSISTANT_NAME} said:\n {text_response}", 'green'))
                    print("*" * os.get_terminal_size().columns)
                    play_mp3(audio_fp)

                    record_history(
                        user_prompt=user_prompt,
                        text_response=text_response
                    )
                else:
                    print(colored("Error: No response from the model!", 'red'))
                    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("-t", "--textual", help = "Enable Textual Interaction", action='store_true')
    parser.add_argument("-el", "--el_voice", help = "Enable ElevenLabs Voice", action='store_true')
    args = parser.parse_args()

    conversation_loop(
        textual_interaction=args.textual,
        elevenlabs_voice=args.el_voice
    )