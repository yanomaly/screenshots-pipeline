import asyncio
import os

from dotenv import load_dotenv

from screenshots_maker import UIDocumentationScreenshots

load_dotenv()

config = {
    'outputDir': './documentation-screenshots',
    'baseUrl': 'https://app.writer.com',
    'authConfig': {
        'loginUrl': '/login',
        'emailSelector': 'input[name="email"]',
        'passwordSelector': 'input[name="password"]',
        'submitSelector': 'button[type="submit"]',
        'email': os.getenv('ACCOUNT_EMAIL'),
        'password': os.getenv('ACCOUNT_PASSWORD')
    },
}

documentation_flow = [
    # {
    #     'name': 'Creating agent',
    #     'url': '/aistudio/organization/897440',
    #     'actions': [
    #         {
    #             'type': 'screenshot',
    #             'element': {
    #                 'type': 'complex',
    #                 'locator_selector': {
    #                     'type': 'locator',
    #                     'expression': '._header_23eca_7',
    #                 },
    #                 'text_selector': {
    #                     'type': 'text',
    #                     'text': 'Build an agent'
    #                 },
    #             },
    #             'filename': 'agent_creation/build-an-agent-button.png',
    #             'options': {'padding': 10}
    #         },
    #         {
    #             'type': 'click',
    #             'element': {
    #                 'type': 'complex',
    #                 'locator_selector': {
    #                     'type': 'locator',
    #                     'expression': '._header_23eca_7',
    #                 },
    #                 'text_selector': {
    #                     'type': 'text',
    #                     'text': 'Build an agent'
    #                 },
    #             },
    #         },
    #         {
    #             'type': 'screenshot',
    #             'element': {
    #                 'type': 'locator',
    #                 'expression': 'xpath=//div[@tabindex="-1" and @role="dialog"]',
    #             },
    #             'filename': 'agent_creation/type-chose-window.png',
    #             'options': {'padding': 0}
    #         },
    #     ]
    # },
    {
        'name': 'Editing agent',
        'url': '/aistudio/organization/897440/agent/ad695ce6-56b1-491e-9ed7-e7b39ebefeab/deploy',
        'actions': [
            {
                'type': 'screenshot',
                'element': {
                    'type': 'text',
                    'text': "Edit",
                },
                'filename': 'agent_mastering/edit-button.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'text',
                    'text': "Edit",
                },
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'button[data-writer-tooltip="Interface Layers (Ctrl+I)"]'
                },
                'filename': 'agent_mastering/ui-layers.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'button[data-writer-tooltip="Interface Layers (Ctrl+I)"]'
                }
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]'
                },
                'filename': 'agent_mastering/page-button.png',
                'options': {'padding': 50}
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]'
                },
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div[2]/div[3]/button[8]/i'
                },
                'filename': 'agent_mastering/delete-button.png',
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]'
                },
                'filename': 'agent_mastering/ui-tree.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[1]/div[2]/button[2]'
                },
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]'
                },
                'filename': 'agent_mastering/blueprints-root.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]'
                },
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]'
                },
                'filename': 'agent_mastering/blueprints-blank.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[3]/div/button'
                },
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[3]/div/button'
                },
                'filename': 'blueprints_operations/add.png',
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div[2]/div[4]/div[1]/div/div/div/div/div[2]/div/div/input',
                },
                'filename': 'blueprints_operations/set_name.png',
                'options': {'padding': 60}
            },
            {
                'type': 'fill',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div[2]/div[4]/div[1]/div/div/div/div/div[2]/div/div/input',
                },
                'value': 'Name for test pipeline'
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div[2]/div[4]/div[1]/div/div/div/div/div[2]/div/div/input',
                },
                'filename': 'blueprints_operations/set_name_done.png',
                'options': {'padding': 60}
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[1]/div[1]/button[2]/span'
                },
                'filename': 'agent_mastering/add-block.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[1]/div[1]/button[2]/span'
                },
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div'
                },
                'filename': 'agent_mastering/classification.png',
            },
            {
                'type': 'drag',
                'element': {
                    'from':{
                        'type': 'locator',
                        'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div'
                    },
                    'to': {
                        'type': 'locator',
                        'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div/main/div[3]/div/div/div[1]'
                    }
                }
            },
            {
                'type': 'drag',
                'element': {
                    'from': {
                        'type': 'locator',
                        'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/div'
                    },
                    'to': {
                        'type': 'locator',
                        'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div/main/div[3]/div/div/div[1]'
                    }
                }
            },
            {
                'type': 'screenshot',
                'filename': 'agent_mastering/page.png',
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[1]/div[1]/button[1]'
                }
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/span[1]'
                }
            },
            {
                'type': 'click',
                'element': {
                    'type': 'locator',
                    'expression': 'xpath=/html/body/div/div/div[1]/div[3]/div[2]/div[3]/button[8]'
                }
            }
        ]
    }
]
async def run_step(step):
    screenshotter = UIDocumentationScreenshots(config)
    try:
        await screenshotter.initialize()
        await screenshotter.navigate_and_actions(step.get('url', ''), step.get('actions', []))
        print('\n✅ Documentation screenshots completed!')
    except Exception as e:
        print('❌ Error generating screenshots:', e)
    finally:
        await screenshotter.cleanup()

async def main():
    await asyncio.gather(*[run_step(step) for step in documentation_flow])

asyncio.get_event_loop().run_until_complete(main())
