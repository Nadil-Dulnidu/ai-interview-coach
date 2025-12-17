from langchain_openai import ChatOpenAI
from app.config.env_config import get_settings, Settings

settings = get_settings()


class OpenAIModel:
    def __init__(self, temperature: float = 0.0):
        self.temperature = temperature

    def create_model(self):
        return ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            temperature=self.temperature,
        )

    def generate_response(self, prompt: str):
        return self.create_model().invoke(prompt)


def get_openai_model() -> ChatOpenAI:
    return OpenAIModel().create_model()


# if __name__ == "__main__":
#     print(get_openai_model().generate_response("Hello, how are you?"))
