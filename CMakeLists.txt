cmake_minimum_required(VERSION 3.16)
project(hMailServerNext VERSION 2.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build configuration
option(BUILD_SHARED_LIBS "Build shared libraries" ON)
option(ENABLE_AI_FEATURES "Enable AI and MCP integration" ON)
option(ENABLE_QUANTUM_CRYPTO "Enable quantum-safe cryptography" ON)
option(ENABLE_ZERO_TRUST "Enable zero-trust security framework" ON)
option(BUILD_TESTS "Build unit tests" ON)

# Platform-specific settings
if(WIN32)
    set(CMAKE_SYSTEM_VERSION 10.0)
    add_definitions(-D_WIN32_WINNT=0x0A00)
endif()

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Threads REQUIRED)

# External dependencies
find_package(Boost 1.75.0 REQUIRED COMPONENTS
    system
    filesystem
    thread
    date_time
    regex
    serialization
)

find_package(OpenSSL 1.1.1 REQUIRED)

# Additional dependencies for AI features
if(ENABLE_AI_FEATURES)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(CURL REQUIRED libcurl)
    find_path(NLOHMANN_JSON_INCLUDE_DIR nlohmann/json.hpp)
    find_library(SPDLOG_LIBRARY spdlog)
endif()

# Quantum cryptography dependencies
if(ENABLE_QUANTUM_CRYPTO)
    find_library(OQS_LIBRARY oqs)
    find_path(OQS_INCLUDE_DIR oqs/oqs.h)
endif()

# Source directories
set(COMMON_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/hmailserver/source/Server/Common)
set(SERVER_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/hmailserver/source/Server/hMailServer)
set(FOUNDATION_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/implementation/Phase1_Foundation)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${COMMON_SOURCE_DIR}
    ${SERVER_SOURCE_DIR}
    ${FOUNDATION_SOURCE_DIR}
    ${Boost_INCLUDE_DIRS}
    ${OPENSSL_INCLUDE_DIR}
)

if(ENABLE_AI_FEATURES)
    include_directories(
        ${NLOHMANN_JSON_INCLUDE_DIR}
        ${CURL_INCLUDE_DIRS}
    )
endif()

if(ENABLE_QUANTUM_CRYPTO)
    include_directories(${OQS_INCLUDE_DIR})
endif()

# Compiler flags
if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4 /permissive-")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Od /Zi /RTC1")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
endif()

# Source files for existing hMailServer
file(GLOB_RECURSE HMAILSERVER_COMMON_SOURCES
    "${COMMON_SOURCE_DIR}/*.cpp"
    "${COMMON_SOURCE_DIR}/*.h"
)

file(GLOB_RECURSE HMAILSERVER_SERVER_SOURCES
    "${SERVER_SOURCE_DIR}/*.cpp"
    "${SERVER_SOURCE_DIR}/*.h"
)

# AI Integration sources
if(ENABLE_AI_FEATURES)
    file(GLOB_RECURSE AI_SOURCES
        "${FOUNDATION_SOURCE_DIR}/AI/*.cpp"
        "${FOUNDATION_SOURCE_DIR}/AI/*.h"
    )
endif()

# Security Framework sources
if(ENABLE_ZERO_TRUST)
    file(GLOB_RECURSE SECURITY_SOURCES
        "${FOUNDATION_SOURCE_DIR}/Security/*.cpp"
        "${FOUNDATION_SOURCE_DIR}/Security/*.h"
    )
endif()

# Engine sources
file(GLOB_RECURSE ENGINE_SOURCES
    "${FOUNDATION_SOURCE_DIR}/Engine/*.cpp"
    "${FOUNDATION_SOURCE_DIR}/Engine/*.h"
)

# Create the main hMailServer library
add_library(hMailServerCore
    ${HMAILSERVER_COMMON_SOURCES}
    ${HMAILSERVER_SERVER_SOURCES}
)

