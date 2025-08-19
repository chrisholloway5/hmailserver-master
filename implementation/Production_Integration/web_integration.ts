/**
 * Production Web Integration Service for hMailServer
 * Next.js 15 integration layer that connects the React 19 frontend
 * with all backend services through the API Gateway
 */

import { NextRequest, NextResponse } from 'next/server';
import { WebSocket } from 'ws';
import { Server } from 'http';

// Types for production integration
interface EmailProcessingRequest {
  sender: string;
  recipient: string;
  subject: string;
  content: string;
  timestamp?: string;
  hasAttachments?: boolean;
  language?: string;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  operations?: ('core' | 'ai' | 'autonomous' | 'translation')[];
}

interface IntegratedProcessingResult {
  coreProcessing: {
    processed: boolean;
    securityScan: {
      passed: boolean;
      spamScore: number;
      threatLevel: string;
    };
    threadId: string;
    processingTimeMs: number;
  };
  aiEnhancements: {
    suggestions: string[];
    summary: string;
    routingDecisions: string[];
    translation?: string;
    keyPoints: string[];
    confidenceScores: Record<string, number>;
    processingTimeMs: number;
  };
  autonomousActions: {
    optimizations: string[];
    predictions: string[];
    actions: string[];
    processingTimeMs: number;
  };
  overall: {
    processingTimeMs: number;
    success: boolean;
    errors: string[];
    confidence: number;
    timestamp: string;
  };
}

interface SystemHealth {
  healthy: boolean;
  services: Record<string, boolean>;
  details: Record<string, any>;
  timestamp: string;
}

interface SystemStats {
  coreStats: any;
  aiStats: any;
  autonomousStats: any;
  gatewayStats: {
    requestsProcessed: number;
    averageResponseTime: number;
    errorRate: number;
    uptime: string;
  };
  timestamp: string;
}

/**
 * Production Web Integration Manager
 * Handles all communication between React frontend and backend services
 */
export class ProductionWebIntegrator {
  private readonly gatewayUrl: string;
  private readonly wsConnections: Set<WebSocket> = new Set();
  private readonly requestCache = new Map<string, any>();
  private readonly cacheTimeout = 30000; // 30 seconds
  
  constructor() {
    this.gatewayUrl = process.env.GATEWAY_URL || 'http://localhost:8080';
  }
  
