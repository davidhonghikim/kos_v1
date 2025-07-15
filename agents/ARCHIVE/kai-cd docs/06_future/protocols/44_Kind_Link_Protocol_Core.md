---
title: "Kind Link Protocol Core"
description: "Core KLP specification for agent interoperability"
type: "protocol"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["kind-link-protocol-extensions.md", "agent-communication-protocols-core.md"]
implementation_status: "planned"
---

# Kind Link Protocol Core

## Agent Context
Core specification for the Kind Link Protocol (KLP) enabling standardized agent-to-agent communication and interoperability across different Kind ecosystem implementations.

## Protocol Foundation

```typescript
interface KLPMessage {
  version: string; // Protocol version (e.g., "1.0")
  id: string; // Unique message identifier
  type: KLPMessageType;
  source: KLPAddress;
  destination: KLPAddress;
  payload: KLPPayload;
  headers: KLPHeaders;
  timestamp: string; // ISO 8601
  signature?: string; // Optional cryptographic signature
}

interface KLPAddress {
  scheme: 'klp'; // Protocol scheme
  authority: string; // Cluster or domain
  path: string; // Agent identifier
  query?: Record<string, string>; // Optional parameters
  fragment?: string; // Optional fragment
}

interface KLPPayload {
  contentType: string; // MIME type
  encoding: 'json' | 'msgpack' | 'protobuf' | 'binary';
  data: any; // Actual payload data
  size: number; // Payload size in bytes
  checksum?: string; // Optional integrity check
}

interface KLPHeaders {
  priority: 'low' | 'normal' | 'high' | 'urgent';
  ttl?: number; // Time to live in seconds
  correlation?: string; // Correlation ID for request/response
  reply?: KLPAddress; // Reply-to address
  route?: KLPAddress[]; // Routing path
  [key: string]: any; // Additional headers
}

type KLPMessageType = 
  | 'request'
  | 'response'
  | 'notification'
  | 'error'
  | 'heartbeat'
  | 'capability'
  | 'delegation'
  | 'subscription';
```

## Core Protocol Implementation

```typescript
class KLPProtocolEngine {
  private version: string = '1.0';
  private localAddress: KLPAddress;
  private messageHandlers: Map<KLPMessageType, KLPMessageHandler>;
  private routingTable: KLPRoutingTable;

  constructor(localAddress: KLPAddress) {
    this.localAddress = localAddress;
    this.messageHandlers = new Map();
    this.routingTable = new KLPRoutingTable();
    this.setupDefaultHandlers();
  }

  async sendMessage(
    destination: KLPAddress,
    type: KLPMessageType,
    payload: any,
    options: KLPSendOptions = {}
  ): Promise<KLPMessageResult> {
    const message: KLPMessage = {
      version: this.version,
      id: crypto.randomUUID(),
      type,
      source: this.localAddress,
      destination,
      payload: await this.encodePayload(payload, options.encoding),
      headers: this.buildHeaders(options),
      timestamp: new Date().toISOString()
    };

    // Sign message if required
    if (options.sign) {
      message.signature = await this.signMessage(message);
    }

    // Route and send message
    const route = await this.routingTable.findRoute(destination);
    if (!route) {
      return {
        success: false,
        error: 'No route to destination',
        messageId: message.id
      };
    }

    try {
      await this.transmitMessage(message, route);
      return {
        success: true,
        messageId: message.id,
        route: route.path
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        messageId: message.id
      };
    }
  }

  async receiveMessage(rawMessage: Buffer | string): Promise<void> {
    try {
      const message = await this.parseMessage(rawMessage);
      
      // Validate message
      const validation = await this.validateMessage(message);
      if (!validation.valid) {
        console.warn('Invalid KLP message received:', validation.error);
        return;
      }

      // Route to appropriate handler
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        await handler.handle(message);
      } else {
        console.warn(`No handler for message type: ${message.type}`);
        
        // Send error response if it's a request
        if (message.type === 'request') {
          await this.sendErrorResponse(message, 'Unsupported message type');
        }
      }

    } catch (error) {
      console.error('Message processing failed:', error);
    }
  }

  registerHandler(type: KLPMessageType, handler: KLPMessageHandler): void {
    this.messageHandlers.set(type, handler);
  }

  private async encodePayload(
    data: any,
    encoding: 'json' | 'msgpack' | 'protobuf' | 'binary' = 'json'
  ): Promise<KLPPayload> {
    let encodedData: any;
    let contentType: string;

    switch (encoding) {
      case 'json':
        encodedData = JSON.stringify(data);
        contentType = 'application/json';
        break;
      
      case 'msgpack':
        encodedData = msgpack.encode(data);
        contentType = 'application/msgpack';
        break;
      
      case 'protobuf':
        encodedData = this.encodeProtobuf(data);
        contentType = 'application/protobuf';
        break;
      
      case 'binary':
        encodedData = data;
        contentType = 'application/octet-stream';
        break;
      
      default:
        throw new Error(`Unsupported encoding: ${encoding}`);
    }

    const size = Buffer.byteLength(encodedData);
    const checksum = await this.calculateChecksum(encodedData);

    return {
      contentType,
      encoding,
      data: encodedData,
      size,
      checksum
    };
  }

  private buildHeaders(options: KLPSendOptions): KLPHeaders {
    return {
      priority: options.priority || 'normal',
      ttl: options.ttl,
      correlation: options.correlationId,
      reply: options.replyTo,
      ...options.customHeaders
    };
  }
}
```

