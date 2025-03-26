<h1 align="center"> A8s: AI Agent Desktop Environment Platform </h1>

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

The project is designed to be deployed using Docker and Kubernetes (Minikube). For detailed deployment instructions, see the [`k8s`](./k8s) directory.

### Quick Start with Minikube

1. **Prerequisites**:
   - [Docker](https://docs.docker.com/get-docker/)
   - [Minikube](https://minikube.sigs.k8s.io/docs/start/)
   - [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
   - Anthropic API key

2. **Setup and Deploy**:
   ```bash
   # Navigate to k8s directory
   cd k8s

   # Create empty GitHub credentials file
   touch ../environments/claude/.github-credentials

   # Build Docker images (web app and Claude environment)
   ./build-local-image.sh

   # Start Minikube and set up infrastructure
   ./setup-minikube.sh

   # Set up secrets and configuration
   export ANTHROPIC_API_KEY=your_api_key
   ./create-secret.sh

   # Deploy web application
   kubectl apply -f web-deployment.yaml
   ```

3. **Access the Application**:
   ```bash
   # Get Minikube IP
   minikube ip
   ```
   Access the services at:
   - Web App: `http://<minikube-ip>/`

   Alternatively, use port forwarding for local access:
   ```bash
   # For web application
   kubectl port-forward service/web-service 3000:3000 -n a8s
   ```
   Then access:
   - Web App: `http://localhost:3000`

For detailed instructions, environment setup, development workflow, and cleanup procedures, refer to the [k8s/README.md](./k8s/README.md) file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
