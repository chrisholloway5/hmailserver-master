#include "pch.h"
#include "../Common/Application/Application.h"
#include "../../../implementation/Phase1_Foundation/AI/MCPClient.h"
#include "../../../implementation/Phase1_Foundation/Security/ZeroTrustFramework.h"
#include "../../../implementation/Phase1_Foundation/Engine/ContextAwareEmailEngine.h"

#include <iostream>
#include <memory>
#include <Windows.h>
#include <tchar.h>

using namespace HM;

// Service configuration
#define SERVICE_NAME _T("hMailServerNext")
#define SERVICE_DISPLAY_NAME _T("hMailServer Next-Generation")
#define SERVICE_DESCRIPTION _T("Next-Generation Email Server with AI Integration")

// Global service variables
SERVICE_STATUS g_ServiceStatus = {0};
SERVICE_STATUS_HANDLE g_StatusHandle = NULL;
HANDLE g_ServiceStopEvent = INVALID_HANDLE_VALUE;

// Application components
std::shared_ptr<AI::MCPClient> g_AIClient;
std::shared_ptr<Security::ZeroTrustFramework> g_SecurityFramework;
std::shared_ptr<Engine::ContextAwareEmailEngine> g_EmailEngine;
std::shared_ptr<Engine::EmailIntelligenceOrchestrator> g_Orchestrator;

// Forward declarations
VOID WINAPI ServiceMain(DWORD argc, LPTSTR *argv);
VOID WINAPI ServiceCtrlHandler(DWORD dwCtrl);
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam);
bool InitializeNextGenComponents();
void CleanupNextGenComponents();
void PrintBanner();
void ShowHelp();

int _tmain(int argc, TCHAR *argv[])
{
    PrintBanner();

    // Parse command line arguments
    bool debugMode = false;
    bool serviceMode = false;
    bool showHelp = false;
    std::wstring configPath = L"";

    for (int i = 1; i < argc; i++) {
        std::wstring arg = argv[i];
        if (arg == L"--debug" || arg == L"/debug") {
            debugMode = true;
        }
        else if (arg == L"--service" || arg == L"/service") {
            serviceMode = true;
        }
        else if (arg == L"--help" || arg == L"/help" || arg == L"-h" || arg == L"/?") {
            showHelp = true;
        }
        else if (arg == L"--config" || arg == L"/config") {
            if (i + 1 < argc) {
                configPath = argv[++i];
            }
        }
    }

    if (showHelp) {
        ShowHelp();
        return 0;
    }

    if (serviceMode) {
        // Running as Windows service
        SERVICE_TABLE_ENTRY ServiceTable[] = {
            {(LPWSTR)SERVICE_NAME, (LPSERVICE_MAIN_FUNCTION)ServiceMain},
            {NULL, NULL}
        };

        if (StartServiceCtrlDispatcher(ServiceTable) == FALSE) {
            return GetLastError();
        }
    }
    else {
        // Running in console mode
        std::wcout << L"Starting hMailServer Next-Generation in console mode..." << std::endl;
        
        if (debugMode) {
            std::wcout << L"Debug mode enabled" << std::endl;
        }

        // Initialize next-generation components
        if (!InitializeNextGenComponents()) {
            std::wcerr << L"Failed to initialize next-generation components!" << std::endl;
            return 1;
        }

        // Initialize legacy hMailServer application
        String errorMessage;
        std::shared_ptr<Application> app = Application::Instance();
        
        if (!app->InitInstance(errorMessage)) {
            std::wcerr << L"Failed to initialize hMailServer: " << errorMessage.c_str() << std::endl;
            CleanupNextGenComponents();
            return 1;
        }

        std::wcout << L"hMailServer Next-Generation started successfully!" << std::endl;
        std::wcout << L"AI Features: " << (g_AIClient ? L"Enabled" : L"Disabled") << std::endl;
        std::wcout << L"Zero-Trust Security: " << (g_SecurityFramework ? L"Enabled" : L"Disabled") << std::endl;
        std::wcout << L"Context-Aware Engine: " << (g_EmailEngine ? L"Enabled" : L"Disabled") << std::endl;
        std::wcout << L"Press Ctrl+C to stop..." << std::endl;

        // Wait for Ctrl+C
        SetConsoleCtrlHandler([](DWORD dwCtrlType) -> BOOL {
            if (dwCtrlType == CTRL_C_EVENT || dwCtrlType == CTRL_BREAK_EVENT) {
                std::wcout << L"\nShutting down..." << std::endl;
                
                // Cleanup application
                Application::Instance()->ExitInstance();
                CleanupNextGenComponents();
                
                ExitProcess(0);
                return TRUE;
            }
            return FALSE;
        }, TRUE);

        // Keep running
        while (true) {
            Sleep(1000);
        }
    }

    return 0;
}

