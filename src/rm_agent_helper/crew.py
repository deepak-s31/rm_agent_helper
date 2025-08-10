from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
import json
from rm_agent_helper.report import generate_html_report
from rm_agent_helper.utils import coerce_result_to_json_text, normalize_candidates_json
from rm_agent_helper.enrich import load_resume_texts, enrich_candidates
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

    @after_kickoff
    def _persist_reports(self, result):
        def _coerce_to_json_text(result_obj) -> str:
            try:
                if isinstance(result_obj, str):
                    return result_obj
                if isinstance(result_obj, (list, dict)):
                    return json.dumps(result_obj)
                for attr in ["raw", "raw_output", "output", "final_output", "json"]:
                    if hasattr(result_obj, attr):
                        value = getattr(result_obj, attr)
                        if callable(value):
                            try:
                                value = value()
                            except Exception:
                                continue
                        if isinstance(value, str):
                            return value
                        if isinstance(value, (list, dict)):
                            return json.dumps(value)
                if hasattr(result_obj, "to_json") and callable(getattr(result_obj, "to_json")):
                    try:
                        return result_obj.to_json()
                    except Exception:
                        pass
                text = str(result_obj).strip()
                if text.startswith("[") or text.startswith("{"):
                    return text
            except Exception:
                pass
            return "[]"

        os.makedirs("output", exist_ok=True)
        output_json = os.path.join("output", "resource_report.json")
        output_html = os.path.join("output", "resource_report.html")

        json_text = coerce_result_to_json_text(result)
        json_text_stripped = (json_text or "").strip()
        should_overwrite = True
        if json_text_stripped == "[]" and os.path.exists(output_json):
            try:
                if os.path.getsize(output_json) > 2:
                    should_overwrite = False
            except Exception:
                should_overwrite = True

        try:
            if should_overwrite:
                final_json_text = normalize_candidates_json(json_text)
                # Enrich missing info using simple heuristics
                try:
                    data = json.loads(final_json_text)
                    if isinstance(data, list):
                        texts = load_resume_texts()
                        data = enrich_candidates(data, texts)
                        final_json_text = json.dumps(data)
                except Exception:
                    pass
                with open(output_json, "w", encoding="utf-8") as f:
                    f.write(final_json_text)
                print(f"Saved consolidated report to {output_json}")
            else:
                print(f"Kept existing non-empty report at {output_json}")
        except Exception as e:
            print(f"Warning: failed to write JSON report: {e}")

        try:
            generate_html_report(output_json, output_html)
            print(f"Saved HTML report to {output_html}")
        except Exception as e:
            print(f"Warning: failed to generate HTML report: {e}")
