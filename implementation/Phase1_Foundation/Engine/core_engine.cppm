// hMailServer Next-Generation Core Engine
// Modern C++26 Architecture with AI Integration
// Copyright (c) 2025 hMailServer Development Team

module;

#include <memory>
#include <string>
#include <vector>
#include <unordered_map>
#include <atomic>
#include <coroutine>
#include <expected>
#include <chrono>

export module hmailserver.core.engine;

import std;
import std.compat;

namespace hmailserver::core {

export enum class ComponentStatus {
    Stopped,
    Starting, 
    Running,
    Stopping,
    Error,
    Upgrading
};

export enum class SecurityLevel {
    Basic,
    Enhanced,
    Enterprise,
    Military,
    Quantum
};

export class CoreEngine {
public:
    CoreEngine();
    ~CoreEngine() = default;

    // Modern C++26 coroutine-based lifecycle
    std::coroutine<void> initialize_async();
    std::coroutine<void> shutdown_async();
    
    // Component management
    std::expected<void, std::error_code> register_component(
        std::string_view name, 
        std::unique_ptr<class IComponent> component
    );
    
    std::expected<ComponentStatus, std::error_code> get_component_status(
        std::string_view name
    ) const noexcept;
    
    // Configuration management with modern C++
    template<typename T>
    std::expected<T, std::error_code> get_config(std::string_view key) const;
    
    template<typename T>
    std::expected<void, std::error_code> set_config(std::string_view key, T&& value);
    
    // Performance monitoring
    struct PerformanceMetrics {
        std::chrono::nanoseconds average_response_time{0};
        std::atomic<uint64_t> total_requests{0};
        std::atomic<uint64_t> successful_requests{0};
        std::atomic<uint64_t> failed_requests{0};
        std::atomic<double> cpu_usage{0.0};
        std::atomic<uint64_t> memory_usage{0};
    };
    
    [[nodiscard]] const PerformanceMetrics& get_metrics() const noexcept {
        return metrics_;
    }
    
    // Security integration
    std::expected<void, std::error_code> set_security_level(SecurityLevel level);
    [[nodiscard]] SecurityLevel get_security_level() const noexcept {
        return security_level_;
    }
    
    // AI/ML integration point
    std::expected<void, std::error_code> enable_ai_features(bool enable = true);
    [[nodiscard]] bool ai_enabled() const noexcept {
        return ai_enabled_;
    }
    
    // Event system for modern reactive programming
    template<typename EventType>
    void publish_event(EventType&& event);
    
    template<typename EventType, typename Handler>
    void subscribe_event(Handler&& handler);

private:
    // Core state management
    std::atomic<ComponentStatus> status_{ComponentStatus::Stopped};
    SecurityLevel security_level_{SecurityLevel::Enhanced};
    std::atomic<bool> ai_enabled_{false};
    
    // Component registry
    std::unordered_map<std::string, std::unique_ptr<class IComponent>> components_;
    mutable std::shared_mutex components_mutex_;
    
    // Configuration storage
    std::unordered_map<std::string, std::any> configuration_;
    mutable std::shared_mutex config_mutex_;
    
    // Performance monitoring
    mutable PerformanceMetrics metrics_;
    std::chrono::steady_clock::time_point start_time_;
    
    // Event system
    class EventBus;
    std::unique_ptr<EventBus> event_bus_;
    
    // Internal methods
    void initialize_security();
    void initialize_monitoring();
    void initialize_ai_subsystem();
    std::expected<void, std::error_code> validate_configuration();
};

// Component interface for modern polymorphism
export class IComponent {
public:
    virtual ~IComponent() = default;
    
    virtual std::coroutine<void> start_async() = 0;
    virtual std::coroutine<void> stop_async() = 0;
    
    virtual ComponentStatus get_status() const noexcept = 0;
    virtual std::string_view get_name() const noexcept = 0;
    virtual std::string get_version() const = 0;
    
    // Health check for monitoring
    virtual std::expected<bool, std::error_code> health_check() const = 0;
    
    // Configuration update notification
    virtual void on_configuration_changed(std::string_view key, const std::any& value) {}
};

// Modern factory pattern with concepts
export template<typename T>
concept ComponentType = std::derived_from<T, IComponent>;

export template<ComponentType T, typename... Args>
std::unique_ptr<T> create_component(Args&&... args) {
    return std::make_unique<T>(std::forward<Args>(args)...);
}

// Performance monitoring utilities
export class PerformanceProfiler {
public:
    class ScopedTimer {
    public:
        explicit ScopedTimer(PerformanceProfiler& profiler, std::string_view operation)
            : profiler_(profiler), operation_(operation), start_(std::chrono::high_resolution_clock::now()) {}
        
        ~ScopedTimer() {
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start_);
            profiler_.record_operation(operation_, duration);
        }
        
    private:
        PerformanceProfiler& profiler_;
        std::string operation_;
        std::chrono::high_resolution_clock::time_point start_;
    };
    
    void record_operation(std::string_view operation, std::chrono::nanoseconds duration);
    
    struct OperationStats {
        std::chrono::nanoseconds total_time{0};
        std::chrono::nanoseconds average_time{0};
        std::chrono::nanoseconds min_time{std::chrono::nanoseconds::max()};
        std::chrono::nanoseconds max_time{0};
        uint64_t call_count{0};
    };
    
    [[nodiscard]] std::expected<OperationStats, std::error_code> 
    get_operation_stats(std::string_view operation) const;
    
    [[nodiscard]] auto create_timer(std::string_view operation) {
        return ScopedTimer(*this, operation);
    }

private:
    std::unordered_map<std::string, OperationStats> operation_stats_;
    mutable std::shared_mutex stats_mutex_;
};

// Configuration management with type safety
export class ConfigurationManager {
public:
    template<typename T>
    std::expected<void, std::error_code> set(std::string_view key, T&& value) {
        std::unique_lock lock(config_mutex_);
        
        try {
            config_data_[std::string{key}] = std::forward<T>(value);
            notify_change(key, config_data_[std::string{key}]);
            return {};
        } catch (const std::exception&) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }
    }
    
    template<typename T>
    std::expected<T, std::error_code> get(std::string_view key) const {
        std::shared_lock lock(config_mutex_);
        
        auto it = config_data_.find(std::string{key});
        if (it == config_data_.end()) {
            return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
        }
        
        try {
            return std::any_cast<T>(it->second);
        } catch (const std::bad_any_cast&) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }
    }
    
    bool exists(std::string_view key) const noexcept {
        std::shared_lock lock(config_mutex_);
        return config_data_.contains(std::string{key});
    }
    
    void subscribe_changes(std::function<void(std::string_view, const std::any&)> callback) {
        std::unique_lock lock(subscribers_mutex_);
        change_subscribers_.push_back(std::move(callback));
    }

private:
    std::unordered_map<std::string, std::any> config_data_;
    mutable std::shared_mutex config_mutex_;
    
    std::vector<std::function<void(std::string_view, const std::any&)>> change_subscribers_;
    mutable std::shared_mutex subscribers_mutex_;
    
    void notify_change(std::string_view key, const std::any& value) {
        std::shared_lock lock(subscribers_mutex_);
        for (const auto& subscriber : change_subscribers_) {
            subscriber(key, value);
        }
    }
};

// Global engine instance management
export CoreEngine& get_core_engine();
export std::expected<void, std::error_code> initialize_hmailserver_engine();
export void shutdown_hmailserver_engine() noexcept;

} // namespace hmailserver::core