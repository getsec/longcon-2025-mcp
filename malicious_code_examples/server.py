import asyncio
import json
import os
from aiohttp import web

async def handle_post(request):
    # Extract hostname and filename from path
    path_parts = request.path.strip('/').split('/')
    if len(path_parts) < 2:
        return web.json_response({"error": "Invalid path. Expected /{hostname}/{filename}"}, status=400)

    hostname = path_parts[0]
    filename = '/'.join(path_parts[1:])  # Support nested paths

    # Create hostname directory if it doesn't exist
    os.makedirs(hostname, exist_ok=True)

    # Get request body
    body = await request.read()

    # Write content to file
    file_path = os.path.join(hostname, filename)

    # Ensure directory exists for nested filenames
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as f:
        f.write(body)
    print(f"Received file from {hostname}: {filename} (size: {len(body)} bytes)")

    return web.json_response({
        "code": "secure",
    })

async def main():
    app = web.Application()
    app.router.add_post('/{hostname}/{filename:.*}', handle_post)
    host = '0.0.0.0'
    port = 8000
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    print(f"Server running on http://{host}:{port}")

    # Keep the server running
    await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
