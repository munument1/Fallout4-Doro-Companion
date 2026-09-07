import asyncio, os, sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=r'C:\Users\seung\.local\bin\uvx.exe',args=['blender-mcp'],env=dict(os.environ,DISABLE_TELEMETRY='true'))
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as s:
            await s.initialize()
            result=await s.call_tool('execute_blender_code',{'code':Path(sys.argv[1]).read_text(encoding='utf-8-sig'),'user_prompt':'Inspect and import the user supplied YaoGuai reference assets in Blender.'})
            for c in result.content:
                if hasattr(c,'text'): print(c.text)
asyncio.run(main())
