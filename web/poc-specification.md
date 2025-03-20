A8s PoC Technical Specification
Overview
This Proof of Concept (PoC) demonstrates a web-based system that enables users to interact with AI agents through a chat interface while also providing access to remote desktop environments that the agents can control. The system allows for parallel agent operations, state preservation, and direct user intervention.
Core Requirements
Chat Agent 
General chat agent that converses with the user to understand requirements
User can add various items in storage, eg: documents, Saas connections or previously created artifacts like apps into the chat to define things more
Hands off to overseer agent once the requirement is clear on a new workflow
Overseer Agent (Could be a non AI program)
Decides which agent template and tools to inject into a new containerised desktop environment based on the Chat Agent request
Provisions the environment with the gathered information
Agent Environment


Chat interface to communicate with AI agents inside each desktop environment
Required credentials to access external services are provided at the provisioning time. 
Agent can request the Overseer Agent to provide additional context, tools, credentials if required
Parallelization and Multi-session Support


Support for multiple concurrent agent sessions
Independent parallel execution tracks
Multi-user support with authentication/authorisation and session management
Interactive Desktop Environment


Remote desktop streaming embedded as artifacts in chat
Ability to toggle between observation and direct interaction modes
Real-time view of agent actions in the desktop environment
Agent Control and Interaction


Ability to interrupt and redirect agent tasks
Communication with agent about current desktop operations
Handoff between agent control and user control
State Management


Environment state snapshots and restoration points
Recovery from errors by returning to previous states
Persistent state storage across sessions
Deployment and Administration


Kubernetes-based deployment
Administration interface for monitoring
Resource management and scaling
Artifact Extraction/Output


Ability to extract and download outputs (PDFs, websites, etc.)
Result persistence independent of environment state
User Flow https://github.com/a8s-ai/a8s/blob/main/prototype-spec.md

Technology Stack
Frontend
Framework: Next.js with Vercel AI SDK
UI Library: Tailwind CSS + Shadcn UI
Remote Desktop Client: noVNC (WebSocket-based VNC client)
State Management: React Context + SWR for data fetching
Authentication: NextAuth.js with JWT
Backend
API Framework: FastAPI microservices
Real-time Communication:
Server-Sent Events (SSE) for chat streaming
WebSockets for remote desktop interactions
Agent Framework: Agno for AI agent orchestration
Container Orchestration: Kubernetes with custom operator
Database: PostgreSQL for metadata, Redis for session management
Storage: Persistent volumes for environment state
System Architecture
Microservices
Auth Service


User authentication and session management
Role-based permissions
JWT token issuance and validation
Agent Service


Integration with Agno framework
Chat processing and response generation
Task analysis and environment requirements determination
Agent-to-environment coordination
Environment Orchestrator: Overseer


Custom Kubernetes operator for desktop environment management
Container provisioning and configuration
State snapshot management
Resource allocation and scheduling
Streaming Service


noVNC proxy for browser-based VNC access
WebSocket relay for desktop interactions
Stream quality management
Input event capture and forwarding
State Management Service


Environment state snapshots
Recovery point creation and restoration
Artifact extraction (PDFs, websites, etc.)
Persistent storage management
User Flow
Session Initialization


User logs in and starts a new chat session
User describes their task or goal to the agent
Agent analyzes requirements through conversation
Environment Provisioning


Agent determines desktop environment is needed
System provisions appropriate container environment
Remote desktop session is initialized and embedded as artifact
User receives notification that environment is ready
Agent Operation


Agent interacts with desktop environment to perform tasks
User can observe actions in real-time through noVNC stream
Agent provides explanations via chat alongside visual feedback
User Intervention


User can toggle to interaction mode at any time
User can directly interact with the desktop environment
User can interrupt agent task and provide new instructions
Agent can adapt to changes in requirements
State Management


User or agent can trigger state snapshots at key points
System can restore from snapshots if errors occur
User can save session for later continuation
Output Extraction