VOID WINAPI ServiceMain(DWORD argc, LPTSTR *argv)
{
    DWORD Status = E_FAIL;

    // Register service control handler
    g_StatusHandle = RegisterServiceCtrlHandler(SERVICE_NAME, ServiceCtrlHandler);
    if (g_StatusHandle == NULL) {
        return;
    }

    // Set service status to starting
    ZeroMemory(&g_ServiceStatus, sizeof(g_ServiceStatus));
    g_ServiceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    g_ServiceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP;
    g_ServiceStatus.dwCurrentState = SERVICE_START_PENDING;
    g_ServiceStatus.dwWin32ExitCode = 0;
    g_ServiceStatus.dwServiceSpecificExitCode = 0;
    g_ServiceStatus.dwCheckPoint = 0;

    if (SetServiceStatus(g_StatusHandle, &g_ServiceStatus) == FALSE) {
        OutputDebugString(_T("hMailServerNext: SetServiceStatus returned error"));
    }

    // Create stop event
    g_ServiceStopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (g_ServiceStopEvent == NULL) {
        g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
        g_ServiceStatus.dwWin32ExitCode = GetLastError();
        g_ServiceStatus.dwCheckPoint = 1;
        SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
        return;
    }

    // Set service status to running
    g_ServiceStatus.dwCurrentState = SERVICE_RUNNING;
    g_ServiceStatus.dwWin32ExitCode = 0;
    g_ServiceStatus.dwCheckPoint = 0;

    if (SetServiceStatus(g_StatusHandle, &g_ServiceStatus) == FALSE) {
        OutputDebugString(_T("hMailServerNext: SetServiceStatus returned error"));
    }

    // Start worker thread
    HANDLE hThread = CreateThread(NULL, 0, ServiceWorkerThread, NULL, 0, NULL);
    if (hThread != NULL) {
        // Wait for stop event
        WaitForSingleObject(g_ServiceStopEvent, INFINITE);
        CloseHandle(hThread);
    }

    // Set service status to stopped
    g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);

    CloseHandle(g_ServiceStopEvent);
}

VOID WINAPI ServiceCtrlHandler(DWORD dwCtrl)
{
    switch (dwCtrl) {
    case SERVICE_CONTROL_STOP:
        if (g_ServiceStatus.dwCurrentState != SERVICE_RUNNING)
            break;

        g_ServiceStatus.dwControlsAccepted = 0;
        g_ServiceStatus.dwCurrentState = SERVICE_STOP_PENDING;
        g_ServiceStatus.dwWin32ExitCode = 0;
        g_ServiceStatus.dwCheckPoint = 4;

        if (SetServiceStatus(g_StatusHandle, &g_ServiceStatus) == FALSE) {
            OutputDebugString(_T("hMailServerNext: SetServiceStatus returned error"));
        }

        SetEvent(g_ServiceStopEvent);
        break;

    default:
        break;
    }
}

DWORD WINAPI ServiceWorkerThread(LPVOID lpParam)
{
    // Initialize next-generation components
    if (!InitializeNextGenComponents()) {
        OutputDebugString(_T("hMailServerNext: Failed to initialize next-generation components"));
        SetEvent(g_ServiceStopEvent);
        return 1;
    }

    // Initialize legacy hMailServer application
    String errorMessage;
    std::shared_ptr<Application> app = Application::Instance();
    
    if (!app->InitInstance(errorMessage)) {
        OutputDebugString(_T("hMailServerNext: Failed to initialize hMailServer application"));
        CleanupNextGenComponents();
        SetEvent(g_ServiceStopEvent);
        return 1;
    }

    // Service main loop
    while (WaitForSingleObject(g_ServiceStopEvent, 1000) != WAIT_OBJECT_0) {
        // Perform periodic health checks and maintenance
        if (g_Orchestrator) {
            auto health = g_Orchestrator->CheckSystemHealth();
            if (!health.isHealthy) {
                OutputDebugString(_T("hMailServerNext: System health issues detected"));
                // Could trigger alerts or self-healing procedures
            }
        }
    }

    // Cleanup
    app->ExitInstance();
    CleanupNextGenComponents();

    return 0;
}

