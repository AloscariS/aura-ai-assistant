# Nova AI Assistant

Nova is a friendly AI assistant you can use to ask whatever you want. It supports multimodal interaction, including text, audio, and image processing, so you can even ask it to describe what it sees through a connected camera.
You can choose between textual and verbal communication.

---

## 🤖 How to Interact with Nova

* **Wake Word**: Nova stays in standby until you say its name -- then it wakes up and responds.
* **Visual Task Trigger**: sentence with "What do you see" or "Look at the camera" will trigger the image captioning using a photo taken by the connected camera.
* **End the Chat**: Say "Goodbye" to pause the conversation. Nova will return to standby mode, waiting to be called again.

---

## 🚀 Getting Started

Follow these simple steps to get your Nova assistant up and running:

### 1. Clone the Repository

```bash
git clone https://github.com/AloscariS/nova-ai-assistant.git
```

### 2. Open the Project

Open the folder `nova-ai-assistant` in your preferred IDE.

### 3. Set Up the Conda Environment

Make sure you have Conda installed, then create the environment:

```bash
conda env create -f environment.yml
```

### 4. Activate the Environment

```bash
conda activate nova
```

### 5. Configure API Keys

Obtain your API keys from [AIMLAPI](https://aimlapi.com) and [ElevenLabs](https://elevenlabs.io), then create a `.env` file in the root directory of the project.

Example `.env` file:

```
AIML_API_KEY="<your-API-key>"
ELEVENLABS_API_KEY="<your-API-key>"
```

### 6. Run the Assistant

```bash
python assistant.py
```

---

## ⚙️ Customization

You can personalize your experience in several ways:

* **Interaction Mode**: Choose between verbal or textual interaction via CLI arguments.
* **Voice Provider**: Pick between AIMLAPI and ElevenLabs.
* **Assistant Name**: Set a custom name for your assistant.
* **LLM Model Parameters**: Modify the model to interrogate, including temperature, max tokens, etc.
* **Voice Speed**: Adjust speaking speed to your preference.
* **System Prompt**: Customize the assistant's base personality and instructions.

All of these options can be fine-tuned by editing the relevant parts of the `assistant.py` script.

---

Enjoy building with Nova! 🌟