Final outputs are automatically identified and extracted
User can download artifacts (documents, code, etc.)
Artifacts are stored independently from environment
Component Interaction
1. Chat and Environment Coordination
User → Chat Interface → Agent Service → Task Analysis
                                      ↓
                                    Environment Required?
                                      ↓
                                    Environment Orchestrator → Container Provisioning
                                      ↓
                                    noVNC Stream Embedded as Artifact
2. Desktop Interaction Flow
Agent Instruction → Agno Framework → Desktop Actions
                                   ↓
                                 VNC/RDP Protocol
                                   ↓
User ← noVNC Client ← WebSocket Proxy ← Container Desktop
3. State Management Flow
Snapshot Trigger → Environment Orchestrator → Container Snapshot
                                            ↓
                                          Persistent Volume
                                            ↓
                                          Metadata Database
Database Schema
Users Table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
Sessions Table
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50) NOT NULL
);
Environments Table
CREATE TABLE environments (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES sessions(id),
  container_id VARCHAR(255),
  image_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_snapshot_at TIMESTAMP WITH TIME ZONE,
  status VARCHAR(50) NOT NULL,
  vnc_port INTEGER,
  vnc_password VARCHAR(255)
);
Snapshots Table
CREATE TABLE snapshots (
  id UUID PRIMARY KEY,
  environment_id UUID REFERENCES environments(id),
  snapshot_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  storage_path VARCHAR(255) NOT NULL,
  metadata JSONB
);
API Endpoints
Auth Service
POST /api/auth/login - User login
POST /api/auth/logout - User logout
GET /api/auth/session - Get current session
POST /api/auth/register - Register new user (admin only)
Agent Service
POST /api/sessions - Create new chat session
GET /api/sessions - List user sessions
GET /api/sessions/{session_id} - Get session details
POST /api/sessions/{session_id}/messages - Send message to agent
GET /api/sessions/{session_id}/messages/stream - Stream agent responses (SSE)
POST /api/sessions/{session_id}/interrupt - Interrupt current agent operation
Environment Orchestrator
POST /api/environments - Create new environment
GET /api/environments/{env_id} - Get environment details
POST /api/environments/{env_id}/snapshots - Create environment snapshot
POST /api/environments/{env_id}/restore - Restore from snapshot
DELETE /api/environments/{env_id} - Terminate environment
Streaming Service
GET /api/environments/{env_id}/vnc - WebSocket endpoint for noVNC connection
POST /api/environments/{env_id}/interact - Send interaction events to environment
State Management Service
GET /api/environments/{env_id}/snapshots - List available snapshots
GET /api/environments/{env_id}/artifacts - List extracted artifacts
GET /api/environments/{env_id}/artifacts/{artifact_id} - Download artifact
UI Specification
Layout and Interface Design
The user interface follows a split-panel design inspired by Claude's chat interface with artifacts:
+--------------------------------------------------+
|              HEADER / NAVIGATION                 |
+-------------------+------------------------------+
|                   |                              |
|                   |                              |
|                   |                              |
|    CHAT PANEL     |    ENVIRONMENT PANEL         |
|                   |    (Remote Desktop View)     |
|                   |                              |
|                   |                              |
|                   |                              |
+-------------------+------------------------------+
|           INPUT / CONTROL PANEL                  |
+--------------------------------------------------+
Main Interface Components
1. Chat Panel
The left panel of the interface is dedicated to the chat interaction with the agent:
Message History: Scrollable area displaying the conversation history
User Messages: Right-aligned with distinctive styling
Agent Messages: Left-aligned with agent avatar
Special Messages: System notifications about environment status
Message Types: Support for text, markdown, code blocks, and embedded artifacts
2. Environment Panel
The right panel displays the remote desktop environment as an interactive artifact:
Desktop View: Live stream of the remote desktop via noVNC
Control Bar: Overlay with controls for interaction mode and actions
Status Indicator: Shows connection status and current control mode
Interaction Modes: Toggle between "View Only" and "Interactive" modes
Action Buttons: Options for snapshot creation, interruption, etc.
3. Control Panel
The bottom section contains input controls:
Message Input: Text area for sending messages to the agent
Environment Controls: Quick actions for the current environment
Session Actions: Save, restart, or terminate the current session



