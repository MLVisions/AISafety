 """
 run_full_update.py

 This script serves as the entry point for executing the full update
 pipeline defined in `crew_agents.py`.  It builds the crew, kicks
 off the process and prints or logs the final result.  Running this
 script manually will perform a complete cycle of summarisation,
 research, evaluation, content generation, validation and deployment.

 Usage:

   python run_full_update.py

 The script assumes that environment variables for any API keys (e.g.,
 GPT API) are already set.  To restrict API costs, schedule this
 command (e.g., via cron) to run weekly after new content has been
 uploaded.
 """

 from crew_agents import build_crew


 def main() -> None:
     crew = build_crew()
     # Kick off the crew.  The run() method orchestrates the tasks in
     # sequence, passing the outputs to dependent tasks.  It returns
     # whatever the final task yields.  For debugging, set
     # verbose=True in the Crew definition to see agent messages.
     final_result = crew.run()
     print("=== Update complete ===")
     print(final_result)


 if __name__ == "__main__":
     main()