  /**
   * Process email through the complete hMailServer pipeline
   */
  async processEmailIntegrated(
    request: EmailProcessingRequest
  ): Promise<IntegratedProcessingResult> {
    const startTime = Date.now();
    const requestId = this.generateRequestId();
    
    try {
      console.log(`[${requestId}] Starting integrated email processing`);
      
      // Validate request
      this.validateEmailRequest(request);
      
      // Check cache first
      const cacheKey = this.generateCacheKey(request);
      if (this.requestCache.has(cacheKey)) {
        console.log(`[${requestId}] Returning cached result`);
        return this.requestCache.get(cacheKey);
      }
      
      // Call API Gateway for integrated processing
      const response = await fetch(`${this.gatewayUrl}/api/email/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        body: JSON.stringify({
          ...request,
          timestamp: request.timestamp || new Date().toISOString(),
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Gateway request failed: ${response.status} ${response.statusText}`);
      }
      
      const rawResult = await response.json();
      
      // Transform gateway response to our interface
      const result: IntegratedProcessingResult = {
        coreProcessing: {
          processed: rawResult.coreProcessing?.processed || false,
          securityScan: {
            passed: rawResult.coreProcessing?.securityScan?.passed || false,
            spamScore: rawResult.coreProcessing?.securityScan?.spamScore || 0,
            threatLevel: rawResult.coreProcessing?.securityScan?.threatLevel || 'unknown',
          },
          threadId: rawResult.coreProcessing?.threadId || '',
          processingTimeMs: rawResult.coreProcessing?.processingTimeMs || 0,
        },
        aiEnhancements: {
          suggestions: rawResult.aiEnhancements?.suggestions || [],
          summary: rawResult.aiEnhancements?.summary || '',
          routingDecisions: rawResult.aiEnhancements?.routingDecisions || [],
          translation: rawResult.aiEnhancements?.translation || undefined,
          keyPoints: rawResult.aiEnhancements?.keyPoints || [],
          confidenceScores: rawResult.aiEnhancements?.confidenceScores || {},
          processingTimeMs: rawResult.aiEnhancements?.processingTimeMs || 0,
        },
        autonomousActions: {
          optimizations: rawResult.autonomousActions?.optimizations || [],
          predictions: rawResult.autonomousActions?.predictions || [],
          actions: rawResult.autonomousActions?.actions || [],
          processingTimeMs: rawResult.autonomousActions?.processingTimeMs || 0,
        },
        overall: {
          processingTimeMs: Date.now() - startTime,
          success: rawResult.success || false,
          errors: rawResult.errors || [],
          confidence: this.calculateOverallConfidence(rawResult),
          timestamp: new Date().toISOString(),
        },
      };
      
      // Cache successful results
      if (result.overall.success) {
        this.requestCache.set(cacheKey, result);
        setTimeout(() => this.requestCache.delete(cacheKey), this.cacheTimeout);
      }
      
      // Notify WebSocket clients
      this.notifyWebSocketClients('email_processed', {
        requestId,
        result,
        processingTime: result.overall.processingTimeMs,
      });
      
      console.log(`[${requestId}] Email processing completed in ${result.overall.processingTimeMs}ms`);
      return result;
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      console.error(`[${requestId}] Email processing failed: ${errorMessage}`);
      
      // Return error result
      const errorResult: IntegratedProcessingResult = {
        coreProcessing: {
          processed: false,
          securityScan: { passed: false, spamScore: 0, threatLevel: 'unknown' },
          threadId: '',
          processingTimeMs: 0,
        },
        aiEnhancements: {
          suggestions: [],
          summary: '',
          routingDecisions: [],
          keyPoints: [],
          confidenceScores: {},
          processingTimeMs: 0,
        },
        autonomousActions: {
          optimizations: [],
          predictions: [],
          actions: [],
          processingTimeMs: 0,
        },
        overall: {
          processingTimeMs: processingTime,
          success: false,
          errors: [errorMessage],
          confidence: 0,
          timestamp: new Date().toISOString(),
        },
      };
      
      // Notify WebSocket clients of error
      this.notifyWebSocketClients('email_error', {
        requestId,
        error: errorMessage,
        processingTime,
      });
      
      return errorResult;
    }
  }
  
  /**
   * Get comprehensive system health information
   */
  async getSystemHealth(): Promise<SystemHealth> {
    try {
      const response = await fetch(`${this.gatewayUrl}/health`);
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      const health = await response.json();
      
      return {
        healthy: health.healthy || false,
        services: health.services || {},
        details: health.details || {},
        timestamp: new Date().toISOString(),
      };
      
    } catch (error) {
      console.error('System health check failed:', error);
      
      return {
        healthy: false,
        services: {
          core_engine: false,
          ai_services: false,
          autonomous: false,
          gateway: false,
        },
        details: {
          error: error instanceof Error ? error.message : 'Unknown error',
        },
        timestamp: new Date().toISOString(),
      };
    }
  }
  
  /**
   * Get comprehensive system statistics
   */
  async getSystemStats(): Promise<SystemStats> {
    try {
      const response = await fetch(`${this.gatewayUrl}/api/stats`);
      
      if (!response.ok) {
        throw new Error(`Stats request failed: ${response.status}`);
      }
      
      const stats = await response.json();
      
      return {
        coreStats: stats.coreStats || {},
        aiStats: stats.aiStats || {},
        autonomousStats: stats.autonomousStats || {},
        gatewayStats: {
          requestsProcessed: 0,
          averageResponseTime: 0,
          errorRate: 0,
          uptime: '0 seconds',
        },
        timestamp: new Date().toISOString(),
      };
      
    } catch (error) {
      console.error('System stats request failed:', error);
      
      return {
        coreStats: { error: 'Unavailable' },
        aiStats: { error: 'Unavailable' },
        autonomousStats: { error: 'Unavailable' },
        gatewayStats: {
          requestsProcessed: 0,
          averageResponseTime: 0,
          errorRate: 1.0,
          uptime: '0 seconds',
        },
        timestamp: new Date().toISOString(),
      };
    }
  }
  
  /**
   * Enhanced AI-only processing (for quick responses)
   */
  async processWithAIOnly(request: EmailProcessingRequest): Promise<any> {
    try {
      const response = await fetch(`${this.gatewayUrl}/api/ai/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        throw new Error(`AI enhancement failed: ${response.status}`);
      }
      
      return await response.json();
      
    } catch (error) {
      console.error('AI-only processing failed:', error);
      throw error;
    }
  }
  
  /**
   * Autonomous optimization request
   */
  async requestAutonomousOptimization(data: any): Promise<any> {
    try {
      const response = await fetch(`${this.gatewayUrl}/api/autonomous/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error(`Autonomous optimization failed: ${response.status}`);
      }
      
      return await response.json();
      
    } catch (error) {
      console.error('Autonomous optimization failed:', error);
      throw error;
    }
  }
  
  /**
   * WebSocket connection management
   */
  setupWebSocketHandler(server: Server) {
    const wss = new WebSocket.Server({ server });
    
    wss.on('connection', (ws: WebSocket, request) => {
      console.log('New WebSocket connection established');
      this.wsConnections.add(ws);
      
      // Send welcome message
      ws.send(JSON.stringify({
        type: 'welcome',
        message: 'Connected to hMailServer Production WebSocket',
        timestamp: new Date().toISOString(),
      }));
      
      // Handle incoming messages
      ws.on('message', async (data: Buffer) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWebSocketMessage(ws, message);
        } catch (error) {
          console.error('WebSocket message handling failed:', error);
          ws.send(JSON.stringify({
            type: 'error',
            error: 'Invalid message format',
            timestamp: new Date().toISOString(),
          }));
        }
      });
      
      // Handle connection close
      ws.on('close', () => {
        console.log('WebSocket connection closed');
        this.wsConnections.delete(ws);
      });
      
      // Handle errors
      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.wsConnections.delete(ws);
      });
    });
    
    console.log('WebSocket server setup complete');
  }
  
  private async handleWebSocketMessage(ws: WebSocket, message: any) {
    const { type, data, requestId } = message;
    
    try {
      switch (type) {
        case 'email_process':
          const result = await this.processEmailIntegrated(data);
          ws.send(JSON.stringify({
            type: 'email_result',
            data: result,
            requestId,
            timestamp: new Date().toISOString(),
          }));
          break;
          
        case 'health_check':
          const health = await this.getSystemHealth();
          ws.send(JSON.stringify({
            type: 'health_result',
            data: health,
            requestId,
            timestamp: new Date().toISOString(),
          }));
          break;
          
        case 'stats_request':
          const stats = await this.getSystemStats();
          ws.send(JSON.stringify({
            type: 'stats_result',
            data: stats,
            requestId,
            timestamp: new Date().toISOString(),
          }));
          break;
          
        case 'ai_enhance':
          const aiResult = await this.processWithAIOnly(data);
          ws.send(JSON.stringify({
            type: 'ai_result',
            data: aiResult,
            requestId,
            timestamp: new Date().toISOString(),
          }));
          break;
          
        default:
          ws.send(JSON.stringify({
            type: 'error',
            error: `Unknown message type: ${type}`,
            requestId,
            timestamp: new Date().toISOString(),
          }));
      }
    } catch (error) {
      ws.send(JSON.stringify({
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        requestId,
        timestamp: new Date().toISOString(),
      }));
    }
  }
  
  private notifyWebSocketClients(type: string, data: any) {
    const message = JSON.stringify({
      type,
      data,
      timestamp: new Date().toISOString(),
    });
    
    this.wsConnections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        try {
          ws.send(message);
        } catch (error) {
          console.error('Failed to send WebSocket message:', error);
          this.wsConnections.delete(ws);
        }
      }
    });
  }
  
  private validateEmailRequest(request: EmailProcessingRequest) {
    if (!request.sender) throw new Error('Sender is required');
    if (!request.recipient) throw new Error('Recipient is required');
    if (!request.subject) throw new Error('Subject is required');
    if (!request.content) throw new Error('Content is required');
  }
  
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private generateCacheKey(request: EmailProcessingRequest): string {
    const key = `${request.sender}_${request.recipient}_${request.subject}_${request.content}`;
    return Buffer.from(key).toString('base64').substr(0, 32);
  }
  
  private calculateOverallConfidence(result: any): number {
    const scores = result.aiEnhancements?.confidenceScores || {};
    const values = Object.values(scores) as number[];
    
    if (values.length === 0) return 0.5; // Default confidence
    
    return values.reduce((sum, score) => sum + score, 0) / values.length;
  }
}

