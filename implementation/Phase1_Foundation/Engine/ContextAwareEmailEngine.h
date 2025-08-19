#pragma once

#include "../AI/MCPClient.h"
#include "../Security/ZeroTrustFramework.h"
#include <memory>
#include <vector>
#include <string>
#include <chrono>
#include <functional>
#include <nlohmann/json.hpp>

namespace HM {
namespace Engine {

/**
 * @brief Context-Aware Email Processing Engine
 * 
 * The core intelligence engine that processes emails with full context awareness,
 * using AI models and security frameworks to provide intelligent email management.
 */
class ContextAwareEmailEngine {
public:
    struct EmailContext {
        std::string emailId;
        std::string threadId;
        std::string senderId;
        std::string recipientId;
        std::vector<std::string> ccRecipients;
        std::vector<std::string> bccRecipients;
        std::string subject;
        std::string body;
        std::vector<std::string> attachments;
        std::chrono::system_clock::time_point timestamp;
        std::unordered_map<std::string, std::string> headers;
        nlohmann::json metadata;
    };

    struct ProcessingResult {
        std::string emailId;
        bool shouldDeliver;
        bool isSpam;
        bool isThreat;
        double confidenceScore;
        std::string classification;
        std::string priority;
        std::vector<std::string> suggestedActions;
        std::string autoResponse;
        nlohmann::json analysis;
        std::vector<std::string> appliedRules;
        std::chrono::system_clock::time_point processedAt;
    };

    struct UserProfile {
        std::string userId;
        std::string preferredLanguage;
        std::vector<std::string> interests;
        std::unordered_map<std::string, std::string> communicationPatterns;
        std::unordered_map<std::string, double> senderTrustScores;
        nlohmann::json preferences;
        std::chrono::system_clock::time_point lastUpdated;
    };

    struct ContextualRule {
        std::string ruleId;
        std::string name;
        std::string description;
        std::string condition;
        std::string action;
        int priority;
        bool isActive;
        std::chrono::system_clock::time_point createdAt;
        std::unordered_map<std::string, std::string> parameters;
    };

    enum class ProcessingMode {
        SYNCHRONOUS,
        ASYNCHRONOUS,
        REAL_TIME_STREAM,
        BATCH_PROCESSING
    };

public:
    ContextAwareEmailEngine(std::shared_ptr<AI::MCPClient> aiClient,
                           std::shared_ptr<Security::ZeroTrustFramework> securityFramework);
    virtual ~ContextAwareEmailEngine();

    // Core Processing
    bool Initialize(const std::string& configPath);
    ProcessingResult ProcessEmail(const EmailContext& email, 
                                const UserProfile& userProfile,
                                ProcessingMode mode = ProcessingMode::SYNCHRONOUS);
    
    void ProcessEmailAsync(const EmailContext& email, 
                         const UserProfile& userProfile,
                         std::function<void(const ProcessingResult&)> callback);
    
    // Context Management
    bool CreateUserContext(const std::string& userId);
    bool UpdateUserProfile(const UserProfile& profile);
    UserProfile GetUserProfile(const std::string& userId);
    bool DeleteUserContext(const std::string& userId);
    
    // Intelligent Features
    std::vector<std::string> GenerateSmartReplies(const EmailContext& email,
                                                 const UserProfile& userProfile);
    std::string SummarizeEmailThread(const std::vector<EmailContext>& thread);
    std::vector<std::string> ExtractActionItems(const EmailContext& email);
    std::string TranslateEmail(const EmailContext& email, const std::string& targetLanguage);
    
    // Predictive Capabilities
    double PredictEmailImportance(const EmailContext& email, const UserProfile& userProfile);
    std::chrono::system_clock::time_point PredictOptimalResponseTime(const EmailContext& email);
    std::vector<std::string> PredictUserActions(const EmailContext& email, 
                                               const UserProfile& userProfile);
    
    // Learning and Adaptation
    void LearnFromUserBehavior(const std::string& userId, 
                             const std::string& emailId,
                             const std::string& userAction,
                             bool wasCorrect);
    void AdaptToUserPreferences(const std::string& userId,
                              const nlohmann::json& feedbackData);
    void UpdateMLModels();
    
    // Rule Engine
    bool AddContextualRule(const ContextualRule& rule);
    bool RemoveContextualRule(const std::string& ruleId);
    bool UpdateContextualRule(const ContextualRule& rule);
    std::vector<ContextualRule> GetActiveRules(const std::string& userId);
    std::vector<std::string> EvaluateRules(const EmailContext& email, 
                                         const UserProfile& userProfile);
    
    // Security Integration
    bool ValidateEmailSecurity(const EmailContext& email);
    Security::ZeroTrustFramework::ThreatLevel AssessEmailThreatLevel(const EmailContext& email);
    bool QuarantineEmail(const std::string& emailId, const std::string& reason);
    bool ReleaseEmailFromQuarantine(const std::string& emailId);
    
    // Performance and Monitoring
    struct EngineStats {
        uint64_t totalEmailsProcessed;
        uint64_t spamDetected;
        uint64_t threatsBlocked;
        double averageProcessingTime;
        double accuracyRate;
        std::chrono::system_clock::time_point lastUpdated;
    };
    
    EngineStats GetEngineStatistics();
    void ResetStatistics();
    
    // Real-time Stream Processing
    bool StartStreamProcessing();
    bool StopStreamProcessing();
    void ProcessEmailStream(const std::vector<EmailContext>& emailBatch);
    
