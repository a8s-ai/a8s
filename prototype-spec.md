# Minimal Prototype Specification

## User Flow

- User chats with the main agent, gives requirement
- This agent decides tools/data needed and asks the image([./environments/claude](./environments/claude)) to be deployed
- The operator deploys the image and passes the tools/data/requirement
- The frontend connects to VM once it has been deployed/ready
- Agent inside the VM would execute on the requirement using the tools/data
- User can interact with the agent inside the VM through chat interface inside the desktop

## Implementation Approach

Here's a streamlined, minimal implementation focusing only on the essential components needed to get the prototype working:

### 1. Next.js Frontend (Minimal)

- **Core Components**:
  - Simple chat interface with AI model integration
  - Basic deployment status indicator
  - Connection panel for accessing deployed environments

- **Implementation**:
  - Use Next.js App Router with a single main page
  - Integrate AI SDK for Claude or GPT model communication
  - Simple WebSocket connection for real-time updates
  - Basic authentication with session cookies

- **Connection Method**:
  - Embed a simple iframe or terminal component
  - Use direct WebSocket connection to deployed environment
  - Minimal styling with basic CSS or Tailwind

### 2. Kubernetes Deployment (Minimal)

- **Base Structure**:
  - Single namespace for all components
  - One deployment controller service
  - Pre-built container images with common tools

- **Deployment Process**:
  1. Frontend sends deployment request to API
  2. API creates a Kubernetes Deployment with appropriate container
  3. Service and Ingress resources expose the environment
  4. Connection details returned to frontend

- **Container Strategy**:
  - Use 2-3 pre-built images covering common use cases
  - Minimal dynamic configuration via environment variables
  - Expose SSH or WebSocket endpoint for connection

- **Resource Management**:
  - Fixed resource limits for all deployments
  - Simple TTL-based cleanup (terminate after fixed time)
  - Basic health checks

### 3. API Service (Minimal)

- **Endpoints**:
  - `/deploy` - Request new environment
  - `/status/:id` - Check deployment status
  - `/connect/:id` - Get connection details

- **Implementation**:
  - Next.js API routes
  - Direct Kubernetes API interaction via client library
  - Basic error handling and logging

### 4. Connection Method (Minimal)

- **For GUI Access**:
  - Simple noVNC implementation


### 5. Deployment Flow

1. **User Request**:
   - User describes requirements in chat interface
   - AI determines basic environment type needed

2. **Deployment**:
   - Frontend calls `/deploy` with environment type
   - Backend creates Kubernetes resources
   - Polling or WebSocket updates deployment status

3. **Connection**:
   - Once ready, frontend connects to the deployed environment
   - User can now interact with the deployed environment


### 7. Implementation Steps

1. **Setup Infrastructure**:
   - Create Kubernetes cluster (can use minikube for development)
   - Set up basic networking and storage

2. **Build Container Images**:
   - Ensure Image from [./environments/claude](./environments/claude/Dockerfile) exposes necessary connection endpoints

3. **Develop API Service**:
   - Implement basic deployment and status endpoints
   - Create Kubernetes client integration

4. **Build Frontend**:
   - Implement chat interface with AI SDK
   - Create simple deployment request flow
   - Add basic terminal/GUI component

5. **Integration**:
   - Connect frontend to API service
   - Test deployment and connection flow
   - Implement basic error handling

