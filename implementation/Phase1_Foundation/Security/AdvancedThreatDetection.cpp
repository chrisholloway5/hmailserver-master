#include "AdvancedThreatDetection.h"
#include <algorithm>
#include <regex>
#include <fstream>
#include <unordered_set>

namespace hMailServer {
namespace Security {

class AdvancedThreatDetection::Impl {
public:
    std::unordered_set<std::string> threatSignatures;
    std::unordered_set<std::string> urlBlacklist;
    std::unordered_map<std::string, std::string> signatureTypes;
    std::unordered_map<std::string, std::vector<std::string>> behaviorPatterns;
    bool initialized;

    Impl() : initialized(false) {}
};

AdvancedThreatDetection::AdvancedThreatDetection() : m_impl(std::make_unique<Impl>()) {}

AdvancedThreatDetection::~AdvancedThreatDetection() = default;

bool AdvancedThreatDetection::Initialize(const std::string& configPath) {
    try {
        // Initialize default threat signatures
        m_impl->threatSignatures.insert("urgent.transfer");
        m_impl->threatSignatures.insert("nigerian.prince");
        m_impl->threatSignatures.insert("lottery.winner");
        m_impl->threatSignatures.insert("click.here.now");
        m_impl->threatSignatures.insert("verify.account");
        m_impl->threatSignatures.insert("suspended.account");
        
        // Initialize URL blacklist
        m_impl->urlBlacklist.insert("suspicious-site.com");
        m_impl->urlBlacklist.insert("phishing-example.net");
        m_impl->urlBlacklist.insert("malware-host.org");
        
        m_impl->initialized = true;
        return true;
    } catch (const std::exception& e) {
        return false;
    }
}

bool AdvancedThreatDetection::DetectPhishing(const std::string& content, double& confidence) {
    confidence = 0.0;
    
    if (!m_impl->initialized) {
        return false;
    }
    
    std::string lowerContent = content;
    std::transform(lowerContent.begin(), lowerContent.end(), lowerContent.begin(), ::tolower);
    
    // Replace spaces with dots for signature matching
    std::string normalizedContent = lowerContent;
    std::replace(normalizedContent.begin(), normalizedContent.end(), ' ', '.');
    
    // Check against phishing signatures
    std::vector<std::string> phishingPatterns = {
        "verify.your.account", "suspended.account", "click.here.to.verify",
        "update.your.information", "confirm.your.identity", "urgent.action.required",
        "account.will.be.closed", "suspicious.activity.detected"
    };
    
    int matchCount = 0;
    for (const auto& pattern : phishingPatterns) {
        if (normalizedContent.find(pattern) != std::string::npos) {
            matchCount++;
            confidence += 0.2;
        }
    }
    
    // Check for URL spoofing patterns
    std::regex urlRegex(R"(https?://[^\s]+)");
    std::sregex_iterator urlBegin(content.begin(), content.end(), urlRegex);
    std::sregex_iterator urlEnd;
    
    for (std::sregex_iterator i = urlBegin; i != urlEnd; ++i) {
        std::string url = (*i).str();
        double urlRisk;
        if (AnalyzeURL(url, urlRisk)) {
            confidence += urlRisk * 0.4;
        }
    }
    
    // Check for urgency indicators
    std::vector<std::string> urgencyPatterns = {
        "immediate", "urgent", "expire", "suspend", "terminate", "limited time"
    };
    
    for (const auto& pattern : urgencyPatterns) {
        if (lowerContent.find(pattern) != std::string::npos) {
            confidence += 0.1;
        }
    }
    
    confidence = std::min(confidence, 1.0);
    return confidence > 0.6;
}

bool AdvancedThreatDetection::DetectMalware(const std::vector<std::string>& attachments, double& confidence) {
    confidence = 0.0;
    
    if (!m_impl->initialized) {
        return false;
    }
    
    // Dangerous file extensions
    std::unordered_set<std::string> dangerousExtensions = {
        "exe", "scr", "bat", "com", "pif", "cmd", "vbs", "js", "jar",
        "msi", "dll", "sys", "drv", "ocx", "cpl", "src", "asp", "php"
    };
    
    // Suspicious double extensions
    std::vector<std::string> doubleExtensions = {
        ".pdf.exe", ".doc.exe", ".jpg.exe", ".txt.exe"
    };
    
    for (const auto& attachment : attachments) {
        std::string lowerAttachment = attachment;
        std::transform(lowerAttachment.begin(), lowerAttachment.end(), 
                      lowerAttachment.begin(), ::tolower);
        
        // Check for dangerous extensions
        size_t dotPos = lowerAttachment.find_last_of('.');
        if (dotPos != std::string::npos) {
            std::string ext = lowerAttachment.substr(dotPos + 1);
            if (dangerousExtensions.find(ext) != dangerousExtensions.end()) {
                confidence += 0.7;
            }
        }
        
        // Check for double extensions
        for (const auto& doubleExt : doubleExtensions) {
            if (lowerAttachment.find(doubleExt) != std::string::npos) {
                confidence += 0.9;
            }
        }
        
        // Check for suspicious filenames
        std::vector<std::string> suspiciousNames = {
            "invoice", "receipt", "document", "photo", "image", "update"
        };
        
        for (const auto& suspName : suspiciousNames) {
            if (lowerAttachment.find(suspName) != std::string::npos && 
                lowerAttachment.find(".exe") != std::string::npos) {
                confidence += 0.5;
            }
        }
    }
    
    confidence = std::min(confidence, 1.0);
    return confidence > 0.5;
}

bool AdvancedThreatDetection::DetectSuspiciousPatterns(const std::string& content, double& confidence) {
    confidence = 0.0;
    
    std::string lowerContent = content;
    std::transform(lowerContent.begin(), lowerContent.end(), lowerContent.begin(), ::tolower);
    
    // Check for suspicious patterns
    std::vector<std::string> suspiciousPatterns = {
        "wire transfer", "western union", "money gram", "bitcoin", "cryptocurrency",
        "inheritance", "beneficiary", "confidential", "classified", "top secret"
    };
    
    for (const auto& pattern : suspiciousPatterns) {
        if (lowerContent.find(pattern) != std::string::npos) {
            confidence += 0.2;
        }
    }
    
    // Check for excessive capitalization
    int capitalCount = 0;
    int letterCount = 0;
    for (char c : content) {
        if (std::isalpha(c)) {
            letterCount++;
            if (std::isupper(c)) {
                capitalCount++;
            }
        }
    }
    
    if (letterCount > 0) {
        double capitalRatio = static_cast<double>(capitalCount) / letterCount;
        if (capitalRatio > 0.3) {
            confidence += 0.2;
        }
    }
    
    // Check for excessive punctuation
    int exclamationCount = std::count(content.begin(), content.end(), '!');
    if (exclamationCount > 5) {
        confidence += 0.3;
    }
    
    confidence = std::min(confidence, 1.0);
    return confidence > 0.4;
}

bool AdvancedThreatDetection::AnalyzeURL(const std::string& url, double& riskScore) {
    riskScore = 0.0;
    
    std::string lowerUrl = url;
    std::transform(lowerUrl.begin(), lowerUrl.end(), lowerUrl.begin(), ::tolower);
    
    // Check blacklist
    for (const auto& blacklistedDomain : m_impl->urlBlacklist) {
        if (lowerUrl.find(blacklistedDomain) != std::string::npos) {
            riskScore = 1.0;
            return true;
        }
    }
    
    // Check for suspicious characteristics
    
    // 1. IP addresses instead of domain names
    std::regex ipRegex(R"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})");
    if (std::regex_search(url, ipRegex)) {
        riskScore += 0.4;
    }
    
    // 2. Suspicious TLDs
    std::vector<std::string> suspiciousTlds = {".tk", ".ml", ".ga", ".cf"};
    for (const auto& tld : suspiciousTlds) {
        if (lowerUrl.find(tld) != std::string::npos) {
            riskScore += 0.3;
        }
    }
    
    // 3. URL shorteners
    std::vector<std::string> shorteners = {"bit.ly", "tinyurl", "t.co", "goo.gl"};
    for (const auto& shortener : shorteners) {
        if (lowerUrl.find(shortener) != std::string::npos) {
            riskScore += 0.2;
        }
    }
    
    // 4. Excessive subdomains
    size_t subdomainCount = std::count(lowerUrl.begin(), lowerUrl.end(), '.');
    if (subdomainCount > 4) {
        riskScore += 0.2;
    }
    
    // 5. Suspicious keywords in URL
    std::vector<std::string> suspiciousKeywords = {
        "secure", "verify", "account", "update", "confirm", "login"
    };
    for (const auto& keyword : suspiciousKeywords) {
        if (lowerUrl.find(keyword) != std::string::npos) {
            riskScore += 0.1;
        }
    }
    
    riskScore = std::min(riskScore, 1.0);
    return riskScore > 0.5;
}

bool AdvancedThreatDetection::IsURLInBlacklist(const std::string& url) {
    std::string lowerUrl = url;
    std::transform(lowerUrl.begin(), lowerUrl.end(), lowerUrl.begin(), ::tolower);
    
    for (const auto& blacklistedDomain : m_impl->urlBlacklist) {
        if (lowerUrl.find(blacklistedDomain) != std::string::npos) {
            return true;
        }
    }
    return false;
}

bool AdvancedThreatDetection::AddThreatSignature(const std::string& signature, const std::string& threatType) {
    m_impl->threatSignatures.insert(signature);
    m_impl->signatureTypes[signature] = threatType;
    return true;
}

bool AdvancedThreatDetection::AnalyzeBehaviorPattern(const std::string& senderEmail,
                                                   const std::vector<std::string>& recentEmails,
                                                   double& anomalyScore) {
    anomalyScore = 0.0;
    
    // Simple behavioral analysis
    if (recentEmails.size() > 10) {
        // Sender is sending too many emails in a short period
        anomalyScore += 0.3;
    }
    
    // Check for pattern consistency
    if (recentEmails.size() >= 2) {
        // Analyze if the content patterns are suspicious
        // This is a simplified implementation
        bool hasVariedContent = false;
        for (size_t i = 1; i < recentEmails.size(); ++i) {
            if (recentEmails[i] != recentEmails[i-1]) {
                hasVariedContent = true;
                break;
            }
        }
        
        if (!hasVariedContent) {
            anomalyScore += 0.4; // Identical emails might be spam
        }
    }
    
    return anomalyScore > 0.5;
}

} // namespace Security
} // namespace hMailServer