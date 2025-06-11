import asyncio
import os

from dotenv import load_dotenv

from screenshots_maker import UIDocumentationScreenshots

load_dotenv()

config = {
    'outputDir': './documentation-screenshots',
    'authConfig': {
        'type': 'form',
        'loginUrl': 'https://app.writer.com/organization/897440',
        'emailSelector': 'input[name="email"]',
        'passwordSelector': 'input[name="password"]',
        'submitSelector': 'button[type="submit"]',
        'email': os.getenv('ACCOUNT_EMAIL'),
        'password': os.getenv('ACCOUNT_PASSWORD')
    }
}

documentation_flow = [
    {
        'name': 'Test exception button',
        'url': 'https://app.writer.com/login',
        'actions': [
            {
                'type': 'screenshot',
                'filename': 'test-folder/login.png'
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'locator',
                    'expression': 'input[name="email"]',
                },
                'filename': 'email-input.png',
                'options': {'padding': 25}
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'text',
                    'text': 'Sign in to your',
                    'options': {'match': 'partial'}
                },
                'filename': 'sign-in-text.png',
            },
            {
                'type': 'screenshot',
                'element': {
                    'locator_selector': {
                        'type': 'locator',
                        'expression': 'button'
                    },
                    'type': 'complex',
                    'text_selector': {
                        'type': 'text',
                        'text': 'Sign in with Google',
                        'options': {'match': 'exact'}
                    },
                },
                'filename': 'sign-in-complex-search.png',
                'options': {'padding': 10, 'crop': 'element'}
            },
        ]
    },
    #other chains
]

async def run_step(step):
    screenshotter = UIDocumentationScreenshots(config)
    try:
        await screenshotter.initialize()
        await screenshotter.authenticate()
        await screenshotter.navigate_and_actions(step.get('url', ''), step.get('actions', ''))
        await asyncio.sleep(20)
        print('\n✅ Documentation screenshots completed!')
    except Exception as e:
        print('❌ Error generating screenshots:', e)
    finally:
        await screenshotter.cleanup()

async def main():
    await asyncio.gather(*[run_step(step) for step in documentation_flow])

asyncio.get_event_loop().run_until_complete(main())
