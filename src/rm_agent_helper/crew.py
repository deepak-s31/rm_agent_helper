from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from rm_agent_helper.tools.custom_tool import ResourceResumeAnalyzerTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class RmAgentHelper():
    """RmAgentHelper crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    @agent
    def resource_analyser(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_analyser'],  # type: ignore[index]
            verbose=True,
            tools=[ResourceResumeAnalyzerTool()],
        )

    @task
    def analyse_resource_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyse_resource_task'],  # type: ignore[index]
            agent=self.resource_analyser(),  # type: ignore
        )

    @crew
    def crew(self) -> Crew:
        """Creates the RmAgentHelper crew"""
        return Crew(
            agents=[self.resource_analyser()],  # Automatically created by the @agent decorator
            tasks=[self.analyse_resource_task()],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
