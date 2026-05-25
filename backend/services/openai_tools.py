"""
OpenAI tool/function definitions exposed to the AI agent via Vapi.
The AI calls these; Vapi routes them to our /vapi-webhook endpoint.
"""
from datetime import date, time
from typing import Optional

# ─── Tool JSON schemas (sent to Vapi/OpenAI) ──────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": (
                "Retrieve available appointment time slots for a specific date. "
                "Always call this before offering times to the caller."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format",
                    }
                },
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book an appointment for the caller. "
                "Always confirm the details with the caller before calling this tool."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the person booking",
                    },
                    "phone": {
                        "type": "string",
                        "description": "Phone number of the caller",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format",
                    },
                    "time": {
                        "type": "string",
                        "description": "Start time in HH:MM (24-hour) format",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes or reason for appointment",
                    },
                },
                "required": ["name", "phone", "date", "time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_human",
            "description": (
                "Transfer the call to a human agent when the caller requests it "
                "or when the AI cannot handle the request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for transfer",
                    }
                },
                "required": ["reason"],
            },
        },
    },
]
