#pragma once

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>

namespace hMailServer {
namespace Security {

/**
 * Advanced threat detection system using machine learning and heuristic analysis
 */
class AdvancedThreatDetection {
public:
    AdvancedThreatDetection();
    ~AdvancedThreatDetection();

    // Initialization
    bool Initialize(const std::string& configPath);
    bool LoadThreatSignatures(const std::string& signaturesPath);

    // Threat detection methods
    bool DetectPhishing(const std::string& content, double& confidence);
    bool DetectMalware(const std::vector<std::string>& attachments, double& confidence);
    bool DetectSuspiciousPatterns(const std::string& content, double& confidence);
    
    // URL analysis
    bool AnalyzeURL(const std::string& url, double& riskScore);
    bool IsURLInBlacklist(const std::string& url);
    
    // Machine learning integration
    bool TrainModel(const std::vector<std::string>& trainingData);
    bool UpdateThreatModel(const std::string& newThreatData);
    
    // Signature-based detection
    bool AddThreatSignature(const std::string& signature, const std::string& threatType);
    bool RemoveThreatSignature(const std::string& signature);
    
    // Behavioral analysis
    bool AnalyzeBehaviorPattern(const std::string& senderEmail, 
                               const std::vector<std::string>& recentEmails,
                               double& anomalyScore);

private:
    class Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace Security
} // namespace hMailServer