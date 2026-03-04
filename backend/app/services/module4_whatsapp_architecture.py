"""
Rayeva AI — Module 4: AI WhatsApp Support Bot (ARCHITECTURE OUTLINE)
This module is designed but NOT fully implemented. See README for architecture details.

─────────────────────────────────────────────────────────────────────────────
ARCHITECTURE OVERVIEW
─────────────────────────────────────────────────────────────────────────────

Purpose:
  AI-powered WhatsApp support bot that handles:
  1. Order status queries (using real database data)
  2. Return policy questions
  3. Escalation of high-priority/refund issues
  4. Full conversation logging

Design: Webhook-based architecture compatible with WhatsApp Business API.
  A web-based chat simulator replaces the actual WhatsApp integration for demo.
  Plugging in Twilio or WhatsApp Business API requires only changing the
  webhook adapter — zero changes to bot logic.

─────────────────────────────────────────────────────────────────────────────
DATABASE SCHEMA
─────────────────────────────────────────────────────────────────────────────

Table: conversations
  id              INTEGER PRIMARY KEY
  session_id      VARCHAR(100) UNIQUE  -- WhatsApp phone or session UUID
  customer_id     INTEGER FK → customers.id (nullable)
  status          VARCHAR(50)     -- active, resolved, escalated
  escalated_at    DATETIME (nullable)
  escalation_reason VARCHAR(500)
  messages        JSON            -- Full message history
  created_at      DATETIME
  updated_at      DATETIME

Table: message_logs
  id              INTEGER PRIMARY KEY
  conversation_id INTEGER FK → conversations.id
  role            VARCHAR(20)     -- user, assistant, system
  content         TEXT
  intent          VARCHAR(50)     -- order_status, return_policy, refund, general, escalation
  confidence      FLOAT
  tokens_used     INTEGER
  latency_ms      FLOAT
  created_at      DATETIME

─────────────────────────────────────────────────────────────────────────────
API ENDPOINTS
─────────────────────────────────────────────────────────────────────────────

POST /api/v1/chat/message
  Body: { session_id, message }
  → Classifies intent → routes to handler → returns AI response
  → Returns: { response, intent, escalated, conversation_id }

GET /api/v1/chat/conversations
  → List all conversations (for admin dashboard)

GET /api/v1/chat/conversations/{session_id}
  → Get full conversation history

POST /api/v1/chat/webhook  (WhatsApp Business API compatible)
  → Accepts standard WhatsApp webhook payload
  → Processes message → responds via adapter
  → Compatible with Twilio / Meta WhatsApp API contract

─────────────────────────────────────────────────────────────────────────────
INTENT CLASSIFICATION
─────────────────────────────────────────────────────────────────────────────

AI classifies each incoming message into intents:

  order_status    → "Where is my order?", "Track order #123"
                    → Query orders table, return real status
  return_policy   → "How do I return?", "What's your return policy?"
                    → Return predefined policy text, AI-formatted
  refund_request  → "I want a refund", "Money not received"
                    → AUTO-ESCALATE (business rule: all refunds → human)
  product_inquiry → "Tell me about bamboo cutlery"
                    → Query products table, return AI-formatted details
  general         → Greetings, thanks, unclear queries
                    → Friendly response, ask for clarification
  escalation      → "Talk to a human", "This is urgent"
                    → Immediate escalation

System Prompt:
  "You are Rayeva's friendly WhatsApp support assistant.
   You help customers with order tracking, return policies, and product info.
   RULES:
   1. Always check the database for order status — never make up tracking info
   2. For refund requests: acknowledge the issue and escalate to human support
   3. Be concise — WhatsApp messages should be short (under 200 words)
   4. Use friendly, professional tone with occasional emoji
   5. If unsure, ask clarifying questions rather than guessing
   6. Never share other customers' data"

─────────────────────────────────────────────────────────────────────────────
ESCALATION RULES (Business Logic, NOT AI)
─────────────────────────────────────────────────────────────────────────────

Auto-escalate when:
  1. Intent = refund_request (ALL refunds go to human)
  2. Order value > ₹5,000 AND complaint intent
  3. 3+ messages without resolution (conversation length check)
  4. Customer explicitly asks for human support
  5. AI confidence < 0.5 on intent classification

Escalation action:
  - Set conversation.status = "escalated"
  - Set conversation.escalated_at = now()
  - Log escalation_reason
  - Respond: "I'm connecting you with our support team. A human agent
    will respond within 15 minutes. Your reference: #CONV-{id}"

─────────────────────────────────────────────────────────────────────────────
CONVERSATION FLOW
─────────────────────────────────────────────────────────────────────────────

  [User Message via WhatsApp / Web Chat]
       │
       ├─→ [Find or create conversation by session_id]
       │
       ├─→ [AI: Classify intent]
       │     ├─ order_status → Query DB for order → Format response
       │     ├─ return_policy → Retrieve policy → AI formats answer
       │     ├─ refund_request → Acknowledge → Escalate (business rule)
       │     ├─ product_inquiry → Query products DB → AI formats answer
       │     └─ general → AI conversational response
       │
       ├─→ [Check escalation rules]
       │     ├─ Should escalate? → Set status, notify, respond
       │     └─ No → Return AI response
       │
       ├─→ [Log message + response in message_logs]
       │
       └─→ [Return response to user]

─────────────────────────────────────────────────────────────────────────────
WEBHOOK ADAPTER PATTERN
─────────────────────────────────────────────────────────────────────────────

Interface: MessageAdapter (ABC)
  - receive(webhook_payload) → InternalMessage
  - send(session_id, response_text) → bool

Implementations:
  - WebChatAdapter — For the demo web UI (simple HTTP)
  - TwilioAdapter  — For Twilio WhatsApp integration (webhook format)
  - MetaAdapter    — For WhatsApp Business API direct (webhook format)

The bot logic is adapter-agnostic. It receives an InternalMessage and
returns a response string. The adapter handles WhatsApp-specific formatting.

─────────────────────────────────────────────────────────────────────────────
WEB CHAT SIMULATOR (for Demo)
─────────────────────────────────────────────────────────────────────────────

A simple Next.js chat page that:
  - Displays a WhatsApp-style chat interface (green bubbles, timestamps)
  - Sends messages to POST /api/v1/chat/message
  - Shows typing indicators during AI processing
  - Displays intent classification badge on each response
  - Shows escalation alerts

This proves the bot logic works without requiring WhatsApp Business
API approval or Twilio credentials. Document that swapping to real
WhatsApp requires only implementing a new MessageAdapter.

─────────────────────────────────────────────────────────────────────────────
IMPLEMENTATION NOTES
─────────────────────────────────────────────────────────────────────────────

1. Use streaming generation (generate_content_stream) for real-time
   chat feel — yield tokens as they arrive to the web chat UI.
2. Google Search tool (types.Tool(google_search=types.GoogleSearch()))
   can be enabled for grounding policy/product answers with real data.
3. Conversation context: include last 5-10 messages in each AI call
   for multi-turn coherence, but truncate older messages to manage tokens.
4. Rate limiting: max 10 messages per minute per session to prevent abuse.
5. All conversations are logged for quality review and AI improvement.
"""
