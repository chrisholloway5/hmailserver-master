#pragma once

#include <memory>
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <chrono>

namespace HM {
namespace Security {

/**
 * @brief Zero-Trust Security Framework
 * 
 * Implements zero-trust security principles with continuous verification,
 * behavioral analysis, and adaptive threat response.
 */
class ZeroTrustFramework {
public:
    enum class ThreatLevel {
        MINIMAL = 0,
        LOW = 1,
        MEDIUM = 2,
        HIGH = 3,
        CRITICAL = 4
    };

    enum class VerificationMethod {
        PASSWORD,
        MFA,
        BIOMETRIC,
        BEHAVIORAL,
        DEVICE_FINGERPRINT,
        LOCATION_BASED,
        TIME_BASED,
        CERTIFICATE
    };

    struct SecurityContext {
        std::string userId;
        std::string sessionId;
        std::string deviceId;
        std::string ipAddress;
        std::string userAgent;
        std::string location;
        std::chrono::system_clock::time_point timestamp;
        ThreatLevel currentThreatLevel;
        std::vector<VerificationMethod> activeVerifications;
        std::unordered_map<std::string, std::string> attributes;
    };

    struct SecurityEvent {
        std::string eventId;
        std::string eventType;
        std::string userId;
        std::string description;
        ThreatLevel threatLevel;
        std::chrono::system_clock::time_point timestamp;
        std::unordered_map<std::string, std::string> metadata;
    };

    struct AccessRequest {
        std::string requestId;
        std::string userId;
        std::string resourceId;
        std::string action;
        SecurityContext context;
        std::unordered_map<std::string, std::string> parameters;
    };

    struct AccessDecision {
        std::string requestId;
        bool granted;
        std::string reason;
        ThreatLevel riskLevel;
        std::vector<VerificationMethod> requiredAdditionalAuth;
        std::chrono::seconds validityDuration;
        std::unordered_map<std::string, std::string> conditions;
    };

public:
    ZeroTrustFramework();
    virtual ~ZeroTrustFramework();

    // Core Zero-Trust Functions
    bool Initialize(const std::string& configPath);
    AccessDecision EvaluateAccess(const AccessRequest& request);
    bool ValidateSecurityContext(const SecurityContext& context);
    ThreatLevel AssessThreatLevel(const SecurityContext& context);
    
    // Continuous Verification
    bool StartContinuousMonitoring(const std::string& userId);
    bool StopContinuousMonitoring(const std::string& userId);
    void UpdateUserBehaviorProfile(const std::string& userId, 
                                 const std::unordered_map<std::string, std::string>& behaviorData);
    
    // Behavioral Analysis
    bool DetectAnomalousActivity(const SecurityContext& context);
    double CalculateBehavioralRiskScore(const std::string& userId, 
                                      const SecurityContext& context);
    void LearnNormalBehavior(const std::string& userId, 
                           const SecurityContext& context);
    
    // Device Trust Management
    bool RegisterTrustedDevice(const std::string& userId, const std::string& deviceId);
    bool RevokeTrustedDevice(const std::string& userId, const std::string& deviceId);
    bool IsDeviceTrusted(const std::string& userId, const std::string& deviceId);
    std::string GenerateDeviceFingerprint(const SecurityContext& context);
    
    // Adaptive Authentication
    std::vector<VerificationMethod> RecommendAuthMethods(const SecurityContext& context);
    bool RequiresStepUpAuth(const AccessRequest& request);
    bool ValidateMultiFactorAuth(const std::string& userId, 
                               const std::vector<std::string>& authTokens);
    
    // Threat Intelligence
    void ReportSecurityEvent(const SecurityEvent& event);
    std::vector<SecurityEvent> GetRecentEvents(const std::string& userId, 
                                             std::chrono::hours lookback);
    bool IsIPAddressBlacklisted(const std::string& ipAddress);
    void UpdateThreatIntelligence(const std::vector<std::string>& threatIndicators);
    
    // Session Management
    std::string CreateSecureSession(const std::string& userId, 
                                  const SecurityContext& context);
    bool ValidateSession(const std::string& sessionId);
    bool TerminateSession(const std::string& sessionId);
    void RefreshSessionSecurity(const std::string& sessionId, 
                              const SecurityContext& newContext);
    
    // Policy Management
    bool SetSecurityPolicy(const std::string& policyId, 
                         const std::unordered_map<std::string, std::string>& policy);
    std::unordered_map<std::string, std::string> GetSecurityPolicy(const std::string& policyId);
    bool EvaluatePolicy(const std::string& policyId, const AccessRequest& request);
    
    // Quantum-Safe Cryptography
    bool InitializeQuantumSafeCrypto();
    std::string EncryptWithQuantumSafeAlgorithm(const std::string& data, 
                                               const std::string& keyId);
    std::string DecryptWithQuantumSafeAlgorithm(const std::string& encryptedData, 
                                               const std::string& keyId);
    std::string GenerateQuantumSafeKeyPair();
    
    // Event Callbacks
    void SetThreatDetectionCallback(std::function<void(const SecurityEvent&)> callback);
    void SetAccessDeniedCallback(std::function<void(const AccessRequest&, const std::string&)> callback);
    void SetAuthenticationCallback(std::function<bool(const std::string&, VerificationMethod)> callback);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
};

/**
 * @brief Advanced Threat Detection Engine
 * 
 * Uses machine learning and behavioral analysis to detect sophisticated
 * attacks including social engineering, advanced persistent threats, and AI-powered attacks.
 */
class ThreatDetectionEngine {
public:
    enum class AttackType {
        UNKNOWN,
        PHISHING,
        SOCIAL_ENGINEERING,
        MALWARE,
        RANSOMWARE,
        DATA_EXFILTRATION,
        ACCOUNT_TAKEOVER,
        INSIDER_THREAT,
        APT,
        AI_GENERATED_ATTACK,
        DEEPFAKE_ATTACK,
        BUSINESS_EMAIL_COMPROMISE
    };

