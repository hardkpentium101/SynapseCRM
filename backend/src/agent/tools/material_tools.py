"""
Material Tools - Tools for searching and recommending materials
"""

from typing import Dict, Any, Optional, List
from ..tools.registry import ToolRegistry, ToolDefinition


def register_material_tools(registry: ToolRegistry):
    """Register all material tools"""

    registry.register(
        name="search_materials",
        func=_search_materials,
        definition=ToolDefinition(
            name="search_materials",
            description="Search the material catalog by name, type, or description.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query (material name, type, or description)",
                },
                "material_type": {
                    "type": "string",
                    "description": "Filter by type (pdf, brochure, sample, video, etc.)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 10,
                },
            },
            required=["query"],
        ),
    )

    registry.register(
        name="recommend_materials",
        func=_recommend_materials,
        definition=ToolDefinition(
            name="recommend_materials",
            description="AI-driven material recommendations based on HCP specialty, interaction topics, and engagement context.",
            parameters={
                "hcp_id": {
                    "type": "string",
                    "description": "HCP ID to tailor recommendations",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Discussion topics to match materials against",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context for recommendations",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum recommendations to return",
                    "default": 5,
                },
            },
            required=[],
        ),
    )

    registry.register(
        name="get_material_by_id",
        func=_get_material_by_id,
        definition=ToolDefinition(
            name="get_material_by_id",
            description="Get detailed information about a specific material",
            parameters={
                "material_id": {
                    "type": "string",
                    "description": "The material's unique identifier",
                }
            },
            required=["material_id"],
        ),
    )


def _search_materials(
    query: str, material_type: str = None, limit: int = 10
) -> Dict[str, Any]:
    """Search materials in the catalog"""
    from ..services.tool_services import MaterialService

    results = MaterialService.search_material(query=query, limit=limit)
    if material_type:
        results = [r for r in results if r.get("type", "").lower() == material_type.lower()]
    return {"materials": results, "count": len(results)}


def _recommend_materials(
    hcp_id: str = None,
    topics: List[str] = None,
    context: str = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """AI-driven material recommendations based on context"""
    from ..services.tool_services import MaterialService, HCPService

    all_materials = MaterialService.search_material(query="", limit=50)

    if not all_materials:
        return {"recommendations": [], "count": 0}

    hcp_info = {}
    if hcp_id:
        hcp_info = HCPService.get_hcp_by_id(hcp_id) or {}

    search_terms = []
    if topics:
        search_terms.extend(topics)
    if hcp_info.get("specialty"):
        search_terms.append(hcp_info["specialty"])
    if context:
        search_terms.extend(context.split())

    scored = []
    for material in all_materials:
        score = 0
        name = (material.get("name") or "").lower()
        desc = (material.get("description") or "").lower()
        text = f"{name} {desc}"

        for term in search_terms:
            term_lower = term.lower()
            if term_lower in text:
                score += 2
            elif any(word in text for word in term_lower.split()):
                score += 1

        if hcp_info.get("specialty") and hcp_info["specialty"].lower() in text:
            score += 3

        scored.append((score, material))

    scored.sort(key=lambda x: x[0], reverse=True)
    recommendations = [{"score": s, **m} for s, m in scored[:limit] if s > 0]

    if not recommendations:
        recommendations = [m for _, m in scored[:limit]]
        for r in recommendations:
            r["score"] = 0

    return {
        "recommendations": recommendations,
        "count": len(recommendations),
        "hcp_specialty": hcp_info.get("specialty"),
        "topics_used": search_terms,
    }


def _get_material_by_id(material_id: str) -> Dict[str, Any]:
    """Get material by ID"""
    from ..services.tool_services import MaterialService

    result = MaterialService.get_material_by_id(material_id)
    if result:
        return result
    return {"error": f"Material {material_id} not found"}
