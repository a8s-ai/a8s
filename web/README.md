# A8s: AI Agent Desktop Environment Platform

<p align="center">
  An AI-powered platform enabling users to interact with agents through chat while providing access to remote desktop environments.
</p>

<p align="center">
  <a href="#overview"><strong>Overview</strong></a> ·
  <a href="#features"><strong>Features</strong></a> ·
  <a href="#technology-stack"><strong>Technology Stack</strong></a> ·
  <a href="#architecture"><strong>Architecture</strong></a> ·
  <a href="#running-locally"><strong>Running Locally</strong></a> ·
  <a href="#deployment"><strong>Deployment</strong></a>
</p>
<br/>

## Overview

A8s (Agents) is a Proof of Concept (PoC) demonstrating a web-based system that enables users to interact with AI agents through a chat interface while also providing access to remote desktop environments that the agents can control. The system allows for parallel agent operations, state preservation, and direct user intervention.

The platform bridges the gap between natural language interactions with AI and visual desktop-based tasks, allowing agents to perform operations in sandboxed environments while users observe or intervene as needed.

## Features

### Implemented Features

- **Chat Interface**
  - Next.js-based modern chat UI
  - Support for multimodal inputs
  - Responsive design for mobile and desktop
  - Built with Tailwind CSS and Shadcn UI

- **Interactive Desktop Environment**
  - Remote desktop streaming embedded as artifacts in chat
  - noVNC-based iframe integration
  - Seamless animations between chat and desktop view
  - Support for various URL formats from deployment results
  - Error handling and loading states

### Planned Features

- **Chat Agent**
  - General chat agent that converses with the user to understand requirements
  - Support for various storage items (documents, SaaS connections, artifacts)
  - Handoff to overseer agent for new workflows

- **Overseer Agent**
  - Decides which agent template and tools to inject into a containerized desktop environment
  - Provisions the environment with gathered information

- **Agent Environment**
  - Communication with AI agents inside each desktop environment
  - Credentials provision for external services access
  - Additional context and tool requests

- **Parallelization and Multi-session Support**
  - Multiple concurrent agent sessions
  - Independent parallel execution tracks
  - Multi-user support with authentication/authorization

- **Agent Control and Interaction**
  - Ability to interrupt and redirect agent tasks
  - Toggle between observation and direct interaction modes
  - Handoff between agent control and user control

- **State Management**
  - Environment state snapshots and restoration points
  - Recovery from errors by returning to previous states
  - Persistent state storage across sessions

- **Artifact Extraction/Output**
  - Ability to extract and download outputs (PDFs, websites, etc.)
  - Result persistence independent of environment state

## Technology Stack

### Frontend
- [Next.js](https://nextjs.org) with App Router
- [Vercel AI SDK](https://sdk.vercel.ai/docs) for LLM integration
- [Tailwind CSS](https://tailwindcss.com) and [Shadcn UI](https://ui.shadcn.com) for styling
- [noVNC](https://novnc.com) WebSocket-based VNC client for remote desktop
- React Context + SWR for state management
- [NextAuth.js](https://next-auth.js.org) for authentication

### Backend (Planned)
- FastAPI microservices
- Server-Sent Events (SSE) for chat streaming
- WebSockets for remote desktop interactions
- Agno framework for AI agent orchestration
- Kubernetes with custom operator for container orchestration

### Data Layer (Planned)
- PostgreSQL for metadata and persistence
- Redis for session management
- Persistent volumes for environment state

## Architecture

The system is designed with a microservices architecture:

### Microservices
- **Auth Service**: User authentication and session management
- **Agent Service**: Chat processing and task analysis
- **Environment Orchestrator (Overseer)**: Desktop environment management
- **Streaming Service**: noVNC proxy for browser-based VNC access
- **State Management Service**: Environment state snapshots and recovery

### Component Interaction
1. **Chat and Environment Coordination**
   - User → Chat Interface → Agent Service → Task Analysis → Environment Orchestrator
   
2. **Desktop Interaction Flow**
   - Agent Instruction → Agno Framework → Desktop Actions → VNC/RDP Protocol → User

3. **State Management Flow**
   - Snapshot Trigger → Environment Orchestrator → Container Snapshot → Persistent Storage

## Running Locally

### Prerequisites
- Node.js 18+ and npm/pnpm
- Docker (for local development of containerized environments)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/a8s-ai/a8s.git
   cd a8s
   ```

2. Install dependencies
   ```bash
   npm install
   # or
   pnpm install
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your configuration values.

4. Start the development server
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

The application should now be running on [localhost:3000](http://localhost:3000/).

## Deployment

### Vercel Deployment

You can deploy the frontend to Vercel with one click:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fa8s-ai%2Fa8s)

### Kubernetes Deployment (Planned)

The complete system with backend services will support Kubernetes deployment. Documentation for this will be available once implemented.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