target_link_libraries(hMailServerCore
    ${Boost_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    Threads::Threads
)

if(WIN32)
    target_link_libraries(hMailServerCore
        ws2_32
        wsock32
        iphlpapi
        advapi32
        shell32
        ole32
        oleaut32
        uuid
    )
endif()

# Create the AI Integration library
if(ENABLE_AI_FEATURES)
    add_library(hMailServerAI ${AI_SOURCES})
    
    target_link_libraries(hMailServerAI
        hMailServerCore
        ${CURL_LIBRARIES}
        ${SPDLOG_LIBRARY}
    )
    
    target_compile_definitions(hMailServerAI PRIVATE ENABLE_AI_FEATURES)
endif()

# Create the Security Framework library
if(ENABLE_ZERO_TRUST)
    add_library(hMailServerSecurity ${SECURITY_SOURCES})
    
    target_link_libraries(hMailServerSecurity
        hMailServerCore
        ${OPENSSL_LIBRARIES}
    )
    
    if(ENABLE_QUANTUM_CRYPTO AND OQS_LIBRARY)
        target_link_libraries(hMailServerSecurity ${OQS_LIBRARY})
        target_compile_definitions(hMailServerSecurity PRIVATE ENABLE_QUANTUM_CRYPTO)
    endif()
    
    target_compile_definitions(hMailServerSecurity PRIVATE ENABLE_ZERO_TRUST)
endif()

# Create the Email Engine library
add_library(hMailServerEngine ${ENGINE_SOURCES})

target_link_libraries(hMailServerEngine
    hMailServerCore
)

if(ENABLE_AI_FEATURES)
    target_link_libraries(hMailServerEngine hMailServerAI)
endif()

if(ENABLE_ZERO_TRUST)
    target_link_libraries(hMailServerEngine hMailServerSecurity)
endif()

# Create the main executable
add_executable(hMailServerNext
    ${SERVER_SOURCE_DIR}/Main.cpp
)

target_link_libraries(hMailServerNext
    hMailServerCore
    hMailServerEngine
)

if(ENABLE_AI_FEATURES)
    target_link_libraries(hMailServerNext hMailServerAI)
endif()

if(ENABLE_ZERO_TRUST)
    target_link_libraries(hMailServerNext hMailServerSecurity)
endif()

# Configuration files
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/config/hMailServerNext.conf.in
    ${CMAKE_CURRENT_BINARY_DIR}/hMailServerNext.conf
    @ONLY
)

# Installation
install(TARGETS hMailServerNext
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/hMailServerNext.conf
    DESTINATION etc/hmailserver
)

# Create package configuration
if(BUILD_SHARED_LIBS)
    install(TARGETS hMailServerCore hMailServerEngine
        EXPORT hMailServerNextTargets
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
    )
    
    if(ENABLE_AI_FEATURES)
        install(TARGETS hMailServerAI
            EXPORT hMailServerNextTargets
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
        )
    endif()
    
    if(ENABLE_ZERO_TRUST)
        install(TARGETS hMailServerSecurity
            EXPORT hMailServerNextTargets
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
        )
    endif()
    
    # Install headers
    install(DIRECTORY ${FOUNDATION_SOURCE_DIR}/
        DESTINATION include/hmailserver
        FILES_MATCHING PATTERN "*.h"
    )
    
    # Generate and install package config
    include(CMakePackageConfigHelpers)
    
    write_basic_package_version_file(
        hMailServerNextConfigVersion.cmake
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY AnyNewerVersion
    )
    
    configure_package_config_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/cmake/hMailServerNextConfig.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/hMailServerNextConfig.cmake
        INSTALL_DESTINATION lib/cmake/hMailServerNext
    )
    
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/hMailServerNextConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/hMailServerNextConfigVersion.cmake
        DESTINATION lib/cmake/hMailServerNext
    )
    
    install(EXPORT hMailServerNextTargets
        FILE hMailServerNextTargets.cmake
        DESTINATION lib/cmake/hMailServerNext
    )
endif()

# Testing
if(BUILD_TESTS)
    enable_testing()
    find_package(GTest QUIET)
    
    if(GTest_FOUND)
        add_subdirectory(tests)
    else()
        message(WARNING "Google Test not found. Tests will not be built.")
    endif()
endif()

# Documentation
find_package(Doxygen QUIET)
if(Doxygen_FOUND)
    set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
    set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
    
    configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
    
    add_custom_target(doc_doxygen ALL
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
        VERBATIM
    )
endif()

# Packaging
set(CPACK_PACKAGE_NAME "hMailServerNext")
set(CPACK_PACKAGE_VENDOR "hMailServer.com")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Next-Generation Email Server with AI Integration")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_INSTALL_DIRECTORY "hMailServer Next")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")

if(WIN32)
    set(CPACK_GENERATOR "NSIS;ZIP")
    set(CPACK_NSIS_MODIFY_PATH ON)
    set(CPACK_NSIS_ENABLE_UNINSTALL_BEFORE_INSTALL ON)
else()
    set(CPACK_GENERATOR "TGZ;DEB;RPM")
    set(CPACK_DEBIAN_PACKAGE_MAINTAINER "hMailServer Team")
    set(CPACK_RPM_PACKAGE_GROUP "System Environment/Daemons")
endif()

include(CPack)

# Print configuration summary
message(STATUS "")
message(STATUS "hMailServer Next-Generation Configuration Summary:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  AI Features: ${ENABLE_AI_FEATURES}")
message(STATUS "  Zero-Trust Security: ${ENABLE_ZERO_TRUST}")
message(STATUS "  Quantum Cryptography: ${ENABLE_QUANTUM_CRYPTO}")
message(STATUS "  Build Tests: ${BUILD_TESTS}")
message(STATUS "  Shared Libraries: ${BUILD_SHARED_LIBS}")
message(STATUS "")