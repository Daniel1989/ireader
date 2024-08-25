import os
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from django.utils import timezone
from django_ai_assistant import AIAssistant, method_tool, BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

import json

class WeatherAIAssistant(AIAssistant):
    id = "assistant"
    name = "Assistant"
    instructions = "You are a Hacker News reader bot."
    model = os.environ["MODEL_NAME"]

    def get_instructions(self):
        return f"{self.instructions}"

    class FetchForecastWeatherInput(BaseModel):
        location: str = Field(description="Location to fetch the forecast weather for")
        forecast_date: date = Field(description="Date in the format 'YYYY-MM-DD'")

    @method_tool
    def get_weather(self, location: str) -> str:
        """Fetch the current weather data for a location"""
        print(location)
        return json.dumps({
            "location": location,
            "temperature": "25°C",
            "weather": "sunny"
        })

    @method_tool
    def get_location(self, location: str) -> str:
        """Fetch the longitude and latitude for a city"""
        return json.dumps({
            "longitude": "38",
            "latitude": "120"
        })

    @method_tool
    def check_if_ask_for_new_ideas(self) -> str:
        """Based on the user's input, check if they want to ask for new ideas"""
        return json.dumps({
            "longitude": "38",
            "latitude": "120"
        })

    def get_llm(self):
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()
        base_url = os.environ["BASE_URL"]
        api_key = os.environ["SERVERLESS_API_KEY"]
        client = ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model_name=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
            timeout=None,
            max_retries=2,
            verbose=True,
        )
        return client


class MovieSearchAIAssistant(AIAssistant):
    id = "movie_search_assistant"  # noqa: A003
    instructions = (
        "You're a helpful movie search assistant. "
        "Help the user find more information about movies. "
        "Use the provided tools to search the web for upcoming movies. "
    )
    name = "Movie Search Assistant"
    model = os.environ["MODEL_NAME"]

    def get_instructions(self):
        return f"{self.instructions} Today is {timezone.now().isoformat()}."

    def get_tools(self):
        return [
            TavilySearchResults(),
            *super().get_tools(),
        ]

## 获得历史会话
# from django_ai_assistant.use_cases import create_thread, get_thread_messages
#
# thread = create_thread(name="Weather Chat", user=user)
# assistant = WeatherAIAssistant()
# assistant.run("What's the weather in New York City?", thread_id=thread.id)
#
# messages = get_thread_messages(thread=thread, user=user)

## rag
# from langchain_community.retrievers import TFIDFRetriever
# from langchain_core.retrievers import BaseRetriever
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from django_ai_assistant import AIAssistant
# from rag.models import DjangoDocPage
# class DjangoDocsAssistant(AIAssistant):
#     id = "django_docs_assistant"  # noqa: A003
#     name = "Django Docs Assistant"
#     instructions = (
#         "You are an assistant for answering questions related to Django web framework. "
#         "Use the following pieces of retrieved context from Django's documentation to answer "
#         "the user's question. If you don't know the answer, say that you don't know. "
#         "Use three sentences maximum and keep the answer concise."
#         "\n\n"
#         "---START OF CONTEXT---\n"
#         "{context}"
#         "---END OF CONTEXT---\n"
#     )
#     model = "gpt-4o"
#     has_rag = True
#
#     def get_retriever(self) -> BaseRetriever:
#         # NOTE: on a production application, you should persist or cache the retriever,
#         # updating it only when documents change.
#         docs = (page.as_langchain_document() for page in DjangoDocPage.objects.all())
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         splits = text_splitter.split_documents(docs)
#         return TFIDFRetriever.from_documents(splits)
# more details
# https://vintasoftware.github.io/django-ai-assistant/latest/tutorial/#threads-of-messages

# 主要功能
# 1. 在一个ai assistant里通过method_tools或者get tools注册方法
# 2. 使用run就会调用这个方法
# 3. 有历史会话
# 4. 支持rag