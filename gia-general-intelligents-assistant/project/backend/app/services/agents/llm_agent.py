from typing import Dict, Any, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger
from .base_agent import BaseAgent

class LLMAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing LLM Agent with device: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto"
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading LLM model: {str(e)}")
            raise

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = task_input.get("prompt", "")
            if not prompt:
                return {"status": "error", "error": "No prompt provided"}

            # Format the prompt for instruction-based model
            formatted_prompt = f"""<s>[INST] {prompt} [/INST]"""

            # Generate response
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                inputs["input_ids"],
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the response after the instruction
            response = response.split("[/INST]")[-1].strip()

            return {
                "status": "success",
                "response": response,
                "model": self.model_name,
                "device": self.device
            }

        except Exception as e:
            logger.error(f"Error executing LLM task: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def cleanup(self):
        """Clean up GPU memory if needed"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("LLM Agent cleaned up")