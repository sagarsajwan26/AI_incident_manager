import asyncio
from app.ai.ollama_provider import OllamaProvider

async def test():
    provider = OllamaProvider()
    try:
        print(await provider.generate('Hello'))
    except Exception as e:
        print(f"Exception caught: {type(e)}")
        print(e)

if __name__ == "__main__":
    asyncio.run(test())
