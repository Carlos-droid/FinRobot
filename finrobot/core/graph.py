from typing import Annotated, List, Optional, TypedDict
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..agents.schemas import (
    MacroSignal, SectorSignal, PhilosophySignal, 
    RiskAssessment, FinalDecision
)

class PipelineState(TypedDict):
    """LangGraph state for the FinRobot x ATLAS pipeline."""
    # Annotate with operator.add to allow multiple agents to append to the list
    macro_signals: Annotated[List[MacroSignal], operator.add]
    sector_signals: Annotated[List[SectorSignal], operator.add]
    philosophy_signals: Annotated[List[PhilosophySignal], operator.add]
    
    cro_assessment: Optional[RiskAssessment]
    final_decision: Optional[FinalDecision]
    
    error: Optional[str]
    metadata: dict

def create_pipeline_graph():
    """Factory to create the FinRobot x ATLAS StateGraph."""
    workflow = StateGraph(PipelineState)
    
    # Nodes will be added as we implement the agents in Phase 4
    # For now, we define the structure
    
    # Placeholder node functions (will be replaced by actual agent calls)
    async def layer1_macro(state: PipelineState) -> PipelineState:
        return state

    async def layer2_sector(state: PipelineState) -> PipelineState:
        return state

    async def layer3_philosophy(state: PipelineState) -> PipelineState:
        return state

    async def layer4_cro(state: PipelineState) -> PipelineState:
        return state

    async def layer4_cio(state: PipelineState) -> PipelineState:
        return state

    def route_after_cro(state: PipelineState) -> str:
        assessment: Optional[RiskAssessment] = state.get("cro_assessment")
        if assessment and assessment.block_execution:
            return "end"
        return "cio"

    # Add nodes
    workflow.add_node("macro", layer1_macro)
    workflow.add_node("sector", layer2_sector)
    workflow.add_node("philosophy", layer3_philosophy)
    workflow.add_node("cro", layer4_cro)
    workflow.add_node("cio", layer4_cio)

    # Define edges
    workflow.add_edge("macro", "sector")
    workflow.add_edge("sector", "philosophy")
    workflow.add_edge("philosophy", "cro")
    
    workflow.add_conditional_edges(
        "cro",
        route_after_cro,
        {
            "cio": "cio",
            "end": END
        }
    )
    workflow.add_edge("cio", END)

    # Set entry point
    workflow.set_entry_point("macro")
    
    # Compile with memory checkpointer for now
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
