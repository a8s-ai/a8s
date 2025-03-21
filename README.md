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

## Project Structure

The project is organized into several key components:

- **`/web`**: Next.js frontend application with chat interface and remote desktop embedding
- **`/overseer`**: FastAPI service for managing Kubernetes deployments of agent environments
- **`/environments`**: Docker environments for AI agents (including Claude)
- **`/k8s`**: Kubernetes deployment configurations

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
- React Context + SWR for state management
- [NextAuth.js](https://next-auth.js.org) for authentication

### Backend
- FastAPI microservices
- Server-Sent Events (SSE) for chat streaming
- WebSockets for remote desktop interactions
- Agno framework for AI agent orchestration
- Kubernetes with custom operator for container orchestration

### Data Layer
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
- Python 3.11+
- Docker
- Kubernetes cluster or minikube for local development
- uv (for Python dependency management)

### Web Frontend

1. Navigate to the web directory
   ```bash
   cd web
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

The web application should now be running on [localhost:3000](http://localhost:3000/).

### Overseer Service

1. Navigate to the overseer directory
   ```bash
   cd overseer
   ```

2. Install dependencies using uv
   ```bash
   # Install base dependencies
   uv pip install -e .

   # Install development dependencies
   uv pip install -e ".[dev]"

   # Install test dependencies
   uv pip install -e ".[test]"
   ```

3. Run the service
   ```bash
   python run.py
   ```

The Overseer API should now be running on [localhost:8000](http://localhost:8000/) with documentation available at [localhost:8000/docs](http://localhost:8000/docs).

### Environment Setup

For local testing with minikube:

1. Start minikube
   ```bash
   minikube start
   ```

2. Deploy to minikube
   ```bash
   cd overseer
   ./deploy_to_minikube.sh
   ```

## Deployment

### Vercel Deployment (Web Frontend)

You can deploy the frontend to Vercel with one click:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fa8s-ai%2Fa8s)

### Kubernetes Deployment

For production deployment:

1. Build and push container images
   ```bash
   # Build the Overseer image
   cd overseer
   docker build -t your-registry/overseer:latest .
   docker push your-registry/overseer:latest
   
   # Build environment images
   cd environments/claude
   docker build -t your-registry/claude-env:latest .
   docker push your-registry/claude-env:latest
   ```

2. Deploy using Kubernetes manifests
   ```bash
   # Apply base configurations
   kubectl apply -f k8s/namespace.yaml
   
   # Deploy Overseer
   kubectl apply -f overseer/k8s/
   
   # Deploy other required services
   kubectl apply -f k8s/
   ```

Detailed deployment documentation will continue to evolve as the project develops.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
