"""
HCP Tools - Tools for HCP operations
"""

from typing import Dict, Any, Optional
from ..tools.registry import ToolRegistry, ToolDefinition


def register_hcp_tools(registry: ToolRegistry):
    """Register all HCP tools"""

    # search_hcp
    registry.register(
        name="search_hcp",
        func=_search_hcp,
        definition=ToolDefinition(
            name="search_hcp",
            description="Search for healthcare professionals by name, specialty, or institution",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query (name, specialty, or institution)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5,
                },
            },
            required=["query"],
        ),
    )

    # get_hcp_by_id
    registry.register(
        name="get_hcp_by_id",
        func=_get_hcp_by_id,
        definition=ToolDefinition(
            name="get_hcp_by_id",
            description="Get detailed information about a specific HCP by their ID",
            parameters={
                "hcp_id": {
                    "type": "string",
                    "description": "The unique identifier of the HCP",
                }
            },
            required=["hcp_id"],
        ),
    )

    # create_hcp
    registry.register(
        name="create_hcp",
        func=_create_hcp,
        definition=ToolDefinition(
            name="create_hcp",
            description="Register a new healthcare professional in the system",
            parameters={
                "name": {"type": "string", "description": "Full name of the HCP"},
                "specialty": {
                    "type": "string",
                    "description": "Medical specialty (e.g., Oncology, Cardiology)",
                },
                "institution": {
                    "type": "string",
                    "description": "Hospital or clinic name",
                },
                "email": {"type": "string", "description": "Contact email (optional)"},
                "phone": {"type": "string", "description": "Contact phone (optional)"},
            },
            required=["name"],
        ),
    )

    # get_hcp_history
    registry.register(
        name="get_hcp_history",
        func=_get_hcp_history,
        definition=ToolDefinition(
            name="get_hcp_history",
            description="Get interaction history for an HCP",
            parameters={
                "hcp_id": {
                    "type": "string",
                    "description": "The unique identifier of the HCP",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of interactions to return",
                    "default": 10,
                },
            },
            required=["hcp_id"],
        ),
    )


def _search_hcp(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search for HCPs"""
    return {
        "query": query,
        "limit": limit,
        "status": "need_integration",
        "message": f"Search for HCPs matching: {query}",
    }


def _get_hcp_by_id(hcp_id: str) -> Dict[str, Any]:
    """Get HCP by ID"""
    return {
        "hcp_id": hcp_id,
        "status": "need_integration",
        "message": f"Get HCP with ID: {hcp_id}",
    }


def _create_hcp(
    name: str,
    specialty: str = None,
    institution: str = None,
    email: str = None,
    phone: str = None,
) -> Dict[str, Any]:
    """Create new HCP"""
    return {
        "name": name,
        "specialty": specialty,
        "institution": institution,
        "email": email,
        "phone": phone,
        "status": "need_integration",
        "message": f"Create HCP: {name}",
    }


def _get_hcp_history(hcp_id: str, limit: int = 10) -> Dict[str, Any]:
    """Get HCP interaction history"""
    return {
        "hcp_id": hcp_id,
        "limit": limit,
        "status": "need_integration",
        "message": f"Get history for HCP: {hcp_id}",
    }
