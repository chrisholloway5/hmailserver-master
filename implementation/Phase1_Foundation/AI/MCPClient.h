#pragma once

#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <unordered_map>
#include <nlohmann/json.hpp>

namespace HM {
namespace AI {

/**
 * @brief Model Context Protocol (MCP) Client Implementation
 * 
 * This class provides the foundation for integrating various AI models
 * through the Model Context Protocol, enabling context-aware email processing.
 */
class MCPClient {
public:
    struct ModelInfo {
        std::string id;
        std::string name;
        std::string provider;
        std::string version;
        std::vector<std::string> capabilities;
        bool isLocal;
        std::string endpoint;
    };

    struct ContextFrame {
        std::string frameId;
        std::string userId;
        std::string sessionId;
        nlohmann::json context;
        int64_t timestamp;
        std::string contentType;
    };

    struct AIRequest {
        std::string modelId;
        std::string prompt;
        nlohmann::json context;
        std::unordered_map<std::string, std::string> parameters;
        bool preserveContext;
        std::string requestId;
    };

    struct AIResponse {
        std::string requestId;
        std::string modelId;
        std::string content;
        nlohmann::json metadata;
        bool success;
        std::string error;
        double confidence;
        int64_t processingTimeMs;
    };

    enum class ModelCapability {
        TEXT_GENERATION,
        TEXT_ANALYSIS,
        SENTIMENT_ANALYSIS,
        LANGUAGE_DETECTION,
        TRANSLATION,
        SUMMARIZATION,
        INTENT_RECOGNITION,
        SPAM_DETECTION,
        SECURITY_ANALYSIS,
        EMAIL_CLASSIFICATION,
        RESPONSE_GENERATION
    };

public:
    MCPClient();
    virtual ~MCPClient();

    // Model Management
    bool Initialize(const std::string& configPath);
    bool RegisterModel(const ModelInfo& modelInfo);
    bool UnregisterModel(const std::string& modelId);
    std::vector<ModelInfo> GetAvailableModels() const;
    ModelInfo GetModelInfo(const std::string& modelId) const;
    bool IsModelAvailable(const std::string& modelId) const;

    // Context Management
    bool CreateContext(const std::string& contextId, const std::string& userId);
    bool UpdateContext(const std::string& contextId, const nlohmann::json& context);
    nlohmann::json GetContext(const std::string& contextId) const;
    bool ClearContext(const std::string& contextId);
    bool PersistContext(const std::string& contextId);

    // AI Processing
    AIResponse ProcessRequest(const AIRequest& request);
    void ProcessRequestAsync(const AIRequest& request, 
                           std::function<void(const AIResponse&)> callback);
    
    // Specialized Email Processing
    AIResponse AnalyzeEmail(const std::string& emailContent, 
                          const std::string& context = "");
    AIResponse ClassifyEmail(const std::string& emailContent);
    AIResponse DetectSpam(const std::string& emailContent);
    AIResponse GenerateResponse(const std::string& emailContent, 
                              const std::string& userContext);
    AIResponse SummarizeEmail(const std::string& emailContent);
    AIResponse ExtractIntents(const std::string& emailContent);

    // Model Ensemble Support
    AIResponse ProcessWithEnsemble(const std::vector<std::string>& modelIds,
                                 const AIRequest& request);
    
    // Performance Monitoring
    struct ModelStats {
        std::string modelId;
        int64_t totalRequests;
        int64_t successfulRequests;
        double averageResponseTime;
        double averageConfidence;
        int64_t lastUsed;
    };
    
    ModelStats GetModelStats(const std::string& modelId) const;
    void ResetModelStats(const std::string& modelId);

    // Configuration
    bool LoadConfiguration(const std::string& configPath);
    bool SaveConfiguration(const std::string& configPath) const;
    void SetParameter(const std::string& key, const std::string& value);
    std::string GetParameter(const std::string& key) const;

    // Event Callbacks
    void SetModelConnectionCallback(std::function<void(const std::string&, bool)> callback);
    void SetContextUpdateCallback(std::function<void(const std::string&)> callback);
    void SetErrorCallback(std::function<void(const std::string&, const std::string&)> callback);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
};

/**
 * @brief Context-Aware Email Intelligence Engine
 * 
 * High-level interface for AI-powered email processing that uses MCP
 * to coordinate multiple AI models for comprehensive email intelligence.
 */
class EmailIntelligenceEngine {
public:
    struct EmailAnalysis {
        std::string emailId;
        double spamProbability;
        std::string sentimentScore;
        std::vector<std::string> detectedLanguages;
        std::vector<std::string> extractedIntents;
        std::string classification;
        std::string priority;
        std::vector<std::string> suggestedActions;
        std::string summary;
        nlohmann::json metadata;
    };

    struct UserContext {
        std::string userId;
        std::string preferredLanguage;
        std::vector<std::string> interests;
        std::unordered_map<std::string, std::string> communicationPatterns;
        nlohmann::json preferences;
    };

public:
    EmailIntelligenceEngine(std::shared_ptr<MCPClient> mcpClient);
    virtual ~EmailIntelligenceEngine();

    // Core Intelligence Functions
    EmailAnalysis AnalyzeEmail(const std::string& emailContent,
                             const UserContext& userContext);
    
    std::string GenerateSmartReply(const std::string& emailContent,
                                 const UserContext& userContext,
                                 const std::string& replyType = "auto");
    
    std::vector<std::string> SuggestActions(const std::string& emailContent,
                                          const UserContext& userContext);
    
    bool ShouldAutoProcess(const EmailAnalysis& analysis);
    
    std::string TranslateEmail(const std::string& emailContent,
                             const std::string& targetLanguage);

    // Learning and Adaptation
    void LearnFromUserFeedback(const std::string& emailId,
                             const std::string& userAction,
                             bool wasCorrect);
    
    void UpdateUserContext(const std::string& userId,
                         const nlohmann::json& contextUpdate);

    // Real-time Processing
    void StartRealtimeProcessing();
    void StopRealtimeProcessing();
    void ProcessEmailStream(const std::string& emailStream);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
    std::shared_ptr<MCPClient> mcpClient_;
};

} // namespace AI
} // namespace HM