from jsonschema import *


schema = {
    "type": "object",
    "properties": {
        "task_number": {  # number of tasks
            "type": "integer",
            "minimum": 0,
            "exclusiveMinimum": True
        },
        "developer_number": {  # number of developers
            "type": "integer",
            "minimum": 0,
            "exclusiveMinimum": True
        },
        "expert_weight": {"type": "number"},  # weight for the expert
        "developers": {  # developers array
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "developer_id": {"type": "integer"},
                    "estimate": {  # the estimation of the tasks for each developer
                        "type": "array",
                        "item": {  # each estimation
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "integer"},
                                "est_value": {
                                    "type": "number",
                                    "minimum": 0,
                                    "exclusiveMinimum": True
                                }
                            },
                            "required": ["task_id", "est_value"]
                        }
                    },
                    "expert_vote": {  # vote of expert for each developer
                        "type": "array",
                        "item": {
                            "type": "object",
                            "properties": {
                                "candidate_id": {"type": "integer"},
                                "priority": {"type": "integer"}
                            },
                            "required": ["candidate_id", "priority"]
                        }
                    }
                },
                "required": ["developer_id", "estimate", "expert_vote"]
            }
        }
    },
    "required": ["task_number", "developer_number", "expert_weight", "developers"]
}


if __name__ == '__main__':
    test_input = {
        "task_number": 3,
        "developer_number": 3,
        "expert_weight": 0.6,
        "developers": [
            {
                "developer_id": 0,
                "estimate": [
                    {
                        "task_id": 0,
                        "est_value": 3
                    },
                    {
                        "task_id": 1,
                        "est_value": 4
                    },
                    {
                        "task_id": 2,
                        "est_value": 3
                    }
                ],
                "expert_vote": [
                    {
                        "candidate_id": 0,
                        "priority": 1
                    },
                    {
                        "candidate_id": 1,
                        "priority": 2
                    }
                ]
            },
            {
                "developer_id": 1,
                "estimate": [
                    {
                        "task_id": 0,
                        "est_value": 3
                    },
                    {
                        "task_id": 1,
                        "est_value": 4
                    },
                    {
                        "task_id": 2,
                        "est_value": 3
                    }
                ],
                "expert_vote": [
                    {
                        "candidate_id": 0,
                        "priority": 1
                    },
                    {
                        "candidate_id": 1,
                        "priority": 2
                    }
                ]
            }
        ]
    }
    validate(test_input, schema)
