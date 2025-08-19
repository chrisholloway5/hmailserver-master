#include "MCPClient.h"
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <fstream>
#include <curl/curl.h>
#include <spdlog/spdlog.h>

namespace HM {
namespace AI {

class MCPClient::Impl {
public:
    Impl() : initialized_(false), nextRequestId_(1) {
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }

    ~Impl() {
        curl_global_cleanup();
    }

    bool Initialize(const std::string& configPath) {
        try {
            if (!LoadConfiguration(configPath)) {
                spdlog::error("Failed to load MCP configuration from: {}", configPath);
                return false;
            }

            // Initialize HTTP client
            curl_ = curl_easy_init();
            if (!curl_) {
                spdlog::error("Failed to initialize CURL");
                return false;
            }

            // Setup default models
            SetupDefaultModels();

            initialized_ = true;
            spdlog::info("MCP Client initialized successfully");
            return true;
        }
        catch (const std::exception& e) {
            spdlog::error("MCP Client initialization failed: {}", e.what());
            return false;
        }
    }

    bool RegisterModel(const ModelInfo& modelInfo) {
        std::lock_guard<std::mutex> lock(modelsMutex_);
        
        if (models_.find(modelInfo.id) != models_.end()) {
            spdlog::warn("Model {} already registered, updating...", modelInfo.id);
        }

        models_[modelInfo.id] = modelInfo;
        modelStats_[modelInfo.id] = ModelStats{
            modelInfo.id, 0, 0, 0.0, 0.0, 
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count()
        };

        spdlog::info("Registered model: {} ({})", modelInfo.name, modelInfo.id);
        return true;
    }

    AIResponse ProcessRequest(const AIRequest& request) {
        auto startTime = std::chrono::high_resolution_clock::now();
        
        AIResponse response;
        response.requestId = request.requestId.empty() ? 
            GenerateRequestId() : request.requestId;
        response.modelId = request.modelId;
        response.success = false;

        try {
            // Validate model exists
            std::lock_guard<std::mutex> lock(modelsMutex_);
            auto modelIt = models_.find(request.modelId);
            if (modelIt == models_.end()) {
                response.error = "Model not found: " + request.modelId;
                return response;
            }

            const ModelInfo& model = modelIt->second;

            // Prepare request payload
            nlohmann::json payload = {
                {"model", request.modelId},
                {"prompt", request.prompt},
                {"context", request.context},
                {"parameters", request.parameters}
            };

            // Send request based on model type
            std::string responseText;
            if (model.isLocal) {
                responseText = ProcessLocalModel(model, payload);
            } else {
                responseText = ProcessRemoteModel(model, payload);
            }

            // Parse response
            auto responseJson = nlohmann::json::parse(responseText);
            response.content = responseJson.value("content", "");
            response.confidence = responseJson.value("confidence", 0.0);
            response.metadata = responseJson.value("metadata", nlohmann::json::object());
            response.success = true;

            // Update statistics
            UpdateModelStats(request.modelId, true, 
                std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::high_resolution_clock::now() - startTime).count());

        }
        catch (const std::exception& e) {
            response.error = e.what();
            spdlog::error("Request processing failed: {}", e.what());
            
            UpdateModelStats(request.modelId, false, 
                std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::high_resolution_clock::now() - startTime).count());
        }

        response.processingTimeMs = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::high_resolution_clock::now() - startTime).count();

        return response;
    }

    AIResponse AnalyzeEmail(const std::string& emailContent, const std::string& context) {
        AIRequest request;
        request.requestId = GenerateRequestId();
        request.modelId = GetBestModelForCapability(ModelCapability::TEXT_ANALYSIS);
        request.prompt = BuildEmailAnalysisPrompt(emailContent, context);
        request.preserveContext = true;

        return ProcessRequest(request);
    }

    AIResponse ClassifyEmail(const std::string& emailContent) {
        AIRequest request;
        request.requestId = GenerateRequestId();
        request.modelId = GetBestModelForCapability(ModelCapability::EMAIL_CLASSIFICATION);
        request.prompt = BuildEmailClassificationPrompt(emailContent);

        return ProcessRequest(request);
    }

    AIResponse DetectSpam(const std::string& emailContent) {
        AIRequest request;
        request.requestId = GenerateRequestId();
        request.modelId = GetBestModelForCapability(ModelCapability::SPAM_DETECTION);
        request.prompt = BuildSpamDetectionPrompt(emailContent);

        return ProcessRequest(request);
    }

    bool CreateContext(const std::string& contextId, const std::string& userId) {
        std::lock_guard<std::mutex> lock(contextMutex_);
        
        if (contexts_.find(contextId) != contexts_.end()) {
            spdlog::warn("Context {} already exists", contextId);
            return false;
        }

        ContextFrame frame;
        frame.frameId = contextId;
        frame.userId = userId;
        frame.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        frame.context = nlohmann::json::object();

        contexts_[contextId] = frame;
        spdlog::debug("Created context: {}", contextId);
        return true;
    }

    bool UpdateContext(const std::string& contextId, const nlohmann::json& context) {
        std::lock_guard<std::mutex> lock(contextMutex_);
        
        auto it = contexts_.find(contextId);
        if (it == contexts_.end()) {
            spdlog::warn("Context {} not found", contextId);
            return false;
        }

        it->second.context.merge_patch(context);
        it->second.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        if (contextUpdateCallback_) {
            contextUpdateCallback_(contextId);
        }

        return true;
    }

