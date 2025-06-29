import os

from dotenv import load_dotenv

load_dotenv()

config_dict = {
    "base_output_dir": "./documentation-screenshots",
    "base_url": "https://app.writer.com",
    "auth_config": {
        "login_url": "/login",
        "email_selector": 'input[name="email"]',
        "password_selector": 'input[name="password"]',
        "submit_selector": 'button[type="submit"]',
        "email": os.getenv("ACCOUNT_EMAIL"),
        "password": os.getenv("ACCOUNT_PASSWORD"),
    },
}

documentation_flow_dict = {
    "chains": [
        {
            "name": "Creating agent",
            "url": "/aistudio/organization/897440",
            "actions": [
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "complex",
                            "locator_selector": {
                                "type": "locator",
                                "expression": "._header_23eca_7",
                            },
                            "text_selector": {"type": "text", "text": "Build an agent"},
                        }
                    ],
                    "filename": "/agent_creation/build-an-agent-button.png",
                    "note": "/agent_creation/build-an-agent-button.png",
                    "padding": 10,
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "complex",
                            "locator_selector": {
                                "type": "locator",
                                "expression": "._header_23eca_7",
                            },
                            "text_selector": {"type": "text", "text": "Build an agent"},
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": 'xpath=//div[@tabindex="-1" and @role="dialog"]',
                        }
                    ],
                    "filename": "/agent_creation/type-chose-window.png",
                    "note": "/agent_creation/type-chose-window.png",
                    "padding": 0,
                },
            ],
        },
        {
            "name": "Editing agent",
            "url": "/aistudio/organization/897440/agent/ad695ce6-56b1-491e-9ed7-e7b39ebefeab/deploy",
            "actions": [
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "text",
                            "text": "Edit",
                        }
                    ],
                    "filename": "/agent_mastering/edit-button.png",
                    "note": "/agent_mastering/edit-button.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "text",
                            "text": "Edit",
                        }
                    ],
                    "new_page_handling_required": True,
                    "new_page_handling_timeout": 10,
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[1]/div[2]/button[1]",
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": 'button[data-writer-tooltip="Interface Layers (Ctrl+I)"]',
                        }
                    ],
                    "filename": "/agent_mastering/ui-layers.png",
                    "note": "/agent_mastering/ui-layers.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": 'button[data-writer-tooltip="Interface Layers (Ctrl+I)"]',
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]",
                        }
                    ],
                    "filename": "/agent_mastering/page-button.png",
                    "note": "/agent_mastering/page-button.png",
                    "padding": 50,
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]",
                        }
                    ],
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/div/button",
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/div/button",
                        }
                    ],
                    "filename": "/agent_mastering/options-button.png",
                    "note": "/agent_mastering/options-button.png",
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/div/div/button[8]",
                        }
                    ],
                    "filename": "/agent_mastering/delete-button.png",
                    "note": "/agent_mastering/delete-button.png",
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]",
                        }
                    ],
                    "filename": "/agent_mastering/ui-tree.png",
                    "note": "/agent_mastering/ui-tree.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[1]/div[2]/button[2]",
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]",
                        }
                    ],
                    "filename": "/agent_mastering/blueprints-root.png",
                    "note": "/agent_mastering/blueprints-root.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]",
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]",
                        }
                    ],
                    "filename": "/agent_mastering/blueprints-blank.png",
                    "note": "/agent_mastering/blueprints-blank.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[3]/div/button",
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[3]/div/button",
                        }
                    ],
                    "filename": "/blueprints_operations/add.png",
                    "note": "/blueprints_operations/add.png",
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[1]/div/div/div/div/div[2]/div",
                        }
                    ],
                    "filename": "/blueprints_operations/set_name.png",
                    "note": "/blueprints_operations/set_name.png",
                    "padding": 60,
                },
                {
                    "type": "fill",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[1]/div/div/div/div/div[2]/div/div/input",
                        }
                    ],
                    "action_kwargs": {"value": "Name for test pipeline"},
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[1]/div/div/div/div/div[2]/div",
                        }
                    ],
                    "filename": "/blueprints_operations/set_name_done.png",
                    "note": "/blueprints_operations/set_name_done.png",
                    "padding": 60,
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[1]/div[1]/button[2]/span",
                        }
                    ],
                    "filename": "/agent_mastering/add-block.png",
                    "note": "/agent_mastering/add-block.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[1]/div[1]/button[2]/span",
                        }
                    ],
                },
                {
                    "type": "screenshot",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div",
                        }
                    ],
                    "filename": "/agent_mastering/classification.png",
                    "note": "/agent_mastering/classification.png",
                },
                {
                    "type": "drag_to",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/div",
                        },
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[3]/div[1]/div/div/main/div[3]",
                        },
                    ],
                },
                {
                    "type": "drag_to",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/div",
                        },
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[3]/div[1]/div/div/main/div[3]",
                        },
                    ],
                },
                {
                    "type": "screenshot",
                    "filename": "/agent_mastering/page.png",
                    "note": "/agent_mastering/page.png",
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[1]/div[1]/button[1]",
                        }
                    ],
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/span[1]",
                        }
                    ],
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/div/button",
                        }
                    ],
                },
                {
                    "type": "click",
                    "element_selector": [
                        {
                            "type": "locator",
                            "expression": "xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/div/div/button[8]",
                        }
                    ],
                    "note": "Clicking 'Delete' button on the created blueprint",
                },
            ],
        },
    ]
}