    struct ThreatSignature {
        std::string signatureId;
        AttackType attackType;
        std::string description;
        std::vector<std::string> indicators;
        double confidence;
        std::chrono::system_clock::time_point lastUpdated;
    };

    struct ThreatDetection {
        std::string detectionId;
        AttackType attackType;
        std::string emailId;
        std::string description;
        double confidence;
        std::vector<std::string> evidenceItems;
        ZeroTrustFramework::ThreatLevel severity;
        std::chrono::system_clock::time_point timestamp;
        std::unordered_map<std::string, std::string> metadata;
    };

public:
    ThreatDetectionEngine();
    virtual ~ThreatDetectionEngine();

    bool Initialize(const std::string& modelPath);
    
    // Email Threat Analysis
    std::vector<ThreatDetection> AnalyzeEmailForThreats(const std::string& emailContent,
                                                       const std::string& senderInfo);
    bool IsPhishingAttempt(const std::string& emailContent);
    bool IsSocialEngineeringAttack(const std::string& emailContent);
    bool IsBusinessEmailCompromise(const std::string& emailContent, 
                                 const std::string& senderProfile);
    
    // Advanced Detection
    bool DetectDeepfakeContent(const std::vector<uint8_t>& attachment);
    bool DetectAIGeneratedContent(const std::string& content);
    double CalculateEmailAuthenticityScore(const std::string& emailContent,
                                         const std::string& senderHistory);
    
    // Behavioral Threat Detection
    bool DetectInsiderThreat(const std::string& userId, 
                           const std::vector<std::string>& recentActions);
    bool DetectAccountTakeoverAttempt(const std::string& userId,
                                    const ZeroTrustFramework::SecurityContext& context);
    
    // Threat Intelligence
    void UpdateThreatSignatures(const std::vector<ThreatSignature>& signatures);
    std::vector<ThreatSignature> GetThreatSignatures(AttackType attackType);
    void ReportFalsePositive(const std::string& detectionId);
    void ReportTruePositive(const std::string& detectionId);
    
    // Machine Learning
    void TrainOnNewThreats(const std::vector<std::string>& threatExamples,
                         const std::vector<AttackType>& labels);
    bool UpdateMLModel(const std::string& modelPath);
    double GetModelAccuracy();

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
};

/**
 * @brief Quantum-Safe Cryptography Manager
 * 
 * Implements post-quantum cryptographic algorithms to protect against
 * future quantum computer attacks.
 */
class QuantumSafeCrypto {
public:
    enum class Algorithm {
        CRYSTALS_KYBER,      // Key encapsulation
        CRYSTALS_DILITHIUM,  // Digital signatures
        FALCON,              // Digital signatures
        SPHINCS_PLUS,        // Digital signatures
        CLASSIC_MCELIECE,    // Key encapsulation
        BIKE,                // Key encapsulation
        HQC,                 // Key encapsulation
        PICNIC,              // Digital signatures
        RAINBOW,             // Digital signatures
    };

    struct KeyPair {
        std::string keyId;
        Algorithm algorithm;
        std::vector<uint8_t> publicKey;
        std::vector<uint8_t> privateKey;
        std::chrono::system_clock::time_point createdAt;
        std::chrono::system_clock::time_point expiresAt;
    };

    struct EncryptionResult {
        std::vector<uint8_t> ciphertext;
        std::vector<uint8_t> encapsulatedKey;
        std::string keyId;
        Algorithm algorithm;
    };

public:
    QuantumSafeCrypto();
    virtual ~QuantumSafeCrypto();

    bool Initialize();
    
    // Key Management
    std::string GenerateKeyPair(Algorithm algorithm);
    KeyPair GetKeyPair(const std::string& keyId);
    bool RevokeKeyPair(const std::string& keyId);
    std::vector<std::string> ListActiveKeys();
    
    // Encryption/Decryption
    EncryptionResult Encrypt(const std::vector<uint8_t>& plaintext, 
                           const std::string& recipientKeyId);
    std::vector<uint8_t> Decrypt(const EncryptionResult& encrypted, 
                               const std::string& privateKeyId);
    
    // Digital Signatures
    std::vector<uint8_t> Sign(const std::vector<uint8_t>& message, 
                            const std::string& privateKeyId);
    bool Verify(const std::vector<uint8_t>& message, 
              const std::vector<uint8_t>& signature, 
              const std::string& publicKeyId);
    
    // Key Exchange
    std::vector<uint8_t> InitiateKeyExchange(const std::string& remotePublicKeyId);
    std::vector<uint8_t> CompleteKeyExchange(const std::vector<uint8_t>& initiatorData, 
                                           const std::string& localPrivateKeyId);
    
    // Hybrid Mode (Classical + Post-Quantum)
    bool EnableHybridMode(bool enable);
    EncryptionResult HybridEncrypt(const std::vector<uint8_t>& plaintext, 
                                 const std::string& classicalKeyId, 
                                 const std::string& quantumSafeKeyId);
    
    // Migration Support
    bool MigrateFromClassicalCrypto(const std::string& classicalKeyId, 
                                  Algorithm targetAlgorithm);
    std::vector<std::string> GetMigrationPlan();

private:
    class Impl;
    std::unique_ptr<Impl> pImpl_;
};

} // namespace Security
} // namespace HM