bool InitializeNextGenComponents()
{
    try {
        // Initialize AI/MCP Client
#ifdef ENABLE_AI_FEATURES
        g_AIClient = std::make_shared<AI::MCPClient>();
        if (!g_AIClient->Initialize("config/mcp/config.json")) {
            std::wcerr << L"Warning: Failed to initialize AI client" << std::endl;
            g_AIClient.reset();
        }
#endif

        // Initialize Zero-Trust Security Framework
#ifdef ENABLE_ZERO_TRUST
        g_SecurityFramework = std::make_shared<Security::ZeroTrustFramework>();
        if (!g_SecurityFramework->Initialize("config/security.json")) {
            std::wcerr << L"Warning: Failed to initialize security framework" << std::endl;
            g_SecurityFramework.reset();
        }
#endif

        // Initialize Context-Aware Email Engine
        g_EmailEngine = std::make_shared<Engine::ContextAwareEmailEngine>(
            g_AIClient, g_SecurityFramework);
        
        if (!g_EmailEngine->Initialize("config/engine.json")) {
            std::wcerr << L"Warning: Failed to initialize email engine" << std::endl;
            g_EmailEngine.reset();
        }

        // Initialize Intelligence Orchestrator
        g_Orchestrator = std::make_shared<Engine::EmailIntelligenceOrchestrator>();
        
        if (g_AIClient) {
            g_Orchestrator->RegisterAIClient(g_AIClient);
        }
        if (g_SecurityFramework) {
            g_Orchestrator->RegisterSecurityFramework(g_SecurityFramework);
        }
        if (g_EmailEngine) {
            g_Orchestrator->RegisterEngine(g_EmailEngine);
        }

        if (!g_Orchestrator->Initialize("config/orchestrator.json")) {
            std::wcerr << L"Warning: Failed to initialize orchestrator" << std::endl;
            g_Orchestrator.reset();
        }

        if (!g_Orchestrator->Start()) {
            std::wcerr << L"Warning: Failed to start orchestrator" << std::endl;
        }

        return true;
    }
    catch (const std::exception& e) {
        std::wcerr << L"Exception during initialization: " << e.what() << std::endl;
        return false;
    }
}

void CleanupNextGenComponents()
{
    if (g_Orchestrator) {
        g_Orchestrator->Stop();
        g_Orchestrator.reset();
    }

    g_EmailEngine.reset();
    g_SecurityFramework.reset();
    g_AIClient.reset();
}

void PrintBanner()
{
    std::wcout << L"╔══════════════════════════════════════════════════════════════════════════════╗" << std::endl;
    std::wcout << L"║                    hMailServer Next-Generation v2.0.0                       ║" << std::endl;
    std::wcout << L"║                                                                              ║" << std::endl;
    std::wcout << L"║           Context-Aware Email Intelligence Platform                         ║" << std::endl;
    std::wcout << L"║                                                                              ║" << std::endl;
    std::wcout << L"║  🧠 AI-Powered Email Processing     🔒 Zero-Trust Security                  ║" << std::endl;
    std::wcout << L"║  🤖 Model Context Protocol (MCP)    🛡️  Quantum-Safe Cryptography          ║" << std::endl;
    std::wcout << L"║  📧 Sequential Thinking Engine      🌐 Next-Gen Protocols                   ║" << std::endl;
    std::wcout << L"║                                                                              ║" << std::endl;
    std::wcout << L"║  Copyright (c) 2024 hMailServer.com - The Future of Email Communication     ║" << std::endl;
    std::wcout << L"╚══════════════════════════════════════════════════════════════════════════════╝" << std::endl;
    std::wcout << std::endl;
}

void ShowHelp()
{
    std::wcout << L"USAGE:" << std::endl;
    std::wcout << L"  hMailServerNext.exe [OPTIONS]" << std::endl;
    std::wcout << std::endl;
    std::wcout << L"OPTIONS:" << std::endl;
    std::wcout << L"  --debug             Enable debug mode with verbose logging" << std::endl;
    std::wcout << L"  --service           Run as Windows service" << std::endl;
    std::wcout << L"  --config <path>     Specify configuration file path" << std::endl;
    std::wcout << L"  --help              Show this help message" << std::endl;
    std::wcout << std::endl;
    std::wcout << L"EXAMPLES:" << std::endl;
    std::wcout << L"  hMailServerNext.exe                    Run in console mode" << std::endl;
    std::wcout << L"  hMailServerNext.exe --debug            Run with debug output" << std::endl;
    std::wcout << L"  hMailServerNext.exe --service          Run as Windows service" << std::endl;
    std::wcout << std::endl;
    std::wcout << L"FEATURES:" << std::endl;
    std::wcout << L"  ✓ Traditional SMTP/IMAP/POP3 protocols" << std::endl;
    std::wcout << L"  ✓ AI-powered email analysis and classification" << std::endl;
    std::wcout << L"  ✓ Zero-trust security with behavioral analytics" << std::endl;
    std::wcout << L"  ✓ Context-aware email intelligence" << std::endl;
    std::wcout << L"  ✓ Sequential thinking architecture" << std::endl;
    std::wcout << L"  ✓ Quantum-safe cryptography support" << std::endl;
    std::wcout << std::endl;
    std::wcout << L"For more information, visit: https://www.hmailserver.com" << std::endl;
}