## Address Resolution

```typescript
class KLPAddressResolver {
  private cache: Map<string, KLPAddress>;
  private resolvers: KLPResolver[];

  constructor() {
    this.cache = new Map();
    this.resolvers = [];
    this.setupDefaultResolvers();
  }

  async resolve(address: string | KLPAddress): Promise<KLPAddress | null> {
    if (typeof address === 'object') {
      return address; // Already resolved
    }

    // Check cache first
    if (this.cache.has(address)) {
      return this.cache.get(address)!;
    }

    // Try each resolver
    for (const resolver of this.resolvers) {
      try {
        const resolved = await resolver.resolve(address);
        if (resolved) {
          this.cache.set(address, resolved);
          return resolved;
        }
      } catch (error) {
        console.warn(`Resolver ${resolver.name} failed:`, error);
      }
    }

    return null;
  }

  parseAddress(addressString: string): KLPAddress {
    const url = new URL(addressString);
    
    if (url.protocol !== 'klp:') {
      throw new Error('Invalid KLP address scheme');
    }

    return {
      scheme: 'klp',
      authority: url.hostname + (url.port ? `:${url.port}` : ''),
      path: url.pathname,
      query: Object.fromEntries(url.searchParams),
      fragment: url.hash ? url.hash.substring(1) : undefined
    };
  }

  formatAddress(address: KLPAddress): string {
    let addressString = `${address.scheme}://${address.authority}${address.path}`;
    
    if (address.query && Object.keys(address.query).length > 0) {
      const params = new URLSearchParams(address.query);
      addressString += `?${params.toString()}`;
    }
    
    if (address.fragment) {
      addressString += `#${address.fragment}`;
    }

    return addressString;
  }

  private setupDefaultResolvers(): void {
    // DNS-based resolver
    this.resolvers.push(new DNSKLPResolver());
    
    // DHT-based resolver
    this.resolvers.push(new DHTKLPResolver());
    
    // Local registry resolver
    this.resolvers.push(new LocalKLPResolver());
  }
}
```

## Message Handlers

```typescript
abstract class KLPMessageHandler {
  abstract handle(message: KLPMessage): Promise<void>;
  
  protected async sendResponse(
    originalMessage: KLPMessage,
    responseData: any,
    success: boolean = true
  ): Promise<void> {
    const response: KLPMessage = {
      version: originalMessage.version,
      id: crypto.randomUUID(),
      type: success ? 'response' : 'error',
      source: originalMessage.destination,
      destination: originalMessage.source,
      payload: await this.engine.encodePayload(responseData),
      headers: {
        priority: originalMessage.headers.priority,
        correlation: originalMessage.id
      },
      timestamp: new Date().toISOString()
    };

    await this.engine.transmitMessage(response, await this.engine.routingTable.findRoute(response.destination));
  }
}

class KLPRequestHandler extends KLPMessageHandler {
  async handle(message: KLPMessage): Promise<void> {
    try {
      const result = await this.processRequest(message);
      await this.sendResponse(message, result, true);
    } catch (error) {
      await this.sendResponse(message, { error: error.message }, false);
    }
  }

  private async processRequest(message: KLPMessage): Promise<any> {
    const { data } = message.payload;
    
    switch (data.action) {
      case 'ping':
        return { pong: true, timestamp: new Date().toISOString() };
      
      case 'get_capabilities':
        return await this.getCapabilities();
      
      case 'execute_task':
        return await this.executeTask(data.task);
      
      default:
        throw new Error(`Unknown action: ${data.action}`);
    }
  }

  private async getCapabilities(): Promise<any> {
    return {
      protocols: ['klp/1.0'],
      capabilities: ['ping', 'get_capabilities', 'execute_task'],
      extensions: ['delegation', 'streaming']
    };
  }
}

class KLPNotificationHandler extends KLPMessageHandler {
  async handle(message: KLPMessage): Promise<void> {
    const { data } = message.payload;
    
    switch (data.type) {
      case 'status_update':
        await this.handleStatusUpdate(data);
        break;
      
      case 'event_notification':
        await this.handleEventNotification(data);
        break;
      
      default:
        console.warn(`Unknown notification type: ${data.type}`);
    }
  }

  private async handleStatusUpdate(data: any): Promise<void> {
    console.log(`Status update from ${data.source}: ${data.status}`);
    // Handle status update logic
  }

  private async handleEventNotification(data: any): Promise<void> {
    console.log(`Event notification: ${data.event}`);
    // Handle event notification logic
  }
}
```
