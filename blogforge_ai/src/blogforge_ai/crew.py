from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, LLM, Process, Task
from crewai_tools import SerperDevTool

from blogforge_ai.config import settings

CONFIG_DIR = Path(__file__).parent / "config"


def _load_yaml(name: str) -> dict[str, Any]:
    return yaml.safe_load((CONFIG_DIR / name).read_text(encoding="utf-8"))


class BlogForgeCrew:
    """CrewAI orchestration for planning, writing, reviewing and preparing blog visuals."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.agents_config = _load_yaml("agents.yaml")
        self.tasks_config = _load_yaml("tasks.yaml")
        self.search_tool = SerperDevTool(n_results=5)

    def _llm(self, model: str) -> LLM:
        return LLM(
            model=model,
            api_key=settings.groq_api_key,
            temperature=0.7,
            cache={
                "no-cache": True,
                "no-store": True,
            },
        )

    def content_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["content_planner"],
            llm=self._llm(settings.planner_model),
            tools=[self.search_tool],
            verbose=self.verbose,
            allow_delegation=False,
        )

    def blog_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["blog_writer"],
            llm=self._llm(settings.writer_model),
            verbose=self.verbose,
            allow_delegation=False,
        )

    def editor_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["editor_reviewer"],
            llm=self._llm(settings.editor_model),
            verbose=self.verbose,
            allow_delegation=False,
        )

    def image_director(self) -> Agent:
        return Agent(
            config=self.agents_config["image_director"],
            llm=self._llm(settings.editor_model),
            verbose=self.verbose,
            allow_delegation=False,
        )

    def crew(self) -> Crew:
        planner = self.content_planner()
        writer = self.blog_writer()
        editor = self.editor_reviewer()
        visual = self.image_director()

        planning_task = Task(config=self.tasks_config["planning_task"], agent=planner)
        writing_task = Task(config=self.tasks_config["writing_task"], agent=writer, context=[planning_task])
        review_task = Task(config=self.tasks_config["review_task"], agent=editor, context=[writing_task])
        image_prompt_task = Task(config=self.tasks_config["image_prompt_task"], agent=visual, context=[review_task])

        return Crew(
            agents=[planner, writer, editor, visual],
            tasks=[planning_task, writing_task, review_task, image_prompt_task],
            process=Process.sequential,
            verbose=self.verbose,
        )

    def kickoff(self, inputs: dict[str, Any]):
        return self.crew().kickoff(inputs=inputs)