private:
    bool initialized_;
    std::atomic<uint64_t> nextRequestId_;
    CURL* curl_;

    std::mutex modelsMutex_;
    std::unordered_map<std::string, ModelInfo> models_;
    std::unordered_map<std::string, ModelStats> modelStats_;

    std::mutex contextMutex_;
    std::unordered_map<std::string, ContextFrame> contexts_;

    std::unordered_map<std::string, std::string> configuration_;

    // Callbacks
    std::function<void(const std::string&, bool)> connectionCallback_;
    std::function<void(const std::string&)> contextUpdateCallback_;
    std::function<void(const std::string&, const std::string&)> errorCallback_;

    std::string GenerateRequestId() {
        return "req_" + std::to_string(nextRequestId_++);
    }

    bool LoadConfiguration(const std::string& configPath) {
        try {
            std::ifstream file(configPath);
            if (!file.is_open()) {
                return false;
            }

            nlohmann::json config;
            file >> config;

            for (auto& [key, value] : config.items()) {
                if (value.is_string()) {
                    configuration_[key] = value.get<std::string>();
                }
            }

            return true;
        }
        catch (const std::exception& e) {
            spdlog::error("Configuration loading failed: {}", e.what());
            return false;
        }
    }

    void SetupDefaultModels() {
        // Setup default local models
        ModelInfo localModel;
        localModel.id = "hmailserver-local-classifier";
        localModel.name = "Local Email Classifier";
        localModel.provider = "hMailServer";
        localModel.version = "1.0.0";
        localModel.capabilities = {"EMAIL_CLASSIFICATION", "SPAM_DETECTION"};
        localModel.isLocal = true;
        localModel.endpoint = "local://classifier";

        RegisterModel(localModel);

        // Setup cloud model connections (if configured)
        if (configuration_.find("openai_api_key") != configuration_.end()) {
            ModelInfo gptModel;
            gptModel.id = "gpt-4";
            gptModel.name = "GPT-4";
            gptModel.provider = "OpenAI";
            gptModel.version = "4.0";
            gptModel.capabilities = {"TEXT_GENERATION", "TEXT_ANALYSIS", "SUMMARIZATION"};
            gptModel.isLocal = false;
            gptModel.endpoint = "https://api.openai.com/v1/chat/completions";

            RegisterModel(gptModel);
        }
    }

    std::string GetBestModelForCapability(ModelCapability capability) {
        std::lock_guard<std::mutex> lock(modelsMutex_);
        
        std::string capabilityStr = CapabilityToString(capability);
        
        for (const auto& [modelId, model] : models_) {
            for (const auto& cap : model.capabilities) {
                if (cap == capabilityStr) {
                    return modelId;
                }
            }
        }

        // Fallback to first available model
        if (!models_.empty()) {
            return models_.begin()->first;
        }

        return "";
    }

    std::string CapabilityToString(ModelCapability capability) {
        switch (capability) {
            case ModelCapability::TEXT_GENERATION: return "TEXT_GENERATION";
            case ModelCapability::TEXT_ANALYSIS: return "TEXT_ANALYSIS";
            case ModelCapability::SENTIMENT_ANALYSIS: return "SENTIMENT_ANALYSIS";
            case ModelCapability::LANGUAGE_DETECTION: return "LANGUAGE_DETECTION";
            case ModelCapability::TRANSLATION: return "TRANSLATION";
            case ModelCapability::SUMMARIZATION: return "SUMMARIZATION";
            case ModelCapability::INTENT_RECOGNITION: return "INTENT_RECOGNITION";
            case ModelCapability::SPAM_DETECTION: return "SPAM_DETECTION";
            case ModelCapability::SECURITY_ANALYSIS: return "SECURITY_ANALYSIS";
            case ModelCapability::EMAIL_CLASSIFICATION: return "EMAIL_CLASSIFICATION";
            case ModelCapability::RESPONSE_GENERATION: return "RESPONSE_GENERATION";
            default: return "UNKNOWN";
        }
    }

    std::string BuildEmailAnalysisPrompt(const std::string& emailContent, const std::string& context) {
        return "Analyze the following email for sentiment, intent, and key information:\n\n" +
               "Context: " + context + "\n\n" +
               "Email Content:\n" + emailContent + "\n\n" +
               "Provide analysis in JSON format with fields: sentiment, intent, keywords, priority, summary.";
    }

    std::string BuildEmailClassificationPrompt(const std::string& emailContent) {
        return "Classify the following email into categories (personal, business, marketing, notification, etc.):\n\n" +
               emailContent + "\n\n" +
               "Return classification in JSON format.";
    }

    std::string BuildSpamDetectionPrompt(const std::string& emailContent) {
        return "Analyze this email for spam indicators and provide a spam probability score:\n\n" +
               emailContent + "\n\n" +
               "Return result in JSON format with spam_probability (0-1) and reasons.";
    }

    std::string ProcessLocalModel(const ModelInfo& model, const nlohmann::json& payload) {
        // Simulate local model processing for now
        // In real implementation, this would call local ML inference
        nlohmann::json response = {
            {"content", "Local model response simulated"},
            {"confidence", 0.85},
            {"metadata", {{"model", model.id}, {"local", true}}}
        };
        return response.dump();
    }

    std::string ProcessRemoteModel(const ModelInfo& model, const nlohmann::json& payload) {
        // HTTP request to remote model API
        std::string response;
        
        // Setup CURL request
        curl_easy_setopt(curl_, CURLOPT_URL, model.endpoint.c_str());
        curl_easy_setopt(curl_, CURLOPT_POSTFIELDS, payload.dump().c_str());
        curl_easy_setopt(curl_, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl_, CURLOPT_WRITEDATA, &response);

        // Set headers
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        
        if (configuration_.find("openai_api_key") != configuration_.end()) {
            std::string authHeader = "Authorization: Bearer " + configuration_["openai_api_key"];
            headers = curl_slist_append(headers, authHeader.c_str());
        }
        
        curl_easy_setopt(curl_, CURLOPT_HTTPHEADER, headers);

        // Perform request
        CURLcode res = curl_easy_perform(curl_);
        curl_slist_free_all(headers);

        if (res != CURLE_OK) {
            throw std::runtime_error("CURL request failed: " + std::string(curl_easy_strerror(res)));
        }

        return response;
    }

    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
        userp->append((char*)contents, size * nmemb);
        return size * nmemb;
    }

    void UpdateModelStats(const std::string& modelId, bool success, int64_t responseTime) {
        std::lock_guard<std::mutex> lock(modelsMutex_);
        
        auto it = modelStats_.find(modelId);
        if (it != modelStats_.end()) {
            it->second.totalRequests++;
            if (success) {
                it->second.successfulRequests++;
            }
            
            // Update running averages
            it->second.averageResponseTime = 
                (it->second.averageResponseTime + responseTime) / 2.0;
            
            it->second.lastUsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
        }
    }
};