// Global integrator instance
let integratorInstance: ProductionWebIntegrator | null = null;

export function getIntegratorInstance(): ProductionWebIntegrator {
  if (!integratorInstance) {
    integratorInstance = new ProductionWebIntegrator();
  }
  return integratorInstance;
}

// Next.js API Routes
export async function POST(request: NextRequest) {
  const integrator = getIntegratorInstance();
  
  try {
    const requestData = await request.json() as EmailProcessingRequest;
    const result = await integrator.processEmailIntegrated(requestData);
    
    return NextResponse.json(result, {
      headers: {
        'X-Processing-Time': result.overall.processingTimeMs.toString(),
        'X-Success': result.overall.success.toString(),
      },
    });
    
  } catch (error) {
    console.error('API request failed:', error);
    
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const integrator = getIntegratorInstance();
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');
  
  try {
    switch (action) {
      case 'health':
        const health = await integrator.getSystemHealth();
        return NextResponse.json(health);
        
      case 'stats':
        const stats = await integrator.getSystemStats();
        return NextResponse.json(stats);
        
      default:
        return NextResponse.json(
          { error: 'Invalid action parameter' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('API GET request failed:', error);
    
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

// React Hook for using the integration service
export function useProductionIntegration() {
  const integrator = getIntegratorInstance();
  
  return {
    processEmail: (request: EmailProcessingRequest) => 
      integrator.processEmailIntegrated(request),
    
    getSystemHealth: () => integrator.getSystemHealth(),
    
    getSystemStats: () => integrator.getSystemStats(),
    
    processWithAI: (request: EmailProcessingRequest) => 
      integrator.processWithAIOnly(request),
    
    requestOptimization: (data: any) => 
      integrator.requestAutonomousOptimization(data),
  };
}

// WebSocket client for React components
export class ProductionWebSocketClient {
  private ws: WebSocket | null = null;
  private readonly url: string;
  private messageHandlers = new Map<string, (data: any) => void>();
  
  constructor(url = 'ws://localhost:3000/ws') {
    this.url = url;
  }
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('Connected to production WebSocket');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            const handler = this.messageHandlers.get(message.type);
            if (handler) {
              handler(message.data);
            }
          } catch (error) {
            console.error('WebSocket message parsing failed:', error);
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        this.ws.onclose = () => {
          console.log('WebSocket connection closed');
          this.ws = null;
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  send(type: string, data: any, requestId?: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data, requestId }));
    } else {
      throw new Error('WebSocket not connected');
    }
  }
  
  onMessage(type: string, handler: (data: any) => void) {
    this.messageHandlers.set(type, handler);
  }
  
  removeMessageHandler(type: string) {
    this.messageHandlers.delete(type);
  }
}

export default ProductionWebIntegrator;