from typing import Dict, Any
import aiofiles
from gtts import gTTS
import base64
import logging
from config import Settings

logger = logging.getLogger(__name__)


class OutputProcessor:
    def __init__(self, config: Settings):
        self.config = config

    async def process(self, raw_output: Any, input_type: str) -> Dict[str, Any]:
        if isinstance(raw_output, dict):
            text_output = self._extract_text(raw_output)
        else:
            text_output = str(raw_output)

        processed_output = {
            "text": text_output,
            "type": "text"
        }

        if input_type == 'voice':
            audio_output = await self._text_to_speech(text_output)
            processed_output["audio"] = audio_output
            processed_output["type"] = "voice"

        logger.info(f"Processed output: {processed_output['type']}")
        return processed_output

    def _extract_text(self, output_dict: Dict[str, Any]) -> str:
        if "text" in output_dict:
            return output_dict["text"]
        elif "message" in output_dict:
            return output_dict["message"]
        else:
            return str(output_dict)

    async def _text_to_speech(self, text: str) -> str:
        tts = gTTS(text=text, lang=self.config.tts_language)
        filename = f"{self.config.temp_directory}/output.mp3"
        tts.save(filename)

        async with aiofiles.open(filename, mode='rb') as audio_file:
            audio_data = await audio_file.read()

        return base64.b64encode(audio_data).decode('utf-8')