    // Configuration
    bool SetConfiguration(const std::string& key, const std::string& value);
    std::string GetConfiguration(const std::string& key);
    bool LoadConfiguration(const std::string& configPath);
    bool SaveConfiguration(const std::string& configPath);
    
    // Event Callbacks
    void SetEmailProcessedCallback(std::function<void(const ProcessingResult&)> callback);
    void SetThreatDetectedCallback(std::function<void(const EmailContext&, const std::string&)> callback);
    void SetUserLearningCallback(std::function<void(const std::string&, const nlohmann::json&)> callback);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
    std::shared_ptr<AI::MCPClient> aiClient_;
    std::shared_ptr<Security::ZeroTrustFramework> securityFramework_;
};

/**
 * @brief Sequential Thinking Email Processor
 * 
 * Implements the Sequential Thinking Architecture for advanced email processing
 * that observes, analyzes, predicts, adapts, learns, evolves, and transcends.
 */
class SequentialThinkingProcessor {
public:
    enum class ThinkingStage {
        OBSERVE,     // Monitor email patterns and context
        ANALYZE,     // Process data using AI and historical context
        PREDICT,     // Anticipate user needs and potential issues
        ADAPT,       // Dynamically adjust responses and configurations
        LEARN,       // Continuously improve through feedback
        EVOLVE,      // Self-optimize architecture and capabilities
        TRANSCEND    // Provide insights beyond traditional email functionality
    };

    struct ThinkingContext {
        std::string contextId;
        std::string emailId;
        std::string userId;
        ThinkingStage currentStage;
        nlohmann::json observations;
        nlohmann::json analysis;
        nlohmann::json predictions;
        nlohmann::json adaptations;
        nlohmann::json learnings;
        nlohmann::json evolution;
        nlohmann::json transcendence;
        std::chrono::system_clock::time_point startTime;
        std::chrono::system_clock::time_point lastUpdate;
    };

    struct InsightResult {
        std::string insightId;
        std::string type;
        std::string description;
        double confidence;
        nlohmann::json data;
        std::vector<std::string> recommendations;
        std::chrono::system_clock::time_point generatedAt;
    };

public:
    SequentialThinkingProcessor(std::shared_ptr<ContextAwareEmailEngine> engine);
    virtual ~SequentialThinkingProcessor();

    // Sequential Thinking Process
    bool InitializeThinking(const std::string& contextId, 
                          const ContextAwareEmailEngine::EmailContext& email);
    bool AdvanceThinking(const std::string& contextId);
    ThinkingContext GetThinkingContext(const std::string& contextId);
    bool CompleteThinking(const std::string& contextId);
    
    // Stage-Specific Processing
    bool ObserveEmail(const std::string& contextId);
    bool AnalyzeContext(const std::string& contextId);
    bool PredictOutcomes(const std::string& contextId);
    bool AdaptResponse(const std::string& contextId);
    bool LearnFromResult(const std::string& contextId);
    bool EvolveCapabilities(const std::string& contextId);
    bool TranscendLimitations(const std::string& contextId);
    
    // Insight Generation
    std::vector<InsightResult> GenerateInsights(const std::string& contextId);
    InsightResult GetDeepInsight(const std::string& emailId, const std::string& userId);
    std::vector<InsightResult> GetUserInsights(const std::string& userId);
    
    // Meta-Learning
    void UpdateMetaLearning(const std::vector<ThinkingContext>& contexts);
    nlohmann::json GetMetaInsights();
    bool SelfOptimize();
    
    // Consciousness-Level Processing
    bool EnableConsciousnessMode(bool enable);
    nlohmann::json GetConsciousnessState();
    bool SimulateUserPerspective(const std::string& userId);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
    std::shared_ptr<ContextAwareEmailEngine> engine_;
};

/**
 * @brief Email Intelligence Orchestrator
 * 
 * High-level orchestrator that coordinates all intelligent email processing
 * components and provides a unified interface for the email system.
 */
class EmailIntelligenceOrchestrator {
public:
    EmailIntelligenceOrchestrator();
    virtual ~EmailIntelligenceOrchestrator();

    // System Initialization
    bool Initialize(const std::string& configPath);
    bool Start();
    bool Stop();
    bool Restart();
    
    // Component Management
    bool RegisterEngine(std::shared_ptr<ContextAwareEmailEngine> engine);
    bool RegisterProcessor(std::shared_ptr<SequentialThinkingProcessor> processor);
    bool RegisterAIClient(std::shared_ptr<AI::MCPClient> aiClient);
    bool RegisterSecurityFramework(std::shared_ptr<Security::ZeroTrustFramework> security);
    
    // Unified Processing Interface
    ContextAwareEmailEngine::ProcessingResult ProcessEmail(
        const ContextAwareEmailEngine::EmailContext& email,
        const std::string& userId);
    
    void ProcessEmailBatch(const std::vector<ContextAwareEmailEngine::EmailContext>& emails,
                         const std::string& userId);
    
    // System Intelligence
    nlohmann::json GetSystemIntelligence();
    std::vector<std::string> GetSystemRecommendations();
    bool OptimizeSystemPerformance();
    
    // Monitoring and Health
    struct SystemHealth {
        bool isHealthy;
        std::vector<std::string> issues;
        std::unordered_map<std::string, double> metrics;
        std::chrono::system_clock::time_point lastChecked;
    };
    
    SystemHealth CheckSystemHealth();
    void StartHealthMonitoring();
    void StopHealthMonitoring();

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
};

} // namespace Engine
} // namespace HM