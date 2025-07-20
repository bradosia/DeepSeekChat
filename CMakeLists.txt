cmake_minimum_required(VERSION 3.16)

project(BrightMindsDiscussion VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Qt6 components
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)

# Set up Qt6
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Source files
set(SOURCES
    src/main.cpp
    src/MainWindow.cpp
)

set(HEADERS
    src/MainWindow.h
)

set(UI_FILES
    src/MainWindow.ui
)

# Create executable
add_executable(BrightMindsDiscussion ${SOURCES} ${HEADERS} ${UI_FILES})

# Link Qt6 libraries
target_link_libraries(BrightMindsDiscussion Qt6::Core Qt6::Widgets)

# Copy Python script to build directory
configure_file(${CMAKE_SOURCE_DIR}/src/python_interface.py ${CMAKE_BINARY_DIR}/python_interface.py COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/speakers.json ${CMAKE_BINARY_DIR}/speakers.json COPYONLY)

# Set output directory
set_target_properties(BrightMindsDiscussion PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Platform-specific settings
if(WIN32)
    set_target_properties(BrightMindsDiscussion PROPERTIES
        WIN32_EXECUTABLE TRUE
    )
endif()

# Installation
install(TARGETS BrightMindsDiscussion
    RUNTIME DESTINATION bin
)
install(FILES src/python_interface.py speakers.json
    DESTINATION bin
)
