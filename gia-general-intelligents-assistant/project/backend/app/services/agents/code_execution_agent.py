import docker
from typing import Dict, Any
import asyncio
import tempfile
import os
from loguru import logger
from .base_agent import BaseAgent

class CodeExecutionAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.docker_client = docker.from_env()
        self.timeout = config.get("timeout", 30) if config else 30

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        code = task_input.get("code")
        language = task_input.get("language", "python")
        
        if not code:
            return {"status": "error", "error": "No code provided"}
        
        try:
            result = await self._execute_in_container(code, language)
            return {
                "status": "success",
                "result": result,
                "language": language
            }
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_in_container(self, code: str, language: str) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            file_extension = ".py" if language == "python" else ".txt"
            source_file = os.path.join(temp_dir, f"source{file_extension}")
            
            with open(source_file, "w") as f:
                f.write(code)
            
            # Configure container
            container_config = {
                "image": "python:3.9-slim",
                "command": f"python /code/source{file_extension}",
                "volumes": {
                    temp_dir: {
                        "bind": "/code",
                        "mode": "ro"
                    }
                },
                "mem_limit": "100m",
                "cpu_period": 100000,
                "cpu_quota": 50000,
                "network_disabled": True
            }
            
            try:
                container = self.docker_client.containers.run(
                    **container_config,
                    detach=True
                )
                
                # Wait for execution with timeout
                try:
                    await asyncio.wait_for(
                        self._wait_for_container(container),
                        timeout=self.timeout
                    )
                    
                    logs = container.logs().decode()
                    exit_code = container.wait()["StatusCode"]
                    
                    return {
                        "output": logs,
                        "exit_code": exit_code,
                        "execution_time": self.timeout  # Approximate
                    }
                    
                except asyncio.TimeoutError:
                    container.kill()
                    return {
                        "error": "Execution timeout",
                        "timeout": self.timeout
                    }
                    
            finally:
                try:
                    container.remove(force=True)
                except Exception as e:
                    logger.error(f"Error removing container: {str(e)}")

    async def _wait_for_container(self, container) -> None:
        while container.status != "exited":
            await asyncio.sleep(0.1)
            container.reload()