TOOLS_CONFIG = {
 "files": [{        
     "type": "function",
        "function": {
            "name": "get_answer_from_csv",
            "description": "for getting the job data for whatsapp response",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "the requested data regarding jobs with all the details"}
                },
                "required": ["content"]
            }
        }
    }]
 }

