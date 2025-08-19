#pragma once

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <functional>

namespace hMailServer {
namespace Security {

/**
 * Enhanced secure email handler with AI-powered threat detection
 * Integrates with the AI classification system for comprehensive security
 */
class SecureEmailHandler {
public:
    enum class SecurityLevel {
        Low = 1,
        Medium = 2,
        High = 3,
        Critical = 4
    };

    enum class ThreatType {
        None,
        Spam,
        Phishing,
        Malware,
        Suspicious,
        PolicyViolation
    };

    struct SecurityResult {
        bool isSecure;
        ThreatType threatType;
        SecurityLevel level;
        double confidenceScore;
        std::string reason;
        std::vector<std::string> recommendations;
        std::unordered_map<std::string, std::string> metadata;
    };

    struct EmailContent {
        std::string sender;
        std::vector<std::string> recipients;
        std::string subject;
        std::string body;
        std::vector<std::string> attachments;
        std::unordered_map<std::string, std::string> headers;
    };

public:
    SecureEmailHandler();
    ~SecureEmailHandler();

    // Initialization and configuration
    bool Initialize(const std::string& configPath);
    void SetSecurityLevel(SecurityLevel level);
    void EnableAIIntegration(bool enable);

    // Main security analysis
    SecurityResult AnalyzeEmail(const EmailContent& email);
    SecurityResult AnalyzeEmailAsync(const EmailContent& email);

    // Specific security checks
    bool IsSpam(const EmailContent& email, double& confidence);
    bool IsPhishing(const EmailContent& email, double& confidence);
    bool HasMalware(const EmailContent& email, double& confidence);
    bool ViolatesPolicy(const EmailContent& email, std::string& policyName);

    // Attachment security
    bool ScanAttachments(const std::vector<std::string>& attachments);
    bool IsAttachmentSafe(const std::string& filename, const std::vector<uint8_t>& content);

    // URL security
    bool ScanURLs(const std::string& content, std::vector<std::string>& suspiciousURLs);
    bool IsURLSafe(const std::string& url);

    // Sender reputation
    double GetSenderReputation(const std::string& sender);
    void UpdateSenderReputation(const std::string& sender, double score);

    // Policy management
    void AddSecurityPolicy(const std::string& name, std::function<bool(const EmailContent&)> policy);
    void RemoveSecurityPolicy(const std::string& name);
    std::vector<std::string> GetActivePolicies() const;

    // AI integration
    void SetAIClassificationCallback(std::function<SecurityResult(const EmailContent&)> callback);
    
    // Reporting and logging
    void LogSecurityEvent(const EmailContent& email, const SecurityResult& result);
    std::vector<SecurityResult> GetRecentSecurityEvents(int count = 100);

    // Configuration
    void SetConfigValue(const std::string& key, const std::string& value);
    std::string GetConfigValue(const std::string& key) const;

private:
    class Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace Security
} // namespace hMailServer