// MCPClient Implementation
MCPClient::MCPClient() : pImpl_(std::make_unique<Impl>()) {}
MCPClient::~MCPClient() = default;

bool MCPClient::Initialize(const std::string& configPath) {
    return pImpl_->Initialize(configPath);
}

bool MCPClient::RegisterModel(const ModelInfo& modelInfo) {
    return pImpl_->RegisterModel(modelInfo);
}

AIResponse MCPClient::ProcessRequest(const AIRequest& request) {
    return pImpl_->ProcessRequest(request);
}

AIResponse MCPClient::AnalyzeEmail(const std::string& emailContent, const std::string& context) {
    return pImpl_->AnalyzeEmail(emailContent, context);
}

AIResponse MCPClient::ClassifyEmail(const std::string& emailContent) {
    return pImpl_->ClassifyEmail(emailContent);
}

AIResponse MCPClient::DetectSpam(const std::string& emailContent) {
    return pImpl_->DetectSpam(emailContent);
}

bool MCPClient::CreateContext(const std::string& contextId, const std::string& userId) {
    return pImpl_->CreateContext(contextId, userId);
}

bool MCPClient::UpdateContext(const std::string& contextId, const nlohmann::json& context) {
    return pImpl_->UpdateContext(contextId, context);
}

} // namespace AI
} // namespace HM