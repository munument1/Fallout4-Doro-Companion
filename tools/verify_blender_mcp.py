import asyncio, os, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    env = dict(os.environ, DISABLE_TELEMETRY='true')
    params = StdioServerParameters(command=r'C:\Users\seung\.local\bin\uvx.exe', args=['blender-mcp'], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print('SERVER', init.serverInfo)
            listed = await session.list_tools()
            print('TOOLS', [t.name for t in listed.tools])
            tool = next(t for t in listed.tools if t.name == 'get_scene_info')
            print('SCHEMA', json.dumps(tool.inputSchema))
            result = await session.call_tool(tool.name, {'user_prompt':'Verify Blender MCP connection and read scene information only.'})
            print('SCENE', result.model_dump_json())
asyncio.run(main())
