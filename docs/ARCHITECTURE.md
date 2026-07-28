# 🏗️ Astra OS Architecture

## Overview

Astra OS follows a modular architecture that separates the user interface, rendering engine, business logic, AI services, and backend APIs.

```
                        ┌────────────────────────┐
                        │        User            │
                        └───────────┬────────────┘
                                    │
                                    ▼
                      ┌────────────────────────┐
                      │     React Frontend     │
                      └───────────┬────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  Chat Feature             Browser Feature           Voice Feature
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                        Zustand State Stores
                                  │
                                  ▼
                         Service Layer (API)
                                  │
                                  ▼
                          FastAPI Backend
                                  │
                                  ▼
                             Gemini API
```

---

# Frontend

The frontend is built with React and Vite.

## Responsibilities

- User Interface
- State Management
- Voice Controls
- Rendering Engine
- Browser
- Settings

### Technologies

- React
- Vite
- Zustand
- React Router
- React Markdown

---

# Rendering Engine

The rendering engine powers Astra's animated AI Core.

## Components

- Plasma Core
- Glow Halo
- Energy Field
- Orbit System
- Particle Cloud
- Bloom Effects

### Technologies

- Three.js
- React Three Fiber
- GLSL Shaders
- Post Processing

---

# Backend

The backend is built with FastAPI.

## Responsibilities

- AI Chat
- Browser Search
- System Information
- Future File Processing
- Future Memory
- Future Agents

---

# State Management

Zustand manages application state.

## Stores

- Chat Store
- Voice Store
- AI State Store
- Browser Store
- Audio Store

---

# Planned Architecture

```
src/

├── engine/
│   ├── rendering/
│   ├── shaders/
│   ├── materials/
│   ├── effects/
│   └── config/
│
├── features/
│   ├── chat/
│   ├── browser/
│   ├── voice/
│   ├── files/
│   ├── memory/
│   ├── agents/
│   └── settings/
│
├── services/
├── store/
├── hooks/
├── utils/
├── constants/
└── lib/
```

---

# Design Principles

- Modular architecture
- Separation of concerns
- Feature-based organisation
- Reusable components
- GPU-accelerated rendering
- Scalable state management
- Clean API boundaries
- Extensible plugin support

---

# Future Expansion

The architecture is designed to support:

- Desktop application
- Plugin system
- AI agents
- Long-term memory
- File intelligence
- Automation
- Computer vision