# Personal Website (in progress)

My personal website built using Django. It's a full-stack application with a blog, real-time chat, and API integrations.

## Purpose

Serves as my portfolio and blog. The most interesting feature is the real-time chat (hangout) that bridges visitors with my Discord channel. Messages flow both ways instantly using WebSockets.

It also integrates with several APIs to display live data: Discord status via Lanyard, current music from Last.fm, coding stats from WakaTime, GitHub contributions, and recent Mastodon post. Everything is cached in Redis for performance.

The blog supports Markdown articles with commenting and RSS feed. Custom analytics middleware tracks unique visitors and filters out bots.

## Stack

Django 5.2 with Channels for WebSocket support. PostgreSQL for data storage. Redis handles caching, channel layers, and Celery task queues. Daphne serves as the ASGI server in production.

The Discord bot runs as a separate process using discord.py. It communicates with the web app through Redis pub/sub.

Frontend is vanilla JavaScript with a simple pixel art design. No frameworks, just HTML, CSS & JavaScript.

## Architecture

The real-time chat uses Django Channels WebSockets. When someone sends a message, it saves to the database, broadcasts to all connected clients via channel layers, and publishes to Redis. The Discord bot picks it up and forwards it to Discord. The reverse happens for Discord messages.

API integrations follow a base service pattern with automatic caching. Each service implements a fetch method and defines its cache timeout. Celery beat runs scheduled tasks to refresh data at different intervals based on how frequently it changes (Last.fm every 50 seconds, Discord status every 4 minutes, GitHub every 2 hours).

Analytics middleware tracks visitors count by IP with a 5-minute cache interval to prevent duplicate counting. It filters bots using user agent patterns and blocks known monitoring service IP ranges.

## Deployment

Currently on Heroku. The Procfile runs Daphne for the web process and Celery with beat for background tasks. Static files served via WhiteNoise. Environment variables handle all configuration.

## Why This Stack

I wanted to learn WebSockets and Redis pub/sub, so bridging web chat with Discord was a good learning project. Django + Channels made async programming approachable without switching to a different framework.

Celery handles scheduled API refreshes reliably. The project structure keeps code organized and makes adding features straightforward.

Keeping the frontend simple was intentional. No build tools, no complexity. Just load the page and everything works.

## Future

~~The WebSocket connection doesn't handle reconnection gracefully. If the connection drops, users have to refresh the page. Adding automatic reconnection would improve user experience.~~

~~Error handling for API failures could be better. For now, if an integration fails, it just shows placeholder data.~~

Mobile experience works but leaves a lot to be desired. It's just the desktop layout scaled down. A responsive design would improve usability.

Some code could use refactoring.
