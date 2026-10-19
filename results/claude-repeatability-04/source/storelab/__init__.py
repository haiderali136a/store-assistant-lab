"""Synthetic commerce workflow experiment; no connection to a live store."""
import os

# This lab writes traces locally, including when a shell enables hosted tracing.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
