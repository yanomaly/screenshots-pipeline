import asyncio

from inputs import config_dict, documentation_flow_dict
from schemas.config import Config
from schemas.flow import Chain, Flow
from screenshots_maker import UIDocumentationScreenshots

config = Config.model_validate(config_dict)
flow = Flow.model_validate(documentation_flow_dict)


async def run_chain(chain: Chain):
    screenshotter = UIDocumentationScreenshots(config)
    try:
        await screenshotter.process_chain(chain)
        print(f"{chain.name} | ✅ Documentation screenshots completed!")
    except Exception as e:
        print(f"{chain.name} | ❌ Error generating screenshots:", e)
    finally:
        await screenshotter.cleanup()


async def main():
    await asyncio.gather(*[run_chain(chain) for chain in flow.chains])


asyncio.get_event_loop().run_until_complete(main())
