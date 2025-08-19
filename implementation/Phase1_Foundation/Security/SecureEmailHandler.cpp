#include "SecureEmailHandler.h"
#include "AdvancedThreatDetection.h"
#include <algorithm>
#include <regex>
#include <fstream>
#include <json/json.h>
#include <chrono>
#include <thread>

namespace hMailServer {
namespace Security {

class SecureEmailHandler::Impl {
public:
    SecurityLevel currentSecurityLevel;
    bool aiIntegrationEnabled;
    std::unordered_map<std::string, std::function<bool(const EmailContent&)>> securityPolicies;
    std::unordered_map<std::string, double> senderReputations;
    std::vector<SecurityResult> recentEvents;
    std::unordered_map<std::string, std::string> configuration;
    std::function<SecurityResult(const EmailContent&)> aiClassificationCallback;
    std::unique_ptr<AdvancedThreatDetection> threatDetection;

    Impl() : currentSecurityLevel(SecurityLevel::Medium), 
             aiIntegrationEnabled(false),
             threatDetection(std::make_unique<AdvancedThreatDetection>()) {}
};

SecureEmailHandler::SecureEmailHandler() : m_impl(std::make_unique<Impl>()) {
    // Initialize default security policies
    AddSecurityPolicy("attachment_size", [](const EmailContent& email) {
        // Check if total attachment size is reasonable (e.g., < 50MB)
        return email.attachments.size() < 20; // Simple check for now
    });

    AddSecurityPolicy("suspicious_keywords", [](const EmailContent& email) {
        std::vector<std::string> suspiciousKeywords = {
            "urgent transfer", "nigerian prince", "lottery winner",
            "click here now", "limited time offer", "act immediately"
        };
        
        std::string content = email.subject + " " + email.body;
        std::transform(content.begin(), content.end(), content.begin(), ::tolower);
        
        for (const auto& keyword : suspiciousKeywords) {
            if (content.find(keyword) != std::string::npos) {
                return false; // Policy violation
            }
        }
        return true;
    });
}

SecureEmailHandler::~SecureEmailHandler() = default;

bool SecureEmailHandler::Initialize(const std::string& configPath) {
    try {
        std::ifstream configFile(configPath);
        if (!configFile.is_open()) {
            // Use default configuration
            m_impl->configuration["max_attachment_size"] = "52428800"; // 50MB
            m_impl->configuration["scan_attachments"] = "true";
            m_impl->configuration["check_sender_reputation"] = "true";
            m_impl->configuration["ai_integration"] = "true";
            return true;
        }

        Json::Value config;
        configFile >> config;
        
        // Load configuration values
        for (const auto& key : config.getMemberNames()) {
            m_impl->configuration[key] = config[key].asString();
        }

        // Initialize threat detection
        if (m_impl->threatDetection) {
            m_impl->threatDetection->Initialize(configPath);
        }

        return true;
    } catch (const std::exception& e) {
        // Log error and use defaults
        return false;
    }
}

void SecureEmailHandler::SetSecurityLevel(SecurityLevel level) {
    m_impl->currentSecurityLevel = level;
}

void SecureEmailHandler::EnableAIIntegration(bool enable) {
    m_impl->aiIntegrationEnabled = enable;
}

SecureEmailHandler::SecurityResult SecureEmailHandler::AnalyzeEmail(const EmailContent& email) {
    SecurityResult result;
    result.isSecure = true;
    result.threatType = ThreatType::None;
    result.level = SecurityLevel::Low;
    result.confidenceScore = 0.0;

    try {
        std::vector<double> threatScores;
        std::vector<std::string> detectedThreats;

        // AI Integration
        if (m_impl->aiIntegrationEnabled && m_impl->aiClassificationCallback) {
            auto aiResult = m_impl->aiClassificationCallback(email);
            if (!aiResult.isSecure) {
                result = aiResult;
                threatScores.push_back(aiResult.confidenceScore);
                detectedThreats.push_back("AI_CLASSIFICATION");
            }
        }

        // Spam detection
        double spamConfidence;
        if (IsSpam(email, spamConfidence)) {
            result.threatType = ThreatType::Spam;
            result.isSecure = false;
            threatScores.push_back(spamConfidence);
            detectedThreats.push_back("SPAM");
        }

        // Phishing detection
        double phishingConfidence;
        if (IsPhishing(email, phishingConfidence)) {
            result.threatType = ThreatType::Phishing;
            result.isSecure = false;
            result.level = SecurityLevel::High;
            threatScores.push_back(phishingConfidence);
            detectedThreats.push_back("PHISHING");
        }

        // Malware detection
        double malwareConfidence;
        if (HasMalware(email, malwareConfidence)) {
            result.threatType = ThreatType::Malware;
            result.isSecure = false;
            result.level = SecurityLevel::Critical;
            threatScores.push_back(malwareConfidence);
            detectedThreats.push_back("MALWARE");
        }

        // Policy violations
        std::string violatedPolicy;
        if (ViolatesPolicy(email, violatedPolicy)) {
            result.threatType = ThreatType::PolicyViolation;
            result.isSecure = false;
            threatScores.push_back(0.8);
            detectedThreats.push_back("POLICY_" + violatedPolicy);
        }

        // Calculate overall confidence and level
        if (!threatScores.empty()) {
            result.confidenceScore = *std::max_element(threatScores.begin(), threatScores.end());
            
            if (result.confidenceScore > 0.9) {
                result.level = SecurityLevel::Critical;
            } else if (result.confidenceScore > 0.7) {
                result.level = SecurityLevel::High;
            } else if (result.confidenceScore > 0.5) {
                result.level = SecurityLevel::Medium;
            }
        }

        // Generate recommendations
        if (!result.isSecure) {
            result.recommendations.push_back("Quarantine email for further analysis");
            
            if (result.threatType == ThreatType::Phishing) {
                result.recommendations.push_back("Warn user about phishing attempt");
                result.recommendations.push_back("Block sender domain");
            } else if (result.threatType == ThreatType::Malware) {
                result.recommendations.push_back("Scan all attachments with updated signatures");
                result.recommendations.push_back("Alert security team immediately");
            }
        }

        // Add metadata
        result.metadata["detected_threats"] = "";
        for (size_t i = 0; i < detectedThreats.size(); ++i) {
            if (i > 0) result.metadata["detected_threats"] += ",";
            result.metadata["detected_threats"] += detectedThreats[i];
        }
        result.metadata["sender_reputation"] = std::to_string(GetSenderReputation(email.sender));
        result.metadata["analysis_timestamp"] = std::to_string(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());

        // Log security event
        LogSecurityEvent(email, result);

        return result;

    } catch (const std::exception& e) {
        // Return safe default
        result.isSecure = false;
        result.threatType = ThreatType::Suspicious;
        result.level = SecurityLevel::High;
        result.confidenceScore = 0.5;
        result.reason = "Analysis error: " + std::string(e.what());
        return result;
    }
}

bool SecureEmailHandler::IsSpam(const EmailContent& email, double& confidence) {
    confidence = 0.0;
    
    // Basic spam indicators
    std::string content = email.subject + " " + email.body;
    std::transform(content.begin(), content.end(), content.begin(), ::tolower);
    
    // Check for spam patterns
    std::vector<std::string> spamPatterns = {
        "lottery", "winner", "congratulations", "urgent", "act now",
        "click here", "limited time", "free money", "no obligation"
    };
    
    int spamIndicators = 0;
    for (const auto& pattern : spamPatterns) {
        if (content.find(pattern) != std::string::npos) {
            spamIndicators++;
            confidence += 0.15;
        }
    }
    
    // Check sender reputation
    double senderRep = GetSenderReputation(email.sender);
    if (senderRep < 0.3) {
        confidence += 0.4;
    }
    
    // Check for excessive punctuation
    int exclamationCount = std::count(content.begin(), content.end(), '!');
    if (exclamationCount > 3) {
        confidence += 0.2;
    }
    
    confidence = std::min(confidence, 1.0);
    return confidence > 0.5;
}

bool SecureEmailHandler::IsPhishing(const EmailContent& email, double& confidence) {
    confidence = 0.0;
    
    // Use advanced threat detection
    if (m_impl->threatDetection) {
        return m_impl->threatDetection->DetectPhishing(email.body, confidence);
    }
    
    // Fallback basic phishing detection
    std::string content = email.subject + " " + email.body;
    std::transform(content.begin(), content.end(), content.begin(), ::tolower);
    
    std::vector<std::string> phishingPatterns = {
        "verify your account", "suspend your account", "click here to verify",
        "update your information", "confirm your identity"
    };
    
    for (const auto& pattern : phishingPatterns) {
        if (content.find(pattern) != std::string::npos) {
            confidence += 0.3;
        }
    }
    
    return confidence > 0.6;
}

bool SecureEmailHandler::HasMalware(const EmailContent& email, double& confidence) {
    confidence = 0.0;
    
    // Use advanced threat detection
    if (m_impl->threatDetection) {
        return m_impl->threatDetection->DetectMalware(email.attachments, confidence);
    }
    
    // Basic attachment check
    for (const auto& attachment : email.attachments) {
        std::string ext = attachment.substr(attachment.find_last_of('.') + 1);
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        
        std::vector<std::string> dangerousExtensions = {
            "exe", "scr", "bat", "com", "pif", "cmd", "vbs", "js"
        };
        
        if (std::find(dangerousExtensions.begin(), dangerousExtensions.end(), ext) 
            != dangerousExtensions.end()) {
            confidence += 0.7;
        }
    }
    
    return confidence > 0.5;
}

bool SecureEmailHandler::ViolatesPolicy(const EmailContent& email, std::string& policyName) {
    for (const auto& policy : m_impl->securityPolicies) {
        if (!policy.second(email)) {
            policyName = policy.first;
            return true;
        }
    }
    return false;
}

double SecureEmailHandler::GetSenderReputation(const std::string& sender) {
    auto it = m_impl->senderReputations.find(sender);
    if (it != m_impl->senderReputations.end()) {
        return it->second;
    }
    
    // Default reputation for unknown senders
    // In a real implementation, this would query external reputation services
    return 0.5;
}

void SecureEmailHandler::UpdateSenderReputation(const std::string& sender, double score) {
    m_impl->senderReputations[sender] = std::max(0.0, std::min(1.0, score));
}

void SecureEmailHandler::AddSecurityPolicy(const std::string& name, 
                                          std::function<bool(const EmailContent&)> policy) {
    m_impl->securityPolicies[name] = policy;
}

void SecureEmailHandler::SetAIClassificationCallback(
    std::function<SecurityResult(const EmailContent&)> callback) {
    m_impl->aiClassificationCallback = callback;
}

void SecureEmailHandler::LogSecurityEvent(const EmailContent& email, const SecurityResult& result) {
    // Keep only last 1000 events
    if (m_impl->recentEvents.size() >= 1000) {
        m_impl->recentEvents.erase(m_impl->recentEvents.begin());
    }
    
    m_impl->recentEvents.push_back(result);
}

std::vector<SecureEmailHandler::SecurityResult> 
SecureEmailHandler::GetRecentSecurityEvents(int count) {
    int start = std::max(0, static_cast<int>(m_impl->recentEvents.size()) - count);
    return std::vector<SecurityResult>(
        m_impl->recentEvents.begin() + start, 
        m_impl->recentEvents.end());
}

} // namespace Security
} // namespace hMailServer